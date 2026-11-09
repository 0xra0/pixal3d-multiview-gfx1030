"""Optional Qwen-Image 2.1 prompt/CFG controls for Pixal3D pa.py.

Keeps pa.py's existing front/sheet CLI and default model sampling unchanged
unless optional prompt settings are supplied. Requires the node graph exported
in API format (TextEncodeQwenImage21 node 5, KSampler node 7).
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

_CONFIG = {}
_ALLOWED = {
    "negative_prompt", "front_negative", "sheet_negative", "sheet_consistency",
    "front_cfg", "sheet_cfg",
}
DEFAULT_NEGATIVE_CFG = 1.5  # Conservative starting point; tune per model/seed.


def configure_from_argv(argv):
    """Remove only our flags from sys.argv, leaving pa.py commands untouched."""
    parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    parser.add_argument("--prompt-config")
    parser.add_argument("--negative-prompt")
    parser.add_argument("--front-negative")
    parser.add_argument("--sheet-negative")
    parser.add_argument("--sheet-consistency")
    parser.add_argument("--front-cfg", type=float)
    parser.add_argument("--sheet-cfg", type=float)
    parsed, rest = parser.parse_known_args(argv[1:])

    config = {}
    if parsed.prompt_config:
        path = Path(parsed.prompt_config).expanduser()
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError(f"Prompt config must be a JSON object: {path}")
        unknown = set(data) - _ALLOWED
        if unknown:
            raise ValueError(f"Unknown prompt-config fields: {', '.join(sorted(unknown))}")
        config.update(data)

    # CLI wins over JSON; validate before mutating argv and global settings.
    for key in _ALLOWED:
        value = getattr(parsed, key, None)
        if value is not None:
            config[key] = value
    for key, value in config.items():
        if key.endswith("_cfg"):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"Prompt config '{key}' must be a number")
            if not math.isfinite(float(value)) or not 1.0 <= float(value) <= 10.0:
                raise ValueError(f"'{key}' must be between 1 and 10")
        elif not isinstance(value, str):
            raise ValueError(f"Prompt config '{key}' must be a string")

    argv[1:] = rest
    _CONFIG.clear()
    _CONFIG.update(config)
    if config:
        print("  optional Qwen prompt settings:", ", ".join(sorted(config)))
    return config


def apply_prompt_settings(workflow, stage, original_positive):
    """Patch prompt inputs and KSampler CFG for a specific Qwen stage.

    `TextEncodeQwenImage21`'s negative conditioning is ignored by ComfyUI
    at CFG=1. Change CFG only when a nonempty negative prompt is requested.
    A supplied --front-cfg/--sheet-cfg always wins over automatic guidance.
    """
    if stage not in ("front", "sheet"):
        raise ValueError(f"Unrecognized Qwen generation stage: {stage!r}")
    try:
        encoder = workflow["5"]
        sampler = workflow["7"]
        inputs = encoder["inputs"]
        sinputs = sampler["inputs"]
    except KeyError as exc:
        raise ValueError("Expected node 5 (encoder) and node 7 (KSampler)") from exc
    if encoder.get("class_type") != "TextEncodeQwenImage21" or sampler.get("class_type") != "KSampler":
        raise ValueError("Unexpected workflow node types at 5/7; review ComfyUI wiring before patching")
    if "prompt" not in inputs or "negative_prompt" not in inputs:
        raise ValueError("Qwen node 5 does not expose prompt and negative_prompt")
    if sinputs.get("positive") != ["5", 0] or sinputs.get("negative") != ["5", 1]:
        raise ValueError("KSampler node 7 not wired to Qwen node 5 positive/negative outputs")
    if "cfg" not in sinputs:
        raise ValueError("KSampler node 7 has no cfg input")

    positive = original_positive
    if stage == "sheet" and _CONFIG.get("sheet_consistency"):
        positive = (f"{original_positive.rstrip()}\n\n"
                    f"ADDITIONAL VIEW CONSISTENCY RULES:\n{_CONFIG['sheet_consistency']}")
    inputs["prompt"] = positive

    neg_key = f"{stage}_negative"
    negative = _CONFIG.get(neg_key, _CONFIG.get("negative_prompt"))
    if negative is not None:
        inputs["negative_prompt"] = negative

    cfg_key = f"{stage}_cfg"
    if cfg_key in _CONFIG:
        sinputs["cfg"] = float(_CONFIG[cfg_key])
    elif negative and negative.strip() and float(sinputs["cfg"]) <= 1:
        sinputs["cfg"] = DEFAULT_NEGATIVE_CFG
        print(f"  {stage}: negative prompt supplied -> enabling CFG={DEFAULT_NEGATIVE_CFG:g}")

    if inputs["negative_prompt"].strip() and float(sinputs["cfg"]) <= 1:
        print(f"  WARNING {stage}: CFG <= 1 means negative_prompt will have no effect")
    elif float(sinputs["cfg"]) > 1 and not inputs["negative_prompt"].strip():
        print(f"  NOTE {stage}: CFG > 1 but negative_prompt is empty")
    return workflow

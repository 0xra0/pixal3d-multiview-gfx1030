#!/usr/bin/env bash
# Prepare Qwen3.8-Flash-Next IQ2_XS for the existing (patched) HIP engine without running setup.py, which could
# rebuild the engine. Mirrors setup.py step 6-7 for family qwen on a ~48 GB PC (low-RAM resident mode):
# iq_pack.py -> pack, iq_pack.py --experts-bin -> experts.bin, then a config + start script beside the coder's.
set -euo pipefail
S=/mnt/ssd/Strata
G=/mnt/ssd/Strata-data/gguf/IQ2_XS
P=/mnt/ssd/Strata-data/packs/iq2_xs
SH1=$G/Qwen3.8-Flash-Next-GSQ-RCO-IQ2_XS-00001-of-00002.gguf
SH2=$G/Qwen3.8-Flash-Next-GSQ-RCO-IQ2_XS-00002-of-00002.gguf
PY=$S/.venv/bin/python
# aria2 saved the shards under CDN hash names: name them by their exact size (HF API) and check the LFS sha256.
name_shard() {  # size sha256 target
    [ -f "$3" ] && return 0
    local f; for f in "$G"/*; do
        case "$f" in *.aria2|*.log|*.txt|*.gguf) continue;; esac
        [ "$(stat -c %s "$f")" = "$1" ] && [ ! -f "$f.aria2" ] || continue
        echo "checking sha256 of $f"; [ "$(sha256sum "$f" | cut -d' ' -f1)" = "$2" ] || { echo "sha256 mismatch: $f"; exit 1; }
        mv "$f" "$3"; return 0
    done
    echo "incomplete download for $3"; exit 1
}
name_shard 39225954592 92cee27ae5bbadcd732416a0f7a7f0acc092399dbbe8f5a5efa707c2ec0a49d7 "$SH1"
name_shard 28800138432 316b46f3a2dbd68c900f43136ab9449f9dcc3725dfd8c794847c204bc161e113 "$SH2"
cd "$S"
[ -f "$P/native_experts.txt" ] && [ -f "$P/tokenizer/vocab.json" ] || $PY tools/iq_pack.py --gguf "$SH1" --out "$P"
[ -f "$P/experts.bin" ] || $PY tools/iq_pack.py --gguf "$SH1" --out "$P" --experts-bin
# Which shard holds the PLE table (setup.py reads it the same way).
PLE=$($PY -c "import sys; sys.path.insert(0, 'tools'); from gguf_reader import GGUFFile
print(next(s for s in sys.argv[1:] if any(t.name == 'per_layer_token_embd.weight' for t in GGUFFile(s).tensors)))" "$SH1" "$SH2")
$PY - "$P" "$SH1" "$PLE" <<'EOF'
import json, sys
pack, native, ple = sys.argv[1:]
cfg = json.load(open("/mnt/ssd/Strata/strata-coder-uncen-iq1_m.json"))
a = cfg["args"]
def put(flag, value):
    a[a.index(flag) + 1] = value
put("--pack", pack); put("--native", native); put("--ple-gguf", ple)
put("--expert-profile", "/mnt/ssd/Strata/data/expert-profile.bin")
put("--max-context", "65536")
cfg.update(tokenizer=f"{pack}/tokenizer", model_name="qwen3.8-flash-next-iq2_xs",
           log="/mnt/ssd/Strata/strata-iq2_xs.log")
cfg["vision"]["model"] = native   # opened vocab-only beside the shared mmproj (setup.py uses shard 1)
json.dump(cfg, open("/mnt/ssd/Strata/strata-iq2_xs.json", "w"), indent=2)
print("config:", " ".join(a))
EOF
cat > "$S/run-iq2_xs.sh" <<'EOF'
#!/bin/sh
exec /mnt/ssd/Strata/.venv/bin/python /mnt/ssd/Strata/serve/server.py --engine strata --config /mnt/ssd/Strata/strata-iq2_xs.json --port 8099
EOF
chmod +x "$S/run-iq2_xs.sh"
echo "ready: $S/run-iq2_xs.sh"

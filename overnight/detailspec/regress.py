import json, sys, copy
sys.path.insert(0, "/mnt/ssd/work/pixal3d-mv"); sys.path.insert(0, ".")
import pa_prompt_support as new, old_pps as old
K = "/mnt/ssd/work/pixal3d-mv/"
wfs = {n: json.load(open(K + "workflows/" + n)) for n in ("01_front.json", "02_sheet.json")}
fails = 0
for extra in ([], ["--prompt-config", K + "necklace_medallion_prompts.json"], ["--negative-prompt", "blurry", "--sheet-cfg", "3"]):
    for mod in (old, new):
        mod.configure_from_argv(["pa.py", "front", "x", *extra])
    for stage, n in (("front", "01_front.json"), ("sheet", "02_sheet.json")):
        a = old.apply_prompt_settings(copy.deepcopy(wfs[n]), stage, "POS")
        for view in (None, "back"):
            b = new.apply_prompt_settings(copy.deepcopy(wfs[n]), stage, "POS", view=view)
            same = a == b
            fails += not same
            print("same" if same else "DIFF", stage, view, extra[:1])
print("fingerprint without options:", new.prompt_fingerprint() if not new.configure_from_argv(["pa.py"]) else "?")
for bad in ('{"huge": "x"}', '{"small": 3}', '{"views": {"top": "x"}}', '{"large": [""]}', '[1]'):
    open("bad.json", "w").write(bad)
    try:
        new.configure_from_argv(["pa.py", "front", "x", "--detail-spec", "bad.json"]); print("ACCEPTED", bad); fails += 1
    except ValueError as e:
        print("rejected:", e)
sys.exit(fails)

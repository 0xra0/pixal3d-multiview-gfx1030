"""Refine pass for vampire_chestplate texture 00006: regenerate only the back medallion region.
Albedo sampler gets the first-pass views (back medallion painted out) as init_views, keep_mask = 0 only there.
The MR sampler reruns with the first pass's seed. Same LOD0 mesh, same UVs (keep_existing)."""
import os, sys
sys.path.insert(0, "/mnt/ssd/work/pixal3d-mv")
import pa

SEED, RES, DENOISE = 617113405, 1024, float(os.environ.get("DENOISE", ".65"))
name = "vampire_chestplate"
glb = "/mnt/ssd/ComfyUI/output/GameAssets/vampire_chestplate/meshes/vampire_chestplate_LOD0.glb"
p = pa.wf("04_texture.json")
p["1"]["inputs"]["image"] = f"{name}_views/front.png"
p["2"]["inputs"]["glb_path"] = glb
p["14"]["inputs"]["uv_mode"] = "keep_existing"
for nid in ("18", "20"):
    p[nid]["inputs"].update(resolution=RES, seed=SEED, attention="comfy_default")
views = ["view0.png", "view1.png", os.environ.get("BACK_EDIT", "view2_edit.png"), "view3.png", "view4.png", "view5.png"]
def batch(files, base):
    for i, f in enumerate(files):
        p[str(base + i)] = {"class_type": "LoadImage", "inputs": {"image": "chest_backfix/" + f}}
    last = str(base)
    for i in range(1, len(files)):
        node = str(base + 10 + i)
        p[node] = {"class_type": "ImageBatch", "inputs": {"image1": [last, 0], "image2": [str(base + i), 0]}}
        last = node
    return last
init = batch(views, 100)
keep = batch([f"keep{i}.png" for i in range(6)], 200)
p["300"] = {"class_type": "ImageToMask", "inputs": {"image": [keep, 0], "channel": "red"}}
p["18"]["inputs"].update(init_views=[init, 0], keep_mask=["300", 0], denoise=DENOISE)
p["23"]["inputs"]["filename_prefix"] = f"UltraTex/{name}_backfix"
p["30"]["inputs"]["filename_prefix"] = f"UltraTex/{name}_backfix_views"
p["31"]["inputs"]["filename_prefix"] = f"UltraTex/{name}_backfix_normals"
print("seed", SEED, "denoise", DENOISE, "mesh", glb, flush=True)
pa.run(p, "texture")

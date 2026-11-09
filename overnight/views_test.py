"""UltraTex view-sheet A/B: albedo sampler only (no MR pass, no bake), then score horizontal banding.

usage: views_test.py TAG SEED RES [key=value ...]   keys: align, attention, topk, steps, guidance, chunk
Writes ComfyUI/output/UltraTex/vt_<TAG>_views_*.png and appends a line to overnight/views_test.tsv.
"""
import glob
import os
import sys
import time

sys.path.insert(0, "/mnt/ssd/work/pixal3d-mv")
import pa  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image  # noqa: E402
from cmp_ref_front import band_score  # noqa: E402

MESH = "/mnt/ssd/work/overnight/a7/meshes/vampire_chestplate_LOD0.glb"   # tex4/tex5 mesh
REF = "vampire_chestplate_views/front.png"

tag, seed, res = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
opts = dict(a.split("=", 1) for a in sys.argv[4:])

p = pa.wf("04_texture.json")
for nid in ("11", "20", "23", "31"):        # metal/rough pass, bake, normal-view save
    del p[nid]
p["1"]["inputs"]["image"] = REF
p["2"]["inputs"]["glb_path"] = MESH
p["14"]["inputs"]["uv_mode"] = "keep_existing"
p["14"]["inputs"]["reference_alignment"] = opts.get("align", "fit_front_silhouette")
s = p["18"]["inputs"]
s.update(resolution=res, seed=seed, attention=opts.get("attention", "ultratex_sparse"),
         sparse_topk=float(opts.get("topk", 0.2)), steps=int(opts.get("steps", 25)),
         guidance=float(opts.get("guidance", 4.0)), token_chunk=int(opts.get("chunk", 8192)))
prefix = f"UltraTex/vt_{tag}_views"
p["30"]["inputs"]["filename_prefix"] = prefix

t0 = time.time()
pa.run(p, "texture")
wall = time.time() - t0
out = sorted(glob.glob(os.path.join(pa.COMFY, "output", prefix + "_*.png")), key=os.path.getmtime)[-1]

views = Image.open(out)
t = views.size[0] // 3
scores = [band_score(views.crop(((i % 3) * t, (i // 3) * t, (i % 3 + 1) * t, (i // 3 + 1) * t)))[0] for i in range(6)]
line = f"{tag}\t{seed}\t{res}\t{opts}\t{wall:.0f}s\tfront {scores[0]:.3f}\tback {scores[3]:.3f}\tsides {scores[1]:.3f} {scores[2]:.3f}\t{out}"
print(line)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "views_test.tsv"), "a") as f:
    f.write(line + "\n")

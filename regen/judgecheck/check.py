"""Controls for the mesh judge: does it pass a perfect match, fail a wrong one, and agree with itself?
  python check.py  -> results.jsonl (one line per judge call)"""
import json, os, shutil, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, "/mnt/ssd/work/pixal3d-mv")
import mesh_judge as mj
import trimesh

OUT = "/mnt/ssd/work/regen/judgecheck"
SRC = "/mnt/ssd/ComfyUI/output/3D"
VIEWS = "/mnt/ssd/ComfyUI/input/vampire_chestplate_v3_views"

def rgba_render(glb, view):
    """Clay render with an alpha mask, so it can stand in as a reference view."""
    m = trimesh.load(glb, force="mesh", process=False)
    v, f = np.asarray(m.vertices, float), np.asarray(m.faces)
    grey = mj.clay(v, f, view).convert("RGB")
    # mask: same projection as clay(), polygons in white on black
    toward = np.array(mj.EYE[view], float); right = np.cross(-toward, mj.UP); down = -mj.UP
    s = mj.TILE * 2
    u, w = v @ right, v @ down
    span = max(np.ptp(u), np.ptp(w)) or 1.0
    k = 0.9 * s / span
    u = (u - (u.min() + u.max()) / 2) * k + s / 2
    w = (w - (w.min() + w.max()) / 2) * k + s / 2
    mask = Image.new("L", (s, s), 0); d = ImageDraw.Draw(mask)
    for tri in np.stack([u, w], 1)[f].tolist():
        d.polygon([tuple(p) for p in tri], fill=255)
    out = grey.convert("RGBA"); out.putalpha(mask.resize((mj.TILE, mj.TILE), Image.LANCZOS))
    return out

def views_from(glb, name, swap_back=False):
    d = os.path.join(OUT, name); os.makedirs(d, exist_ok=True)
    for view in mj.VIEWS:
        rgba_render(glb, "front" if (swap_back and view == "back") else view).save(os.path.join(d, f"{view}.png"))
    return d

def copy(name, dst):
    p = os.path.join(OUT, dst); shutil.copy(os.path.join(SRC, name), p); return p

cuirass = copy("vampire_chestplate_v3_00004_.glb", "cuirass4.glb")
pendant = copy("medallion_pendant_v3_00004_.glb", "pendant4.glb")
cases = [("repeat-1", VIEWS, cuirass), ("repeat-2", VIEWS, cuirass), ("repeat-3", VIEWS, cuirass),
         ("self-match (expect pass)", views_from(cuirass, "self"), cuirass),
         ("back ref = front render (expect fail on back)", views_from(cuirass, "swap", True), cuirass),
         ("pendant vs cuirass refs (expect fail ~0)", VIEWS, pendant)]
with open(os.path.join(OUT, "results.jsonl"), "w") as log:
    for label, views, glb in cases:
        r = mj.judge(views, glb, ["agy"], "vampire chestplate v3")
        r["case"] = label
        log.write(json.dumps(r) + "\n"); log.flush()
        print(label, r.get("verdict"), r.get("score"), flush=True)

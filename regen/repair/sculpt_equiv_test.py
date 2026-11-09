"""Old vs new Loopcut sculpt_stroke on the same mesh and strokes: positions must match, and time both.
blender -b --factory-startup --python sculpt_equiv_test.py -- in.glb old_sculpt_file"""
import importlib.machinery
import importlib.util
import sys
import time
sys.dont_write_bytecode = True
sys.path.insert(0, "/mnt/sata/loopcut/scripts/addons_core/loopcut")
import bpy
import numpy as np
from studio_vendor.handlers import sculpt as NEW

src, old_path = sys.argv[sys.argv.index("--") + 1:][:2]
loader = importlib.machinery.SourceFileLoader("studio_vendor.handlers._sculpt_old", old_path)
spec = importlib.util.spec_from_loader(loader.name, loader)
OLD = importlib.util.module_from_spec(spec)
loader.exec_module(OLD)


def load():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=src)
    obj = next(o for o in bpy.context.scene.objects if o.type == "MESH")
    if obj.parent:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    import bmesh
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bm.to_mesh(obj.data); bm.free(); obj.data.update()
    return obj


def co(obj):
    a = np.empty(len(obj.data.vertices) * 3); obj.data.vertices.foreach_get("co", a)
    return a.reshape(-1, 3)


def strokes(obj, rows=3):
    out = []
    for i in range(rows):
        zr = -0.11 + 0.06 * i
        rough = [[xr, -zr, -0.40] for xr in [-0.32 + 0.04 * k for k in range(17)]]
        hits = NEW.surface_points(obj.name, points=rough)["points"]
        out.append([h["co"] for h in hits if h["hit"]])
    return out


def run(mod, brush, sym, kw):
    obj = load()
    t = time.perf_counter()
    for pts in strokes(obj):
        mod.sculpt_stroke(obj.name, brush, pts, 0.03, strength=0.8, symmetry=sym, **kw)
    return co(obj), time.perf_counter() - t


base = co(load())
print(f"EQUIV mesh {len(base)} verts")
bad = 0
for brush in NEW.BRUSHES:
    for sym in ("", "X"):
        kw = {"delta": [0.0, 0.0, 0.005]} if brush == "grab" else {}
        a, ta = run(OLD, brush, sym, kw)
        b, tb = run(NEW, brush, sym, kw)
        err = np.abs(a - b).max()
        moved = (np.abs(a - base).max(axis=1) > 0).sum()
        ok = err < 1e-9 and moved > 0
        bad += not ok
        print(f"EQUIV {brush:8s} sym={sym or '-':1s} moved {moved:6d} max|old-new| {err:.2e}  "
              f"old {ta:6.2f}s new {tb:6.2f}s x{ta / max(tb, 1e-9):5.1f}  {'OK' if ok else 'MISMATCH'}")
print("EQUIV RESULT", "PASS" if bad == 0 else f"FAIL ({bad})")

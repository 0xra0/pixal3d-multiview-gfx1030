"""Re-run build_asset stages 1-3 (no export) and say which part of the --texture-from atlas check fails.
blender -b --factory-startup --disable-autoexec --python atlas_diag.py -- painted.glb report.json <build_asset argv...>"""
import json
import sys
sys.dont_write_bytecode = True
import os
sys.path.insert(0, os.environ.get("ATLAS_KIT", "/mnt/ssd/work/pixal3d-mv"))
import bpy
import numpy as np
from mathutils.kdtree import KDTree
import build_asset as B
from asset_bake import uv_triangles
from asset_config import parse_asset

rest = sys.argv[sys.argv.index("--") + 1:]
painted, report_path, argv = rest[0], rest[1], rest[2:]
args = parse_asset(argv)
old = json.load(open(report_path))["options"]
diff = {k: (old.get(k), v) for k, v in vars(args).items() if k not in ("dst",) and old.get(k) != v
        and not (isinstance(v, tuple) and list(v) == old.get(k))}
print("ATLAS option differences vs painted build:", diff)


import hashlib
def _fp(objs, tag):
    h = hashlib.sha1()
    for o in objs:
        a = np.empty(len(o.data.vertices) * 3, np.float32); o.data.vertices.foreach_get("co", a); h.update(a.tobytes())
        l = np.empty(len(o.data.loops), np.int32); o.data.loops.foreach_get("vertex_index", l); h.update(l.tobytes())
    print("ATLAS fp", tag, len(objs), h.hexdigest()[:12], flush=True)
_run = B.prep.subprocess.run
def _logged(cmd, *a, **k):
    if k.get("input"):
        print("ATLAS fp xatlas-input", hashlib.sha1(k["input"]).hexdigest()[:12], flush=True)
    return _run(cmd, *a, **k)
B.prep.subprocess.run = _logged
obj = B.prep.import_mesh(str(args.src), object_name=args.source_object, visible_only=True,
                         source_up=args.source_up, yaw=args.yaw)
B.normalize(obj, args)
_fp([obj], 'imported')
highs, originals, records, repair = B.component_pass(obj, args, B.load_regions(args.regions))
_fp(highs, 'highs')
parts, targets = B.build_low_parts(highs, args)
_fp(parts, 'low')
parts, uv = B.atlas(parts, args)
ours = uv_triangles(parts)
import os
if os.environ.get("ATLAS_SAVE"):
    np.save(os.environ["ATLAS_SAVE"], ours)

before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=painted)
mesh = [x for x in bpy.data.objects if x not in before and x.type == "MESH"]
theirs = uv_triangles(mesh)
print(f"ATLAS triangles ours {len(ours)} painted {len(theirs)}; parts {len(parts)}; "
      f"faces per part {[len(p.data.polygons) for p in parts][:5]}; ngons {[sum(len(f.vertices) > 3 for f in p.data.polygons) for p in parts][:5]}")
a, b = ours.mean(axis=1), theirs.mean(axis=1)
tree = KDTree(len(b))
for i, (u, v) in enumerate(b):
    tree.insert((u, v, 0), i)
tree.balance()
hits = [tree.find((u, v, 0)) for u, v in a]
d = np.array([h[2] for h in hits])
print(f"ATLAS unique {len({h[1] for h in hits})} of {len(a)}; max distance {d.max():.3g}; over 1e-5 {(d > 1e-5).sum()}; "
      f"over 1e-3 {(d > 1e-3).sum()}")
# corner-set comparison: same triangles split differently would match as corner sets but not as centroids
ca = {tuple(sorted(map(tuple, np.round(t, 5)))) for t in ours}
cb = {tuple(sorted(map(tuple, np.round(t, 5)))) for t in theirs}
print(f"ATLAS triangle corner sets in common {len(ca & cb)} of {len(ca)}")
pts_a = {tuple(p) for p in np.round(ours.reshape(-1, 2), 5)}
pts_b = {tuple(p) for p in np.round(theirs.reshape(-1, 2), 5)}
print(f"ATLAS UV points in common {len(pts_a & pts_b)} of {len(pts_a)} / {len(pts_b)}")

"""Which part of asset_bake.painted_sources' atlas check fails? Compares the per-triangle UV centres of two GLBs.
blender -b --factory-startup --python uv_match_diag.py -- a.glb b.glb"""
import sys
sys.dont_write_bytecode = True
import bpy
import numpy as np
from mathutils.kdtree import KDTree


def tris(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    out = []
    for o in meshes:
        m = o.data
        m.calc_loop_triangles()
        uv = np.empty(len(m.loops) * 2, np.float32)
        m.uv_layers.active.data.foreach_get("uv", uv)
        loops = np.empty(len(m.loop_triangles) * 3, np.int32)
        m.loop_triangles.foreach_get("loops", loops)
        out.append(uv.reshape(-1, 2)[loops].reshape(-1, 3, 2))
    print(f"DIAG {path.split('/')[-1]}: {len(meshes)} meshes, uv layers {[l.name for l in meshes[0].data.uv_layers]}, "
          f"materials {len(meshes[0].data.materials)}")
    return np.concatenate(out)


a_path, b_path = sys.argv[sys.argv.index("--") + 1:][:2]
a, b = tris(a_path), tris(b_path)
print(f"DIAG triangles {len(a)} vs {len(b)}")
ours, theirs = a.mean(axis=1), b.mean(axis=1)
tree = KDTree(len(theirs))
for i, (u, v) in enumerate(theirs):
    tree.insert((u, v, 0), i)
tree.balance()
hits = [tree.find((u, v, 0)) for u, v in ours]
d = np.array([h[2] for h in hits])
uniq = len({h[1] for h in hits})
print(f"DIAG unique matches {uniq} of {len(ours)}; distance max {d.max():.3g}, p99 {np.percentile(d, 99):.3g}, "
      f"over 1e-5: {(d > 1e-5).sum()}")
for name, t in (("a", a), ("b", b)):
    print(f"DIAG {name} uv range u {t[..., 0].min():.4f}..{t[..., 0].max():.4f} v {t[..., 1].min():.4f}..{t[..., 1].max():.4f}")
# a flipped V (1 - v) would show as many large distances that vanish when flipped
flip = b.copy(); flip[..., 1] = 1 - flip[..., 1]
tree2 = KDTree(len(flip))
for i, (u, v) in enumerate(flip.mean(axis=1)):
    tree2.insert((u, v, 0), i)
tree2.balance()
d2 = np.array([tree2.find((u, v, 0))[2] for u, v in ours])
print(f"DIAG with b's V flipped: distance max {d2.max():.3g}, over 1e-5: {(d2 > 1e-5).sum()}")

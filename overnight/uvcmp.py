"""blender -b -P uvcmp.py -- a.glb b.glb : compare UV triangle centroids as painted_sources does."""
import sys, bpy, numpy as np
sys.path.insert(0, "/mnt/ssd/work/pixal3d-mv")
from asset_bake import uv_triangles
from mathutils.kdtree import KDTree
a, b = sys.argv[sys.argv.index("--") + 1:]
def load(p):
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=p)
    return [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
A, B = uv_triangles(load(a)).mean(1), uv_triangles(load(b)).mean(1)
t = KDTree(len(B))
for i, (u, v) in enumerate(B): t.insert((u, v, 0), i)
t.balance()
h = [t.find((u, v, 0)) for u, v in A]
d = np.array([x[2] for x in h])
print("CMP", len(A), len(B), "unique", len({x[1] for x in h}), "maxd", d.max(), "n>1e-5", int((d > 1e-5).sum()))

"""At each front-view disc ray's first high hit: how many faces lie within eps, and do they face both ways?
blender -b --factory-startup --python med_coplanar.py -- high.glb out.npz"""
import sys
sys.dont_write_bytecode = True
import bpy, bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0, "/mnt/ssd/work/pixal3d-mv")
import prep_mesh
src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
prep_mesh.import_mesh(src, visible_only=True, source_up="auto", yaw=0)
o = [x for x in bpy.data.objects if x.type == "MESH"][0]
bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); bm.normal_update(); bm.faces.ensure_lookup_table()
co = np.array([v.co[:] for v in bm.verts]); lo, hi = co.min(0), co.max(0); size = (hi - lo).max(); c = (lo + hi) / 2
bt = BVHTree.FromBMesh(bm)
N = 120; half = 0.09 * size; zc = c[2] + 0.165 * size
d = Vector((0, 1, 0)); res = []
for z in np.linspace(zc + half, zc - half, N):
    for x in np.linspace(c[0] - half, c[0] + half, N):
        if (x - c[0]) ** 2 + (z - zc) ** 2 > half * half: continue
        loc, nrm, idx, dist = bt.ray_cast(Vector((x, lo[1] - 0.1 * size, z)), d)
        if loc is None: continue
        row = [x, z, float(nrm.dot(d) > 0)]
        for eps in (1e-6, 1e-5, 1e-4, 1e-3):
            near = bt.find_nearest_range(loc, eps)
            dots = [bm.faces[i].normal.dot(d) for (_, _, i, _) in near]
            row += [len(near), sum(t > 0.3 for t in dots), sum(t < -0.3 for t in dots)]
        res.append(row)
res = np.array(res); np.save(out, res)
print("COP rays", len(res), "first back", res[:, 2].mean().round(3))
for k, eps in enumerate((1e-6, 1e-5, 1e-4, 1e-3)):
    away, toward = res[:, 4 + 3 * k], res[:, 5 + 3 * k]
    print(f"COP eps {eps:g} (={eps / size:.1e} size): faces median {np.median(res[:, 3 + 3 * k]):.0f}; both orientations present {((away > 0) & (toward > 0)).mean():.3f}")
# y-thickness of the disc sheet: spread of vertex y in the disc cylinder, front half
m = ((co[:, 0] - c[0]) ** 2 + (co[:, 2] - zc) ** 2 < (0.08 * size) ** 2) & (co[:, 1] < c[1])
print("COP disc verts", m.sum(), "y percentiles", np.round(np.percentile(co[m, 1], [1, 5, 25, 50, 75, 95, 99]), 5))

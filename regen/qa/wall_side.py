import sys, bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
path = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=path)
dg = bpy.context.evaluated_depsgraph_get(); verts, polys = [], []
for o in [o for o in bpy.data.objects if o.type == "MESH"]:
    me = o.evaluated_get(dg).to_mesh(); base = len(verts)
    verts += [o.matrix_world @ v.co for v in me.vertices]; polys += [[base + i for i in p.vertices] for p in me.polygons]
tree = BVHTree.FromPolygons(verts, polys)
lo = Vector([min(v[i] for v in verts) for i in range(3)]); hi = Vector([max(v[i] for v in verts) for i in range(3)])
# Blender +Z = file +Y = Pixal3D front camera side. Depth of each crossing as 0 (back) .. 1 (front).
for frac in (0.75, 0.68, 0.6, 0.5, 0.4, 0.3):
    y = lo.y + (hi.y - lo.y) * frac; row = []
    for k in range(7):
        x = lo.x + (hi.x - lo.x) * (0.2 + 0.6 * k / 6); p = Vector((x, y, lo.z - 1)); zs = []
        while True:
            h = tree.ray_cast(p, Vector((0, 0, 1)))
            if h[0] is None: break
            zs.append(round((h[0].z - lo.z) / (hi.z - lo.z), 2)); p = h[0] + Vector((0, 0, 1e-5))
        row.append(zs)
    print(f"height {frac:.2f}:", "  ".join(",".join(f"{z:.2f}" for z in r) for r in row))

import sys, bpy, bmesh
from mathutils import Vector
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
print("MESHES", [(o.name, len(o.data.polygons), len(o.data.materials)) for o in meshes])
o = meshes[0]
bm = bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
seen, islands = set(), []
for f in bm.faces:
    if f.index in seen: continue
    stack, isl = [f], []
    seen.add(f.index)
    while stack:
        g = stack.pop(); isl.append(g)
        for e in g.edges:
            for h in e.link_faces:
                if h.index not in seen: seen.add(h.index); stack.append(h)
    islands.append(isl)
islands.sort(key=len, reverse=True)
def bb(isl):
    vs = [v.co for f in isl for v in f.verts]
    return Vector([min(v[i] for v in vs) for i in range(3)]), Vector([max(v[i] for v in vs) for i in range(3)])
mlo, mhi = bb(islands[0]); diag = (mhi - mlo).length
print("ISLANDS", len(islands), "main", len(islands[0]), "diag", round(diag, 4))
far = []
for isl in islands[1:]:
    lo, hi = bb(isl)
    gap = max(max(mlo[i] - hi[i], lo[i] - mhi[i], 0) for i in range(3))
    if gap > 0.05 * diag:
        far.append(isl); print("FAR", len(isl), "gap", round(gap, 4), [round(x, 3) for x in lo], [round(x, 3) for x in hi])
print("FAR_TOTAL", len(far), sum(len(i) for i in far))
if out != "-":
    bmesh.ops.delete(bm, geom=list({f for i in far for f in i}), context="FACES_ONLY")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(o.data); o.data.update()
    print("AFTER", len(o.data.polygons))
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB")

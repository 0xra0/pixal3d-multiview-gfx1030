import bpy, bmesh
obj = next(o for o in bpy.data.objects if o.type == "MESH")
bm = bmesh.new(); bm.from_mesh(obj.data); uv = bm.loops.layers.uv.active
bm.faces.ensure_lookup_table()
parent = list(range(len(bm.faces)))
def find(i):
    while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
    return i
for e in bm.edges:
    if len(e.link_faces) != 2: continue
    f0, f1 = e.link_faces
    def uvs(f):
        return {l.vert.index: tuple(l[uv].uv) for l in f.loops}
    a, b = uvs(f0), uvs(f1)
    if all(a[v.index] == b[v.index] for v in e.verts): parent[find(f0.index)] = find(f1.index)
from collections import Counter
sizes = sorted(Counter(find(i) for i in range(len(bm.faces))).values(), reverse=True)
print("islands", len(sizes), "single", sum(1 for s in sizes if s == 1), "<10", sum(1 for s in sizes if s < 10), "top", sizes[:8])

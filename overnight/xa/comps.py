import bpy, bmesh, sys
from collections import Counter
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=sys.argv[sys.argv.index("--") + 1])
bm = bmesh.new()
for o in bpy.data.objects:
    if o.type == "MESH":
        o.data.transform(o.matrix_world); bm.from_mesh(o.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
from mathutils import Vector
cos = [v.co for v in bm.verts]
gd = (Vector(map(max, *[c[:] for c in cos])) - Vector(map(min, *[c[:] for c in cos]))).length
seen, rows = set(), []
for f in bm.faces:
    if f in seen: continue
    stack, comp = [f], []
    seen.add(f)
    while stack:
        g = stack.pop(); comp.append(g)
        for e in g.edges:
            for h in e.link_faces:
                if h not in seen: seen.add(h); stack.append(h)
    vs = {v for g in comp for v in g.verts}
    lo = Vector(map(min, *[v.co[:] for v in vs])); hi = Vector(map(max, *[v.co[:] for v in vs]))
    open_ = any(not e.is_manifold for g in comp for e in g.edges)
    rows.append((len(comp), (hi - lo).length / gd, open_))
rows.sort()
print("COMPS", len(rows), "open", sum(r[2] for r in rows))
for lim in (.005, .01, .02, .05):
    print("COMPS open&diag<", lim, sum(1 for r in rows if r[2] and r[1] < lim), "closed&diag<", lim, sum(1 for r in rows if not r[2] and r[1] < lim))
print("COMPS largest-small", [(n, round(d, 4), o) for n, d, o in sorted(rows, key=lambda r: -r[1])[:12]])

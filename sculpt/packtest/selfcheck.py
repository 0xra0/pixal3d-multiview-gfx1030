import bpy, sys
exec(open("variant.py").read().split("q = pm.inspect_mesh")[0])
q = pm.inspect_mesh(obj, check_overlap=True)
bad = set(q["uv_overlap_faces"])
import bmesh
bm = bmesh.new(); bm.from_mesh(obj.data); uv = bm.loops.layers.uv.active
def sgn(a, b, c): return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)
selfx = 0; flipped = 0; selfx_bad = 0
for i, f in enumerate(bm.faces):
    c = [l[uv].uv for l in f.loops]
    s = [sgn(c[0], c[k], c[k + 1]) for k in range(1, len(c) - 1)]
    tw = any(x > 0 for x in s) and any(x < 0 for x in s)
    selfx += tw; selfx_bad += tw and i in bad
    flipped += all(x < 0 for x in s)
print("RESULT bad", len(bad), "twisted(fan sign mix)", selfx, "of which bad", selfx_bad, "fully flipped", flipped, "faces", len(bm.faces))

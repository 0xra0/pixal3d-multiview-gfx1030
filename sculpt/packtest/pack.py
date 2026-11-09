import bpy, bmesh, time, sys
method = sys.argv[sys.argv.index("--") + 1]
obj = next(o for o in bpy.data.objects if o.type == "MESH")
for m in list(obj.modifiers): obj.modifiers.remove(m)
bpy.context.view_layer.objects.active = obj; obj.select_set(True)
def fill():
    bm = bmesh.new(); bm.from_mesh(obj.data); uv = bm.loops.layers.uv.active
    s = 0.0
    for f in bm.faces:
        c = [l[uv].uv for l in f.loops]
        s += abs(sum(c[i].x * c[i-1].y - c[i-1].x * c[i].y for i in range(len(c)))) / 2
    bm.free(); return s
print("before", round(fill(), 4))
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.uv.select_all(action="SELECT")
t = time.time()
bpy.ops.uv.pack_islands(rotate=True, shape_method=method, margin_method="FRACTION", margin=4/2048)
bpy.ops.object.mode_set(mode="OBJECT")
print(method, "fill", round(fill(), 4), "secs", round(time.time() - t, 1))

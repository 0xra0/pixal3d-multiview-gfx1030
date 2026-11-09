import bpy, bmesh, sys, time, math
sys.path.insert(0, "/mnt/ssd/work/pixal3d-mv")
import prep_mesh as pm
small = int(sys.argv[sys.argv.index("--") + 1])
obj = next(o for o in bpy.data.objects if o.type == "MESH")
for m in list(obj.modifiers): obj.modifiers.remove(m)
while obj.data.uv_layers: obj.data.uv_layers.remove(obj.data.uv_layers[0])
pm.activate(obj); obj.data.uv_layers.new(name="GameUV")
t = time.time()
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0, area_weight=0, correct_aspect=True, scale_to_bounds=False)
bpy.ops.uv.select_all(action="SELECT"); bpy.ops.uv.seams_from_islands(mark_seams=True)
bpy.ops.object.mode_set(mode="OBJECT")
exec(open("islands.py").read())
from collections import Counter
size = Counter(find(i) for i in range(len(bm.faces)))
cleared = 0
for e in bm.edges:
    if e.seam and any(size[find(f.index)] < small for f in e.link_faces):
        e.seam = False; cleared += 1
bm.to_mesh(obj.data); bm.free()
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.unwrap(method="ANGLE_BASED", margin=0)
bpy.ops.uv.select_all(action="SELECT"); bpy.ops.uv.average_islands_scale()
bpy.ops.uv.pack_islands(rotate=True, shape_method="CONCAVE", margin_method="FRACTION", margin=4/2048)
bpy.ops.object.mode_set(mode="OBJECT")
exec(open("islands.py").read())
q = pm.inspect_mesh(obj, check_overlap=True)
print("RESULT small", small, "cleared", cleared, "islands", len(sizes), "single", sum(s == 1 for s in sizes), "overlap", len(q.get("uv_overlap_faces", ())), "fill", round(q.get("uv_area_sum", 0), 4), "secs", round(time.time() - t, 1))

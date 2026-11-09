import bpy, sys, time, types
sys.path.insert(0, "/mnt/ssd/work/pixal3d-mv")
import prep_mesh as pm
k = int(sys.argv[sys.argv.index("--") + 1])
obj = next(o for o in bpy.data.objects if o.type == "MESH")
for m in list(obj.modifiers): obj.modifiers.remove(m)
while obj.data.uv_layers: obj.data.uv_layers.remove(obj.data.uv_layers[0])
args = types.SimpleNamespace(uv_angle=66, uv_margin_px=4, texture_size=2048, uv_merge_faces=k)
t = time.time()
pm.smart_uv(obj, args); pm.fix_uv_overlaps(obj, args)
exec(open("islands.py").read())
q = pm.inspect_mesh(obj, check_overlap=True)
print("RESULT k", k, "islands", len(sizes), "single", sum(s == 1 for s in sizes), "overlap", len(q.get("uv_overlap_faces", ())), "zero", q.get("zero_area_uv_faces"), "fill", round(q.get("uv_area_sum", 0), 4), "secs", round(time.time() - t, 1))

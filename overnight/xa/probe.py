import bpy, sys, types
sys.path.insert(0, "/mnt/ssd/work/pixal3d-mv")
import prep_mesh as pm
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=sys.argv[sys.argv.index("--") + 1])
obj = next(o for o in bpy.data.objects if o.type == "MESH")
pm.activate(obj)
pm.edit_mesh(obj, lambda bm: __import__("bmesh").ops.remove_doubles(bm, verts=bm.verts, dist=1e-7))
while obj.data.uv_layers: obj.data.uv_layers.remove(obj.data.uv_layers[0])
args = types.SimpleNamespace(texture_size=2048, uv_margin_px=4)
pm.xatlas_uv(obj, args)
q = pm.inspect_mesh(obj, check_overlap=True)
print("PROBE cover", round(q["uv_area_sum"], 4), "zero", q["zero_area_uv_faces"], "invalid", q["invalid_uv_corners"], "pairs", q.get("uv_overlap_pairs"), "faces", q.get("uv_overlap_faces"), "samples", q.get("uv_overlap_samples"))
uv = obj.data.uv_layers.active.data
for i in q.get("uv_overlap_faces", [])[:6]:
    p = obj.data.polygons[i]
    print("PROBE face", i, "area3d", p.area, "uv", [tuple(round(c, 6) for c in uv[l].uv) for l in p.loop_indices])

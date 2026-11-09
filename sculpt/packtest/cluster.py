import bpy, bmesh, sys
exec(open("variant.py").read().split("q = pm.inspect_mesh")[0])
for rnd in range(3):
    q = pm.inspect_mesh(obj, check_overlap=True)
    bad = set(q["uv_overlap_faces"])
    print("RESULT round", rnd, "bad", len(bad), "fill", round(q["uv_area_sum"], 4))
    if not bad: break
    def sel(bm):
        for f in bm.faces: f.select_set(f.index in bad)
    pm.edit_mesh(obj, sel)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.uv.select_all(action="SELECT"); bpy.ops.uv.seams_from_islands(mark_seams=True)
    bpy.ops.mesh.region_to_loop(); bpy.ops.mesh.mark_seam(clear=False)
    bpy.ops.mesh.select_all(action="DESELECT"); bpy.ops.object.mode_set(mode="OBJECT")
    pm.edit_mesh(obj, sel)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.uv.unwrap(method="ANGLE_BASED", margin=0)
    bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.uv.select_all(action="SELECT")
    bpy.ops.uv.average_islands_scale()
    bpy.ops.uv.pack_islands(rotate=True, shape_method="CONCAVE", margin_method="FRACTION", margin=4/2048)
    bpy.ops.object.mode_set(mode="OBJECT")

import bpy, sys
src, out, vox = sys.argv[-3], sys.argv[-2], float(sys.argv[-1])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
ms = [o for o in bpy.context.scene.objects if o.type == "MESH"]
bpy.context.view_layer.objects.active = ms[0]
for o in ms: o.select_set(True)
if len(ms) > 1: bpy.ops.object.join()
o = bpy.context.view_layer.objects.active
o.data.remesh_voxel_size = vox * o.dimensions.length
bpy.ops.object.voxel_remesh()
print("VOX faces", len(o.data.polygons))
bpy.ops.wm.ply_export(filepath=out, export_selected_objects=True, apply_modifiers=False, export_normals=False, export_uv=False, export_colors="NONE", export_triangulated_mesh=True, ascii_format=False)

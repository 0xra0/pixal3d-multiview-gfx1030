import bpy, sys
out = sys.argv[sys.argv.index("--") + 1]
obj = next(o for o in bpy.data.objects if o.type == "MESH")
mod = obj.modifiers[0]
print("TOP", mod.type, mod.levels, mod.sculpt_levels, mod.total_levels, len(obj.data.polygons))
bpy.context.view_layer.objects.active = obj; obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_apply=True)

import bpy
gl = bpy.ops.export_scene.gltf.get_rna_type().properties["export_format"]
print("GLTF_FORMATS", [i.identifier for i in gl.enum_items], "default", gl.default)
sc = bpy.context.scene
try:
    sc.render.engine = "NOPE"
except TypeError as ex:
    print("ENGINES", str(ex)[:300])

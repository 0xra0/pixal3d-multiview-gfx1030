import bpy
out = "/mnt/ssd/work/loopcut-local/t.glb"
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_apply=True)
print("GLB_MAGIC", open(out, "rb").read(4))

import bpy, sys
from mathutils import Vector
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
objs = [o for o in bpy.data.objects if o.type == "MESH"]
pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
lo = Vector(map(min, *[p[:] for p in pts])); hi = Vector(map(max, *[p[:] for p in pts])); c = (lo + hi) / 2; r = (hi - lo).length
print("BOUNDS lo", tuple(round(x, 3) for x in lo), "hi", tuple(round(x, 3) for x in hi))
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"; scene.display.shading.color_type = "TEXTURE"
scene.render.resolution_x = scene.render.resolution_y = 384
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
cam.location = c + Vector((0, -1.6 * r, 0)); cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
scene.render.filepath = out; bpy.ops.render.render(write_still=True)

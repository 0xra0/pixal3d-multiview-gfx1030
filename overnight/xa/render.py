import bpy, sys, math
from mathutils import Vector
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
objs = [o for o in bpy.data.objects if o.type == "MESH"]
pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
lo = Vector(map(min, *[p[:] for p in pts])); hi = Vector(map(max, *[p[:] for p in pts])); c = (lo + hi) / 2; r = (hi - lo).length
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"; scene.display.shading.color_type = "TEXTURE"
scene.render.resolution_x = scene.render.resolution_y = 512
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
for i, ang in enumerate((0, 160)):
    a = math.radians(ang); cam.location = c + Vector((math.sin(a) * r * .3, -math.cos(a) * r * .3, r * 1.4 * (1 if i == 0 else -1)))
    cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = f"{out}_{i}.png"; bpy.ops.render.render(write_still=True)

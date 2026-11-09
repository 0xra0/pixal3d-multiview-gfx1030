import bpy, sys, math
from mathutils import Vector
src, dst = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
ctr, size = (lo + hi) / 2, max(hi - lo)
sc = bpy.context.scene
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
cam.data.type = "ORTHO"; cam.data.ortho_scale = size * 1.15
cam.location = ctr + Vector((0, -size * 3, 0)); cam.rotation_euler = (math.pi / 2, 0, 0); sc.camera = cam
for rot, e in (((0.9, 0, 0.5), 3.0), ((1.2, 0, -2.4), 1.5)):
    l = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); l.data.energy = e; l.rotation_euler = rot; sc.collection.objects.link(l)
sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.35, 0.35, 0.35)
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
sc.render.resolution_x = sc.render.resolution_y = 768; sc.render.film_transparent = True
sc.render.filepath = dst; bpy.ops.render.render(write_still=True)
print("bounds", [round(v, 3) for v in lo], [round(v, 3) for v in hi])

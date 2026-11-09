import bpy, sys, math
from mathutils import Vector
# Same camera/lights as render_front.py, but every material replaced by plain grey,
# so any banding left in the image comes from the geometry, not the texture.
src, dst = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
grey = bpy.data.materials.new("grey"); grey.use_nodes = True
bsdf = next(n for n in grey.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
bsdf.inputs["Base Color"].default_value = (0.6, 0.6, 0.6, 1); bsdf.inputs["Roughness"].default_value = 0.5
for o in objs:
    o.data.materials.clear(); o.data.materials.append(grey)
    print("mesh", o.name, "faces", len(o.data.polygons), "smooth", sum(p.use_smooth for p in o.data.polygons))
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

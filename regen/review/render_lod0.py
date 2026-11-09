"""Front/back EEVEE renders of a built LOD0 GLB with its baked material. -- in.glb out_prefix"""
import sys, math
sys.dont_write_bytecode = True
import bpy
from mathutils import Vector
src, prefix = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
c, size = (lo + hi) / 2, max(hi - lo)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x = sc.render.resolution_y = 700
sc.world = bpy.data.worlds.new("W"); sc.world.color = (0.6, 0.6, 0.6)
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = size * 1.15
for name, ang in (("front", 0.0), ("back", 180.0)):
    for i, (dx, dy) in enumerate(((0, -1), (0, 1))):
        pass
    a = math.radians(ang)
    # glTF import: front of these assets faces -Y in Blender
    d = Vector((math.sin(a), -math.cos(a), 0))
    cam.location = c + d * size * 3
    cam.rotation_euler = (d * -1).to_track_quat("-Z", "Y").to_euler()
    for l in [x for x in sc.collection.objects if x.type == "LIGHT"]:
        bpy.data.objects.remove(l)
    sun = bpy.data.objects.new("S", bpy.data.lights.new("S", "SUN")); sc.collection.objects.link(sun)
    sun.data.energy = 3.0; sun.rotation_euler = (d * -1 + Vector((0, 0, -0.6))).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = f"{prefix}_{name}.png"
    bpy.ops.render.render(write_still=True)
    print("RENDER", sc.render.filepath)

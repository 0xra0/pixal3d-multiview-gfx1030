import bpy, sys, math
from mathutils import Vector
glb, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
ob = next(o for o in bpy.context.scene.objects if o.type == "MESH")
for m in ob.data.materials: m.use_nodes = False
corners = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
c = sum(corners, Vector()) / 8
size = max((max(p[i] for p in corners) - min(p[i] for p in corners)) for i in range(3))
sc = bpy.context.scene
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
cam.data.type = "ORTHO"; cam.data.ortho_scale = size * 1.1
# glTF import is Y-up -> Blender Z-up; file -Y (back camera) becomes Blender +Z? compute from file coords:
# file (x,y,z) -> blender (x,-z,y). Back camera at file -Y -> blender (0,0,-1)*... use direction d
d = Vector((0, 0, -1))   # file -Y maps to blender z = file y -> -1
cam.location = c + d * size * 3
up = Vector((0, 1, 0))   # file up is -Z -> blender y = -file z = +1
cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
sc.camera = cam
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun)
sun.rotation_euler = cam.rotation_euler; sun.data.energy = 3
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 16
sc.render.resolution_x = sc.render.resolution_y = 768
sc.render.filepath = out
bpy.ops.render.render(write_still=True)

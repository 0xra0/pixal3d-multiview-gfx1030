"""Render a textured GLB from -Y (front), +Y (back), +X and -X with Workbench texture colour.
blender -b -P render_tex.py -- <glb> <out_prefix>"""
import sys

import bpy
from mathutils import Matrix, Vector

glb, prefix, mode = (sys.argv[sys.argv.index("--") + 1:] + ["TEXTURE"])[:3]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
lo = Vector([min(p[i] for p in pts) for i in range(3)])
hi = Vector([max(p[i] for p in pts) for i in range(3)])
center, size = (lo + hi) / 2, max(hi - lo)

scene = bpy.context.scene
try:
    scene.render.engine = "BLENDER_WORKBENCH"
except TypeError as e:
    print(e)
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = mode
scene.display.shading.show_cavity = mode != "TEXTURE"
scene.render.resolution_x = scene.render.resolution_y = 512
scene.render.film_transparent = False
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cam.data.type = "ORTHO"
cam.data.ortho_scale = size * 1.1
scene.collection.objects.link(cam)
scene.camera = cam
for tag, d in {"front": (0, -1, 0), "back": (0, 1, 0), "right": (1, 0, 0), "left": (-1, 0, 0)}.items():
    cam.location = center + Vector(d) * size * 3
    back = Vector(d)
    right = Vector((0, 0, 1)).cross(back).normalized()
    cam.rotation_euler = Matrix((right, Vector((0, 0, 1)), back)).transposed().to_euler()
    scene.render.filepath = f"{prefix}_{tag}.png"
    bpy.ops.render.render(write_still=True)
print("BOUNDS", tuple(round(v, 3) for v in lo), tuple(round(v, 3) for v in hi))

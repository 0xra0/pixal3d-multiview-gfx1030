"""Front crop of the LOD0 with one material input cut at a time: which baked map makes the medallion white?"""
import sys, math
sys.dont_write_bytecode = True
import bpy
from mathutils import Vector
src, prefix = sys.argv[sys.argv.index("--") + 1:][:2]
def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=src)
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    c, size = (lo + hi) / 2, max(hi - lo)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x = sc.render.resolution_y = 500
    sc.world = bpy.data.worlds.new("W"); sc.world.color = (0.6, 0.6, 0.6)
    cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.type = "ORTHO"; cam.data.ortho_scale = size * 0.45
    d = Vector((0, -1, 0)); cam.location = c + Vector((0, 0, size * 0.12)) + d * size * 3
    cam.rotation_euler = (d * -1).to_track_quat("-Z", "Y").to_euler()
    sun = bpy.data.objects.new("S", bpy.data.lights.new("S", "SUN")); sc.collection.objects.link(sun)
    sun.data.energy = 3.0; sun.rotation_euler = Vector((0.7, 1, -0.9)).to_track_quat("-Z", "Y").to_euler()
    return objs
for cut in (sys.argv[-1].split(",") if sys.argv[-1].startswith("cuts=") is False and "," in sys.argv[-1] else ("none", "Base Color", "Normal", "Roughness", "Metallic")):
    objs = setup()
    for o in objs:
        for m in o.data.materials:
            b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
            if cut != "none" and b.inputs[cut].is_linked:
                for l in list(b.inputs[cut].links):
                    m.node_tree.links.remove(l)
                if cut == "Base Color":
                    b.inputs[cut].default_value = (0.05, 0.05, 0.05, 1)
    print("LINKS", cut, [(s.name) for s in b.inputs if s.is_linked])
    bpy.context.scene.render.filepath = f"{prefix}_cut_{cut.replace(' ', '')}.png"
    bpy.ops.render.render(write_still=True)

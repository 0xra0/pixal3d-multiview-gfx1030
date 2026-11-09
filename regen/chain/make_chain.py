"""Headless: build an interlocking oval-link necklace chain along a closed curve and export it as GLB.
  blender -b --factory-startup --python make_chain.py -- out.glb [link_mm] [wire_mm]
Z up, front -Y; the bail top is at the origin, so the pendant's bail ring goes there."""
import math, sys
import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
out = argv[0]
link = float(argv[1]) / 1000 if len(argv) > 1 else 0.009     # outer length of one link
wire = float(argv[2]) / 1000 if len(argv) > 2 else 0.0016    # wire diameter
width = link * 0.62                                          # outer width

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# one link: an oval torus along X; the next is the same turned 90 degrees about X, one pitch further
def make_link(name, roll):
    bpy.ops.mesh.primitive_torus_add(major_segments=16, minor_segments=6,
                                     major_radius=(width - wire) / 2, minor_radius=wire / 2)
    o = bpy.context.object
    o.name = name
    o.scale.x = (link - wire) / (width - wire)               # stretch the ring into an oval
    bpy.ops.object.transform_apply(scale=True)
    o.rotation_euler.x = roll
    return o

pitch = link - 2 * wire                                      # inner length: each link hangs in the next one
a = make_link("link_a", 0.0)
b = make_link("link_b", math.pi / 2)
b.location.x = pitch
bpy.ops.object.select_all(action="DESELECT")
a.select_set(True); b.select_set(True)
bpy.context.view_layer.objects.active = a
bpy.ops.object.join()
pair = a
bpy.ops.object.transform_apply(location=True, rotation=True)

# the necklace path (metres): bail, up the chest, around the neck, back down to the bail
half = [(0.0, 0.0, 0.0), (0.035, -0.004, 0.06), (0.058, 0.010, 0.135), (0.066, 0.045, 0.185),
        (0.050, 0.085, 0.205), (0.0, 0.102, 0.212)]
pts = half + [(-x, y, z) for (x, y, z) in reversed(half[1:-1])]
curve = bpy.data.curves.new("necklace", "CURVE")
curve.dimensions = "3D"
spline = curve.splines.new("NURBS")
spline.points.add(len(pts) - 1)
for p, (x, y, z) in zip(spline.points, pts):
    p.co = (x, y, z, 1.0)
spline.use_cyclic_u = True
spline.order_u = 4
path = bpy.data.objects.new("necklace_path", curve)
scene.collection.objects.link(path)
bpy.context.view_layer.update()
length = sum(s.calc_length() for s in curve.splines)

pairs = max(2, int(length / (2 * pitch)))
arr = pair.modifiers.new("array", "ARRAY")
arr.count = pairs
arr.use_relative_offset = False
arr.use_constant_offset = True
arr.constant_offset_displace = (2 * length / (2 * pairs), 0, 0)   # spread the pairs evenly over the loop
arr.use_merge_vertices = False
bend = pair.modifiers.new("curve", "CURVE")
bend.object = path
bend.deform_axis = "POS_X"
bpy.context.view_layer.objects.active = pair
bpy.ops.object.modifier_apply(modifier="array")
bpy.ops.object.modifier_apply(modifier="curve")
pair.name = "chain"
bpy.data.objects.remove(path)

mat = bpy.data.materials.new("chain_iron")
mat.use_nodes = True
bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
bsdf.inputs["Base Color"].default_value = (0.09, 0.085, 0.08, 1)
bsdf.inputs["Metallic"].default_value = 1.0
bsdf.inputs["Roughness"].default_value = 0.45
pair.data.materials.append(mat)
bpy.ops.object.shade_smooth()

tris = sum(len(p.vertices) - 2 for p in pair.data.polygons)
print(f"CHAIN loop {length * 100:.1f} cm, {pairs * 2} links of {link * 1000:.1f} mm, {tris} triangles")
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_yup=True)

"""Headless: hang an interlocking link chain through the pendant's bail and export pendant+chain.
  blender -b --factory-startup --python attach_chain.py -- pendant.glb out_dir [link_mm] [wire_mm] [segments] [sides]
Finds the bail hole by casting rays along X through the top of the pendant (the hole axis is X: the side
views show the open loop), builds the chain along a necklace curve whose lowest point goes through the
hole centre, and writes chain.glb, pendant_with_chain.glb and a measurement line."""
import math, sys
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index("--") + 1:]
src, out_dir = argv[0], argv[1]
link = float(argv[2]) / 1000 if len(argv) > 2 else 0.0045
wire = float(argv[3]) / 1000 if len(argv) > 3 else 0.001
segments = int(argv[4]) if len(argv) > 4 else 10
sides = int(argv[5]) if len(argv) > 5 else 4
width = link * 0.62

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=src)
pendant = next(o for o in scene.objects if o.type == "MESH")
pendant.name = "pendant"
deps = bpy.context.evaluated_depsgraph_get()
bvh = BVHTree.FromObject(pendant, deps)
corners = [pendant.matrix_world @ Vector(c) for c in pendant.bound_box]
lo = Vector([min(c[i] for c in corners) for i in range(3)])
hi = Vector([max(c[i] for c in corners) for i in range(3)])
print(f"PENDANT bbox {tuple(round(v, 4) for v in lo)} .. {tuple(round(v, 4) for v in hi)}")

# --- the bail hole: rays along +X over a Y/Z grid in the top 15% -----------------------------------
step = 0.0001
z0 = hi.z - 0.15 * (hi.z - lo.z)
ny, nz = int((hi.y - lo.y) / step) + 3, int((hi.z - z0) / step) + 3
hit = [[bvh.ray_cast(Vector((lo.x - 0.01, lo.y + (j - 1) * step, z0 + (k - 1) * step)), Vector((1, 0, 0)),
                     1.0)[0] is not None for k in range(nz)] for j in range(ny)]
seen = [[False] * nz for _ in range(ny)]
stack = [(j, k) for j in range(ny) for k in range(nz) if j in (0, ny - 1) or k in (0, nz - 1)]
while stack:                                     # flood the open air from the border; what stays is the hole
    j, k = stack.pop()
    if 0 <= j < ny and 0 <= k < nz and not seen[j][k] and not hit[j][k]:
        seen[j][k] = True
        stack += [(j + 1, k), (j - 1, k), (j, k + 1), (j, k - 1)]
hole = [(j, k) for j in range(ny) for k in range(nz) if not hit[j][k] and not seen[j][k]]
if not hole:
    sys.exit("BAIL HOLE NOT FOUND: no enclosed opening along X in the top 15%")
cy = lo.y + (sum(j for j, _ in hole) / len(hole) - 1) * step
cz = z0 + (sum(k for _, k in hole) / len(hole) - 1) * step
span_y = (max(j for j, _ in hole) - min(j for j, _ in hole) + 1) * step
span_z = (max(k for _, k in hole) - min(k for _, k in hole) + 1) * step
cx = (lo.x + hi.x) / 2
print(f"BAIL HOLE centre ({cx:.4f}, {cy:.4f}, {cz:.4f}) size Y {span_y * 1000:.1f} mm  Z {span_z * 1000:.1f} mm, "
      f"area {len(hole) * step * step * 1e6:.1f} mm2")


# --- the chain -------------------------------------------------------------------------------------
def make_link(name, roll):
    bpy.ops.mesh.primitive_torus_add(major_segments=segments, minor_segments=sides,
                                     major_radius=(width - wire) / 2, minor_radius=wire / 2)
    o = bpy.context.object
    o.name = name
    o.scale.x = (link - wire) / (width - wire)
    bpy.ops.object.transform_apply(scale=True)
    o.rotation_euler.x = roll
    return o


pitch = link - 2 * wire
a = make_link("link_a", 0.0)
b = make_link("link_b", math.pi / 2)
b.location.x = pitch
bpy.ops.object.select_all(action="DESELECT")
a.select_set(True); b.select_set(True)
bpy.context.view_layer.objects.active = a
bpy.ops.object.join()
pair = a
bpy.ops.object.transform_apply(location=True, rotation=True)

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
spline.resolution_u = 64
path = bpy.data.objects.new("necklace_path", curve)
scene.collection.objects.link(path)
bpy.context.view_layer.update()
sampled = [v.co.copy() for v in path.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh().vertices]
bottom = min(sampled, key=lambda v: v.z)
hole_top = z0 + (max(k for _, k in hole) - 1) * step
rest = hole_top - width / 2 - 0.0002       # the pendant hangs: the bail's inner top rests on the link
shift = Vector((cx, cy, rest)) - bottom
path.location = shift                      # the curve's lowest point now runs through the hole, under its top
bpy.context.view_layer.update()
length = sum(s.calc_length() for s in curve.splines)

pairs = max(2, int(length / (2 * pitch)))
arr = pair.modifiers.new("array", "ARRAY")
arr.count = pairs
arr.use_relative_offset = False
arr.use_constant_offset = True
arr.constant_offset_displace = (length / pairs, 0, 0)
arr.use_merge_vertices = False
# the curve modifier works in the curve's local space: start the links at the curve's origin, offset
# along the loop so one link is centred at the bottom (arc position 0 is the first control point = bottom)
pair.location = shift
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
bpy.ops.object.select_all(action="DESELECT")
pair.select_set(True)
bpy.context.view_layer.objects.active = pair
bpy.ops.object.shade_smooth()

# --- does the chain clear the bail? distance from chain vertices near the hole to the pendant surface ---
mw = pair.matrix_world
near = [mw @ v.co for v in pair.data.vertices if (mw @ v.co - Vector((cx, cy, cz))).length < 0.004]
inside = 0
for p in near:                              # a vertex inside the pendant sees an odd number of surfaces along +X
    n, o = 0, p.copy()
    while True:
        loc, _, _, _ = bvh.ray_cast(o, Vector((1, 0, 0)), 1.0)
        if loc is None:
            break
        n += 1
        o = loc + Vector((1e-6, 0, 0))
    inside += n % 2
lowest = min((mw @ v.co).z for v in pair.data.vertices)
tris = sum(len(p.vertices) - 2 for p in pair.data.polygons)
print(f"CHAIN loop {length * 100:.1f} cm, {pairs * 2} links of {link * 1000:.1f} mm / {wire * 1000:.1f} mm wire, "
      f"{tris} triangles; {inside}/{len(near)} chain vertices near the bail are inside the pendant; "
      f"chain lowest z {lowest * 1000:.1f} mm, path at {rest * 1000:.1f} mm, hole top {hole_top * 1000:.1f} mm")

bpy.ops.object.select_all(action="DESELECT")
pair.select_set(True)
bpy.ops.export_scene.gltf(filepath=f"{out_dir}/chain.glb", export_format="GLB", use_selection=True, export_yup=True)
bpy.ops.export_scene.gltf(filepath=f"{out_dir}/pendant_with_chain.glb", export_format="GLB", use_selection=False,
                          export_yup=True)

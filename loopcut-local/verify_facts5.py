"""Facts for the local skills from the 2026-11-08 eval failures (steel_material, gn_scatter), checked in Blender 5.2.2.
blender -b --factory-startup --python verify_facts5.py   (PATH without ~/.local/bin)
Prints FACT <name> OK|FAIL <detail>; every line must be OK before a fact goes into a skill."""
import sys
sys.dont_write_bytecode = True
import bpy

bad = 0


def fact(name, ok, detail: object = ""):
    global bad
    bad += not ok
    print(f"FACT {name} {'OK' if ok else 'FAIL'} {detail}")


def raises(fn):
    try:
        fn()
    except Exception as ex:  # noqa: BLE001
        return f"{type(ex).__name__}: {ex}"
    return ""


# --- materials
mat = bpy.data.materials.new("M")
mat.use_nodes = True
types = sorted(n.type for n in mat.node_tree.nodes)
fact("use_nodes_makes_principled_and_output", types == ["BSDF_PRINCIPLED", "OUTPUT_MATERIAL"], types)
mat.node_tree.nodes.clear()
fact("clear_removes_output_too", len(mat.node_tree.nodes) == 0)
nt = mat.node_tree
fact("new_principled_bl_idname", nt.nodes.new("ShaderNodeBsdfPrincipled").type == "BSDF_PRINCIPLED")
fact("new_output_bl_idname", nt.nodes.new("ShaderNodeOutputMaterial").type == "OUTPUT_MATERIAL")
err = raises(lambda: nt.nodes.new("ShaderNodeBSDF_PRINCIPLED"))
fact("wrong_case_idname_fails", "undefined" in err, err)
b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
b.inputs["Roughness"].default_value = 0.35
fact("roughness_unlinked_value", abs(b.inputs["Roughness"].default_value - 0.35) < 1e-6 and not b.inputs["Roughness"].is_linked)
fact("anisotropic_input_exists", "Anisotropic" in b.inputs, [s.name for s in b.inputs if "niso" in s.name])

# --- geometry nodes scatter
bpy.ops.mesh.primitive_plane_add(size=10)
ground = bpy.context.object
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.05, location=(0, 0, 3))
pebble = bpy.context.object
tree = bpy.data.node_groups.new("S", "GeometryNodeTree")
err = raises(lambda: setattr(tree, "nodes", None))
fact("tree_nodes_read_only", "read-only" in err, err)
tree.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
tree.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
n = tree.nodes
gin, gout = n.new("NodeGroupInput"), n.new("NodeGroupOutput")
dist = n.new("GeometryNodeDistributePointsOnFaces")
fact("distribute_methods", sorted(i.identifier for i in dist.bl_rna.properties["distribute_method"].enum_items)
     == ["POISSON", "RANDOM"])
fact("distribute_inputs", all(k in dist.inputs for k in ("Mesh", "Density", "Seed")), [s.name for s in dist.inputs])
fact("seed_is_int", dist.inputs["Seed"].bl_idname == "NodeSocketInt", dist.inputs["Seed"].bl_idname)
err = raises(lambda: setattr(dist.inputs["Mesh"], "default_value", 1))
fact("geometry_socket_has_no_default_value", "default_value" in err, err)
info = n.new("GeometryNodeObjectInfo")
inst = n.new("GeometryNodeInstanceOnPoints")
fact("instance_on_points_inputs", all(k in inst.inputs for k in ("Points", "Instance", "Rotation", "Scale")),
     [s.name for s in inst.inputs])
join = n.new("GeometryNodeJoinGeometry")
info.inputs["Object"].default_value = pebble
dist.inputs["Density"].default_value = 2.0    # 100 m2 plane
L = tree.links
L.new(gin.outputs[0], dist.inputs["Mesh"])
L.new(dist.outputs["Points"], inst.inputs["Points"])
L.new(info.outputs["Geometry"], inst.inputs["Instance"])
L.new(gin.outputs[0], join.inputs[0])
L.new(inst.outputs[0], join.inputs[0])
L.new(join.outputs[0], gout.inputs[0])
ground.modifiers.new("Scatter", "NODES").node_group = tree
err = raises(lambda: n.new("GeometryNodeRotateRotation"))
fact("rotate_rotation_name", bool(err), err or "exists")

counts = []
for seed in range(6):
    dist.inputs["Seed"].default_value = seed
    bpy.context.view_layer.update()
    g = ground.evaluated_get(bpy.context.evaluated_depsgraph_get()).evaluated_geometry()
    pc = g.instances_pointcloud()
    counts.append(len(pc.points) if pc else 0)
    refs = [getattr(r, "name", "") for r in g.instance_references()]
fact("count_via_evaluated_geometry", all(150 < c < 250 for c in counts), counts)
fact("refs_are_mesh_data_without_as_instance", refs == ["Icosphere"], refs)
# As Instance on Object Info does not change the reference name (still the mesh data's, 5.2.2)
fact("ground_mesh_kept_by_join", g.mesh is not None and len(g.mesh.polygons) >= 1)
# on a flat plane RANDOM gives density x area points for every seed (5.2.2)
fact("random_count_is_density_x_area_on_a_plane", set(counts) == {200}, counts)
dg = bpy.context.evaluated_depsgraph_get()
kept = [i for i in dg.object_instances if i.is_instance]
err = raises(lambda: kept[0].matrix_world)
fact("object_instances_invalid_after_loop", "removed" in err, err)
print("FACTS", "PASS" if bad == 0 else f"FAIL ({bad})")

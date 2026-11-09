"""Headless Blender 5.2: check every API claim a local skill makes, before it is written down."""
import bpy
R = []
def check(claim, ok): R.append((bool(ok), claim))
mat = bpy.data.materials.new("t"); mat.use_nodes = True
nodes = mat.node_tree.nodes
p = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
names = {s.name for s in p.inputs}
for n in ("Base Color", "Metallic", "Roughness", "Specular IOR Level", "Emission Color", "Emission Strength",
          "Transmission Weight", "Subsurface Weight", "Coat Weight", "Alpha", "Normal", "IOR"):
    check(f"Principled input '{n}'", n in names)
for old in ("Specular", "Emission", "Transmission", "Subsurface", "Clearcoat"):
    check(f"old Principled input '{old}' is GONE", old not in names)
check("output node type OUTPUT_MATERIAL", any(n.type == "OUTPUT_MATERIAL" for n in nodes))
check("Material.surface_render_method", hasattr(mat, "surface_render_method"))
check("Material.blend_method still present", hasattr(mat, "blend_method"))
me = bpy.data.meshes.new("m")
check("Mesh.use_auto_smooth is GONE", not hasattr(me, "use_auto_smooth"))
check("Mesh.color_attributes", hasattr(me, "color_attributes"))
check("Mesh.vertex_colors is GONE", not hasattr(me, "vertex_colors"))
check("Mesh.calc_normals_split is GONE", not hasattr(me, "calc_normals_split"))
check("Mesh.corner_normals", hasattr(me, "corner_normals"))
check("op object.shade_auto_smooth", hasattr(bpy.ops.object, "shade_auto_smooth"))
check("op object.shade_smooth_by_angle", hasattr(bpy.ops.object, "shade_smooth_by_angle"))
engines = [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
R.append((True, f"render engines (static enum): {engines}"))
act = bpy.data.actions.new("a")
check("Action.fcurves is GONE (5.x slotted actions)", not hasattr(act, "fcurves"))
check("Action.layers + Action.slots", hasattr(act, "layers") and hasattr(act, "slots"))
try:
    from bpy_extras import anim_utils
    check("bpy_extras.anim_utils.action_get_channelbag_for_slot", hasattr(anim_utils, "action_get_channelbag_for_slot"))
    check("bpy_extras.anim_utils.action_ensure_channelbag_for_slot", hasattr(anim_utils, "action_ensure_channelbag_for_slot"))
except Exception as ex:
    check(f"anim_utils import ({ex})", False)
gn = bpy.data.node_groups.new("g", "GeometryNodeTree")
check("NodeTree.interface.new_socket", hasattr(gn, "interface") and hasattr(gn.interface, "new_socket"))
check("NodeTree.inputs is GONE", not hasattr(gn, "inputs"))
check("op export_scene.gltf", hasattr(bpy.ops.export_scene, "gltf"))
check("op export_scene.fbx", hasattr(bpy.ops.export_scene, "fbx"))
fbx = bpy.ops.export_scene.fbx.get_rna_type().properties.keys()
for k in ("axis_forward", "axis_up", "global_scale", "apply_scale_options", "use_tspace", "mesh_smooth_type",
          "use_selection", "add_leaf_bones", "bake_anim", "path_mode", "embed_textures"):
    check(f"fbx export param {k}", k in fbx)
gl = bpy.ops.export_scene.gltf.get_rna_type().properties
check("gltf export_format GLB", "GLB" in [i.identifier for i in gl["export_format"].enum_items])
for k in ("use_selection", "export_apply", "export_yup", "export_image_format"):
    check(f"gltf export param {k}", k in gl.keys())
sc = bpy.context.scene
check("scene.eevee.use_ssr is GONE", not hasattr(sc.eevee, "use_ssr"))
check("scene.eevee.use_shadows", hasattr(sc.eevee, "use_shadows"))
check("Light.shadow_soft_size", hasattr(bpy.types.PointLight.bl_rna.properties, "get") and
      "shadow_soft_size" in bpy.types.PointLight.bl_rna.properties.keys())
check("op object.bake", hasattr(bpy.ops.object, "bake"))
bake_types = [i.identifier for i in bpy.types.BakeSettings.bl_rna.properties["normal_space"].enum_items]
R.append((True, f"bake normal_space: {bake_types}"))
check("op mesh.primitive_cube_add", hasattr(bpy.ops.mesh, "primitive_cube_add"))
check("Object.modifiers.new WELD type", "WELD" in [i.identifier for i in bpy.types.Modifier.bl_rna.properties["type"].enum_items])
check("modifier DECIMATE", "DECIMATE" in [i.identifier for i in bpy.types.Modifier.bl_rna.properties["type"].enum_items])
check("bpy.app.version", True); R.append((True, f"version {bpy.app.version_string}"))
for ok, claim in R:
    print(("OK   " if ok else "FAIL ") + claim)

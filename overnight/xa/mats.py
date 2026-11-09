import bpy, sys
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=sys.argv[sys.argv.index("--") + 1])
for m in bpy.data.materials:
    if not m.use_nodes: continue
    s = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not s: continue
    print("MAT", m.name, {k: ("LINK" if s.inputs[k].is_linked else (round(s.inputs[k].default_value, 3) if isinstance(s.inputs[k].default_value, float) else tuple(round(x, 3) for x in s.inputs[k].default_value)))
                         for k in ("Base Color", "Roughness", "Metallic", "Alpha", "Emission Color", "Emission Strength", "Normal")})

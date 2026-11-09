import bpy
for o in bpy.data.objects:
    if o.type != "MESH" or "LOD" not in o.name: continue
    for m in o.data.materials:
        for n in m.node_tree.nodes:
            if n.type == "NORMAL_MAP":
                src = n.inputs["Color"].links[0].from_node
                im = src.image
                print("BINFO", o.name, m.name, im.name, im.filepath, bool(im.packed_file), im.colorspace_settings.name, list(im.size), "uvmap", n.uv_map, "tex vector linked", src.inputs["Vector"].is_linked)
    print("BINFO uv layers", o.name, [l.name for l in o.data.uv_layers], "active render", [l.name for l in o.data.uv_layers if l.active_render])

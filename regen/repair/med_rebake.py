"""Re-bake each LOD's tangent normal map from the asset .blend's ApprovedHigh after deleting the medallion's
back skin: every face facing the body (normal.y > 0) inside the disc cylinder at the front of the cuirass. Bake rays
come from the front, so such faces there can only be wrong hits (the skin pair is coincident to <1e-6 at 83% of points).
Also bakes AO per LOD (16 samples, clean high visible), like asset_bake.
Settings mirror asset_bake.project_channel for component 0 (diagonal 1.3225: cage 1%, reach 5%, CPU, 1 sample).
blender -b --factory-startup asset.blend --python med_rebake.py -- out_dir   -> out_dir/rebake_lodN.npy, ao_lodN.npy (T,T,4 float)"""
import sys
sys.dont_write_bytecode = True
import bpy, bmesh
import numpy as np

out = sys.argv[sys.argv.index("--") + 1]
SIZE = 0.9809634635457769
DISC_X, DISC_Z = 0.00032653 - 0.00016655, 0.48939252 + 0.165 * SIZE - 0.00627856
R_DEL, FRONT_Y = 0.13 * SIZE, -0.15
DIAG, CAGE, REACH, MARGIN_PX, TEX = 1.322476605440983, 0.01, 0.05, 4.0, 2048
name = "vampire_chestplate_v3_lc"

high = bpy.data.objects["ApprovedHigh"]
assert abs(high.matrix_world.determinant() - 1) < 1e-6 and high.matrix_world.translation.length < 1e-9
bm = bmesh.new(); bm.from_mesh(high.data); bm.normal_update(); bm.faces.ensure_lookup_table()
doomed = []
for f in bm.faces:
    c = f.calc_center_median()
    if f.normal.y <= 0 or c.y >= FRONT_Y or (c.x - DISC_X) ** 2 + (c.z - DISC_Z) ** 2 >= R_DEL ** 2:
        continue
    doomed.append(f)
print("REBAKE high faces", len(bm.faces), "deleted back-skin faces", len(doomed), flush=True)
bmesh.ops.delete(bm, geom=doomed, context="FACES")
clean = bpy.data.meshes.new("HighClean"); bm.to_mesh(clean)
src = bpy.data.objects.new("HighClean", clean); bpy.context.scene.collection.objects.link(src)
# the clean high keeps ApprovedHigh's materials and smooth-shading flags via to_mesh

scene = bpy.context.scene
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = 1
for o in scene.objects:
    o.hide_render = True
    o.hide_set(True)
    o.select_set(False)
for k in range(4):
    low = bpy.data.objects[f"{name}_LOD{k}"]
    T = TEX // (2 ** k)
    img = bpy.data.images.new(f"rebake{k}", T, T, alpha=True, float_buffer=True)
    img.colorspace_settings.name = "Non-Color"
    mat = low.data.materials[0]
    node = mat.node_tree.nodes.new("ShaderNodeTexImage"); node.image = img
    mat.node_tree.nodes.active = node
    for o in (low, src):
        o.hide_set(False); o.hide_render = False
    bpy.ops.object.select_all(action="DESELECT")
    src.select_set(True); low.select_set(True); bpy.context.view_layer.objects.active = low
    low.data.uv_layers["GameUV"].active = True; low.data.uv_layers["GameUV"].active_render = True
    scene.render.bake.margin = max(0, int(MARGIN_PX * T / TEX / 2))
    bpy.ops.object.bake(type="NORMAL", use_selected_to_active=True, use_clear=True, use_cage=True,
                        cage_extrusion=DIAG * CAGE, max_ray_distance=DIAG * REACH, normal_space="TANGENT",
                        uv_layer="GameUV")
    px = np.empty(T * T * 4, np.float32); img.pixels.foreach_get(px)
    np.save(f"{out}/rebake_lod{k}.npy", px.reshape(T, T, 4)[::-1])   # row 0 = top, like PIL
    img_ao = bpy.data.images.new(f"rebake_ao{k}", T, T, alpha=True, float_buffer=True)
    img_ao.colorspace_settings.name = "Non-Color"
    node.image = img_ao
    scene.cycles.samples = 16
    bpy.ops.object.bake(type="AO", use_selected_to_active=True, use_clear=True, use_cage=True,
                        cage_extrusion=DIAG * CAGE, max_ray_distance=DIAG * REACH, normal_space="TANGENT",
                        uv_layer="GameUV")
    scene.cycles.samples = 1
    img_ao.pixels.foreach_get(px)
    np.save(f"{out}/ao_lod{k}.npy", px.reshape(T, T, 4)[::-1])
    mat.node_tree.nodes.remove(node)
    low.hide_set(True); low.hide_render = True
    print("REBAKE lod", k, T, flush=True)

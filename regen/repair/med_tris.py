"""Dump each LOD GLB's triangles (UV0 corners, 3D corners, face normal) in the Blender import frame.
blender -b --factory-startup --python med_tris.py -- out_dir lod0.glb [lod1.glb ...]  -> out_dir/tris_lodN.npz"""
import sys
sys.dont_write_bytecode = True
import bpy
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
out, paths = argv[0], argv[1:]
for k, path in enumerate(paths):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)
    objs = [o for o in bpy.data.objects if o.type == "MESH"]
    assert len(objs) == 1, objs
    o = objs[0]
    me = o.data
    me.transform(o.matrix_world)
    me.calc_loop_triangles()
    assert len(me.uv_layers) == 1, [l.name for l in me.uv_layers]
    n = len(me.loop_triangles)
    loops = np.empty(n * 3, np.int32); me.loop_triangles.foreach_get("loops", loops)
    verts = np.empty(n * 3, np.int32); me.loop_triangles.foreach_get("vertices", verts)
    nrm = np.empty(n * 3, np.float32); me.loop_triangles.foreach_get("normal", nrm)
    uv = np.empty(len(me.loops) * 2, np.float32); me.uv_layers[0].data.foreach_get("uv", uv)
    co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get("co", co)
    uv, co = uv.reshape(-1, 2), co.reshape(-1, 3)
    np.savez(f"{out}/tris_lod{k}.npz", uv=uv[loops].reshape(n, 3, 2), pos=co[verts].reshape(n, 3, 3),
             normal=nrm.reshape(n, 3), bbox=np.stack([co.min(0), co.max(0)]))
    print("TRIS", k, n, "bbox", co.min(0), co.max(0), flush=True)

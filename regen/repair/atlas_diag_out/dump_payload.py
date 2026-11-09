import sys, io
sys.dont_write_bytecode = True
import bpy, bmesh, numpy as np
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=sys.argv[sys.argv.index("--") + 1])
o = next(x for x in bpy.context.scene.objects if x.type == "MESH")
bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.triangulate(bm, faces=bm.faces[:]); bm.to_mesh(o.data); bm.free()
m = o.data
p = np.empty(len(m.vertices) * 3, np.float32); m.vertices.foreach_get("co", p)
t = np.empty(len(m.loops), np.uint32); m.loops.foreach_get("vertex_index", t)
np.savez(sys.argv[-1], positions=p.reshape(-1, 3), triangles=t.reshape(-1, 3))
print("DUMP", len(t) // 3)

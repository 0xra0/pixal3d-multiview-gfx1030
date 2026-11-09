import sys, bpy
path = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=path)
import numpy as np
cs = []
for o in [o for o in bpy.data.objects if o.type == "MESH"]:
    me = o.data; mw = np.array(o.matrix_world)
    c = np.zeros(len(me.polygons) * 3); me.polygons.foreach_get("center", c); c = c.reshape(-1, 3)
    c = c @ mw[:3, :3].T + mw[:3, 3]; cs.append(c)
c = np.concatenate(cs); z = c[:, 2]; y = c[:, 1]
mid = (z.min() + z.max()) / 2; ymid = y.min() + 0.45 * (y.max() - y.min())
print("faces on -Z half", int((z < mid).sum()), " +Z half", int((z >= mid).sum()))
sel = y < ymid
print("lower 45% only: -Z", int((z[sel] < mid).sum()), " +Z", int((z[sel] >= mid).sum()))

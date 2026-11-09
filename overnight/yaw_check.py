import sys
sys.path.insert(0, "/mnt/ssd/work/pixal3d-mv")
import numpy as np, prep_mesh as prep
a, b = sys.argv[sys.argv.index("--") + 1:]
def verts(src, yaw):
    obj = prep.import_mesh(src, yaw=yaw)
    co = np.empty(len(obj.data.vertices) * 3); obj.data.vertices.foreach_get("co", co)
    return (np.array(obj.matrix_world) @ np.c_[co.reshape(-1, 3), np.ones(len(co) // 3)].T).T[:, :3]
v_yaw, v_rot = verts(a, 180), verts(b, 0)
print("YAWCHECK counts", len(v_yaw), len(v_rot))
print("YAWCHECK bounds yaw180", np.round([v_yaw.min(0), v_yaw.max(0)], 4).tolist())
print("YAWCHECK bounds rot180", np.round([v_rot.min(0), v_rot.max(0)], 4).tolist())
print("YAWCHECK max vertex diff", float(np.abs(np.sort(v_yaw, 0) - np.sort(v_rot, 0)).max()))

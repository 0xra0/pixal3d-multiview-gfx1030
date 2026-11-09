import sys, numpy as np, trimesh, open3d as o3d
def load(p):
    m = trimesh.load(p, force="mesh", process=False); return np.asarray(m.vertices, float), np.asarray(m.faces, np.int64)
d, name = sys.argv[1], sys.argv[2]
v0, f0 = load(f"{d}/{name}_LOD0.glb"); fn0 = trimesh.Trimesh(v0, f0, process=False).face_normals
scene = o3d.t.geometry.RaycastingScene()
scene.add_triangles(o3d.core.Tensor(v0.astype(np.float32)), o3d.core.Tensor(f0.astype(np.uint32)))
for lod in (1, 2, 3):
    t = trimesh.Trimesh(*load(f"{d}/{name}_LOD{lod}.glb"), process=False)
    ids = scene.compute_closest_points(o3d.core.Tensor(t.triangles_center.astype(np.float32)))["primitive_ids"].numpy()
    bad = (t.face_normals * fn0[ids]).sum(1) < 0
    print(f"LOD{lod} faces {len(t.faces):6d} folds {100 * t.area_faces[bad].sum() / t.area_faces.sum():5.1f}%")

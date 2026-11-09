import sys, numpy as np, trimesh, pymeshlab, open3d as o3d
src, lod2 = sys.argv[1], sys.argv[2]
def load(p):
    m = trimesh.load(p, force="mesh", process=False); return np.asarray(m.vertices,float), np.asarray(m.faces,np.int64)
v0, f0 = load(src)
fn0 = trimesh.Trimesh(v0, f0, process=False).face_normals
scene = o3d.t.geometry.RaycastingScene()
scene.add_triangles(o3d.core.Tensor(v0.astype(np.float32)), o3d.core.Tensor(f0.astype(np.uint32)))
def folds(v, f, tag):
    t = trimesh.Trimesh(v, f, process=False)
    q = scene.compute_closest_points(o3d.core.Tensor(t.triangles_center.astype(np.float32)))
    ids = q["primitive_ids"].numpy()
    bad = (t.face_normals * fn0[ids]).sum(1) < 0
    a = t.area_faces
    print(f"{tag:28s} faces {len(f):6d} reversed {100*bad.mean():5.1f}%  area {100*a[bad].sum()/a.sum():5.1f}%", flush=True)
folds(*load(lod2), "current LOD2 (Blender)")
target = len(load(lod2)[1])
for pn in (False, True):
    ms = pymeshlab.MeshSet(); ms.add_mesh(pymeshlab.Mesh(v0, f0))
    ms.meshing_decimation_quadric_edge_collapse(targetfacenum=target, preservenormal=pn, preservetopology=True,
                                                 planarquadric=True, qualitythr=0.3, optimalplacement=True)
    m = ms.current_mesh(); folds(m.vertex_matrix(), m.face_matrix(), f"meshlab preservenormal={pn}")

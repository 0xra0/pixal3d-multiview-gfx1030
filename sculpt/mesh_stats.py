import sys, numpy as np, trimesh
m = trimesh.load(sys.argv[1], force="mesh", process=False)
m.merge_vertices()
e = m.edges_sorted; u, c = np.unique(e, axis=0, return_counts=True)
L = m.edges_unique_length
comp = m.split(only_watertight=False)
sizes = sorted((len(x.faces) for x in comp), reverse=True)
print(f"faces={len(m.faces)} verts={len(m.vertices)} watertight={m.is_watertight}")
print(f"boundary_edges={(c==1).sum()} nonmanifold_edges={(c>2).sum()} components={len(comp)} tiny(<100f)={sum(s<100 for s in sizes)} top={sizes[:4]}")
print(f"edge_len cv={L.std()/L.mean():.2f} max/median={L.max()/np.median(L):.1f} degenerate={(m.area_faces<1e-12).sum()} bbox={np.ptp(m.bounds,axis=0).round(3)}")
if len(sys.argv) > 2:
    ref = trimesh.load(sys.argv[2], force="mesh", process=False)
    p, _ = trimesh.sample.sample_surface(ref, 20000, seed=0)
    from scipy.spatial import cKDTree; d = cKDTree(trimesh.sample.sample_surface(m, 2000000, seed=1)[0]).query(p)[0]
    diag = np.linalg.norm(np.ptp(ref.bounds, axis=0))
    print(f"shape drift vs ref: mean={d.mean()/diag*100:.3f}% p99={np.percentile(d,99)/diag*100:.3f}% of diagonal")

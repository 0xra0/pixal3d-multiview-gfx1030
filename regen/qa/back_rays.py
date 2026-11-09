"""Rays from behind through a raw Pixal3D GLB (file coords: front camera at +Y, up -Z): surfaces crossed per ray.
A closed torso shell gives ~4 (back outer/inner, front inner/outer); an open back gives ~2."""
import sys, numpy as np, trimesh
m = trimesh.load(sys.argv[1], force="mesh", process=False)
lo, hi = m.bounds
xs = np.linspace(lo[0], hi[0], 41)[8:-8]; zs = np.linspace(lo[2], hi[2], 41)[8:-8]
o = np.array([[x, lo[1] - 1, z] for x in xs for z in zs]); d = np.tile([0, 1, 0], (len(o), 1))
loc, idx, _ = m.ray.intersects_location(o, d, multiple_hits=True)
hits = np.bincount(idx, minlength=len(o))
first_y = np.full(len(o), np.nan)
for r in range(len(o)):
    ys = loc[idx == r][:, 1]
    if len(ys): first_y[r] = ys.min()
print(sys.argv[1].split("/")[-1], "faces", len(m.faces), "bounds y", lo[1].round(3), hi[1].round(3))
print("hits per central ray: ", {k: int(v) for k, v in zip(*np.unique(hits, return_counts=True))})
print("first hit depth from back, as share of y-span: median %.2f" % np.nanmedian((first_y - lo[1]) / (hi[1] - lo[1])))

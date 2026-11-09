"""Repair cuirass 00004 by moving vertices only (no booleans, CPU):
  1. the ribbed ball on the chest -> a flat medallion disc with a raised rim, on the chest plane
  2. the web relief on the lower back -> smooth plate (the reference back is plain), seam kept
python repair_cuirass.py in.glb out.glb
Raw-GLB axes: up is -Z, front is +Y, the object's left is +X (mesh_judge.EYE)."""
import sys
import numpy as np
import trimesh
from trimesh.smoothing import filter_taubin

src, out = sys.argv[1], sys.argv[2]
ITER = int(sys.argv[3]) if len(sys.argv) > 3 else 600
m = trimesh.load(src, force="mesh", process=False)
m.remove_unreferenced_vertices()   # isolated vertices make the Taubin Laplacian divide by zero (NaN)
v = np.asarray(m.vertices, float).copy()
x, y, z = v[:, 0], v[:, 1], v[:, 2]

def ramp(t):                      # 0 below 0, 1 above 1, smoothstep between
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)

# --- 1. medallion disc ------------------------------------------------------------------------
CX, CZ, R = 0.0, -0.165, 0.105    # measured from the front relief map
r = np.hypot(x - CX, z - CZ)
front = y > 0.12
ann = front & (r > 1.15 * R) & (r < 1.45 * R)
# the outer layer of the annulus: top 60% of Y there (the inner shell surface sits lower)
ann &= y > np.percentile(y[ann], 40)
A = np.c_[np.ones(ann.sum()), x[ann], z[ann]]
coef, *_ = np.linalg.lstsq(A, y[ann], rcond=None)
plane = coef[0] + coef[1] * x + coef[2] * z
print(f"chest plane at centre Y {coef[0] + coef[2] * CZ:.4f}; shell layers near the disc: "
      f"outer {np.percentile(y[ann], 50):.4f}")
ball = front & (r < R + 0.015) & (y > plane - 0.006)
print(f"ball vertices {ball.sum()}, max rise above the plane {1000 * (y[ball] - plane[ball]).max():.1f} mm")
face = plane + 0.010                                     # disc face 10 mm proud of the chest
rim = 0.005 * ramp((r - 0.80 * R) / (0.06 * R)) * (1 - ramp((r - 0.97 * R) / (0.03 * R)))
target = face + rim
blend = 1 - ramp((r - R) / 0.015)                        # 1 inside, 0 at R + 15 mm
y_new = y.copy()
y_new[ball] = blend[ball] * target[ball] + (1 - blend[ball]) * np.minimum(y[ball], plane[ball] + 0.002)
v[:, 1] = y_new

# --- 2. lower back ----------------------------------------------------------------------------
# The shell is ~1.5 mm thick and BOTH layers follow the web relief: raised terraces 1-3 mm high with step
# edges plus narrow peaks (cross-section at z = 0.12). Smoothing keeps a plateau's height and clamping
# only the outer layer lets the inner one poke through, so both layers move together by one field:
# D = smooth base - outer height, from the outer height map along -Y. The base is a 25 mm grey opening
# (drops the narrow peaks) blurred over ~4 cm (turns 1-3 mm steps into invisible slopes). The centre seam
# rides on the opened field, so it is kept.
from scipy import ndimage
x, y, z = v[:, 0], v[:, 1], v[:, 2]
ST, X0, Z0 = 0.005, -0.40, -0.52
ix = np.clip(((x - X0) / ST).astype(int), 0, 159)
iz = np.clip(((z - Z0) / ST).astype(int), 0, 209)
Hb = np.full((210, 160), -np.inf)
np.maximum.at(Hb, (iz, ix), -y)
have = np.isfinite(Hb) & (Hb > 0)
F = Hb[tuple(ndimage.distance_transform_edt(~have, return_distances=False, return_indices=True))]
O = ndimage.grey_opening(F, size=(5, 5))
G = ndimage.gaussian_filter(O, 8.0)
seam = (np.abs(np.arange(160) * ST + X0 + ST / 2) < 0.012)[None, :]
D = ndimage.gaussian_filter(np.where(seam, 0.0, O - F), 1.0)   # narrow features only: plate edges (x = +-0.14, a 12-15 mm drop) are real
gz, gx = np.gradient(G, ST)
flat = 1 - ramp((np.hypot(gx, gz) - 0.9) / 0.5)          # the Y height map is meaningless on steep sides
fx, fz = (x - X0) / ST - 0.5, (z - Z0) / ST - 0.5
at = lambda grid: ndimage.map_coordinates(grid, [fz, fx], order=1, mode="nearest")
w = (ramp((z + 0.13) / 0.04)                 # from under the shoulder blades (z = -0.09) down ...
     * (1 - ramp((z - 0.27) / 0.04))         # ... to just above the bottom flare
     * ramp((-y - 0.06) / 0.04)              # back half only
     * at(flat))
d = at(D) * w
print(f"back: {(w > 0.5).sum()} vertices, displacement mean {1000 * np.abs(d[w > 0.5]).mean():.2f} mm, "
      f"range {1000 * d.min():.1f} .. {1000 * d.max():.1f} mm")
v[:, 1] = y - d

# a light relax of the disc border so the collapsed ball walls do not leave slivers
relax = trimesh.Trimesh(v.copy(), m.faces, process=False)
filter_taubin(relax, lamb=0.5, nu=0.53, iterations=6)
x, y, z = v[:, 0], v[:, 1], v[:, 2]
r = np.hypot(x - CX, z - CZ)
wr = ((r > 0.9 * R) & (r < R + 0.02) & front).astype(float)[:, None]
v = v + wr * (np.asarray(relax.vertices) - v)

assert np.isfinite(v).all(), "NaN vertices"
trimesh.Trimesh(v, m.faces, process=False).export(out)
print("wrote", out)

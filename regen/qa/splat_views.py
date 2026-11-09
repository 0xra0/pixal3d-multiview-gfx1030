"""CPU-only look at a raw GLB: orthographic depth-shaded splats along +-X and +-Z (glTF Y up). No GPU."""
import sys, numpy as np, trimesh
from PIL import Image
mesh = trimesh.load(sys.argv[1], force="mesh")
pts, _ = trimesh.sample.sample_surface(mesh, 1_500_000, seed=1)
lo, hi = pts.min(0), pts.max(0); s = 500 / (hi - lo).max()
tiles = []
for axis, sign in ((1, 1), (0, 1), (1, -1), (0, -1)):        # Z up (trimesh GLB): view along Y and X
    u = 0 if axis == 1 else 1
    x = ((pts[:, u] - lo[u]) * s * (sign if axis == 1 else -sign)); x -= x.min()
    y = (hi[2] - pts[:, 2]) * s
    d = pts[:, axis] * sign
    img = np.zeros((512, 512)); depth = np.full((512, 512), -np.inf)
    xi, yi = np.clip(x.astype(int) + 6, 0, 511), np.clip(y.astype(int) + 6, 0, 511)
    order = np.argsort(d); np.maximum.at(depth, (yi[order], xi[order]), d[order])
    m = np.isfinite(depth); dn = depth.copy(); dn[m] = (dn[m] - dn[m].min()) / (np.ptp(dn[m]) + 1e-9)
    img[m] = 60 + 195 * dn[m]; tiles.append(img)
Image.fromarray(np.hstack(tiles).astype(np.uint8)).save(sys.argv[2])
print("extent", hi - lo, "components", len(mesh.split(only_watertight=False)) if len(mesh.faces) < 400000 else "?")

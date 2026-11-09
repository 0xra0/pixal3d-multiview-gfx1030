"""Clay renders of pendant_with_chain.glb (Y-up glTF) with mesh_judge.clay: full front/left and bail close-ups."""
import sys
import numpy as np, trimesh
from PIL import Image
sys.path.insert(0, "/mnt/ssd/work/pixal3d-mv")
from mesh_judge import clay
d = sys.argv[1]
m = trimesh.load(f"{d}/pendant_with_chain.glb", force="mesh", process=False)
G = np.asarray(m.vertices, float); F = np.asarray(m.faces)
R = np.stack([G[:, 0], G[:, 2], -G[:, 1]], 1)          # glTF Y-up -> raw-GLB frame (up -Z, front camera at +Y)
tiles = [clay(R, F, v, 768) for v in ("front", "left")]
# close-up: keep faces whose centre is within 9 mm of the bail top (raw z = -73 mm)
c = R[F].mean(1); keep = np.linalg.norm(c - np.array([0, 0, -0.071]), axis=1) < 0.009
used, sub = np.unique(F[keep], return_inverse=True)   # re-index so the close-up frames only the bail
tiles += [clay(R[used], sub.reshape(-1, 3), v, 768) for v in ("front", "left", "back")]
out = Image.new("L", (768 * len(tiles), 768))
for i, t in enumerate(tiles): out.paste(t, (768 * i, 0))
out.save(f"{d}/compare_v2.png"); print(f"{d}/compare_v2.png", keep.sum(), "faces in close-up")

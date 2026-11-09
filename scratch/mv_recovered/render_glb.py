import sys, numpy as np, trimesh
from PIL import Image
m = trimesh.load(sys.argv[1], force='mesh')
V = m.vertices - m.bounds.mean(0); F = m.faces
C = m.visual.vertex_colors[:, :3].astype(float) if m.visual.kind == 'vertex' else np.full((len(V), 3), 180.)
N = m.face_normals
H = 900
def view(R, shade):
    P = V @ R.T; tri = P[F]; cen = tri.mean(1); n = N @ R.T
    lam = np.abs(n[:, 2]) * 0.75 + 0.25
    col = (C[F].mean(1) if not shade else np.full((len(F), 3), 200.)) * lam[:, None]
    s = (H - 40) / (P[:, 1].max() - P[:, 1].min())
    W = int((P[:, 0].max() - P[:, 0].min()) * s) + 40
    img = np.full((H, W, 3), 255.); zb = np.full((H, W), -1e9)
    # splat each triangle via 6 barycentric samples + centroid (dense mesh, fine at this size)
    bs = np.array([[1,1,1],[4,1,1],[1,4,1],[1,1,4],[2,2,1],[1,2,2],[2,1,2]], float); bs /= bs.sum(1, keepdims=True)
    for b in bs:
        p = np.einsum('k,fkj->fj', b, tri)
        x = ((p[:, 0] - P[:, 0].min()) * s + 20).astype(int); y = (H - 20 - (p[:, 1] - P[:, 1].min()) * s).astype(int)
        o = np.argsort(p[:, 2]); x, y, z, c = x[o], y[o], p[o, 2], col[o]
        ok = (x >= 0) & (x < W) & (y >= 0) & (y < H)
        img[y[ok], x[ok]] = c[ok]
    return img.clip(0, 255).astype(np.uint8)
def rot(ax, deg):
    a = np.radians(deg); c, s_ = np.cos(a), np.sin(a)
    return {'y': np.array([[c,0,s_],[0,1,0],[-s_,0,c]])}[ax]
# GLB is Y-up; long axis was z in trimesh extents -> rotate so the long axis is screen-up
ext = m.extents; long = int(np.argmax(ext))
base = np.eye(3)
if long == 2: base = np.array([[1,0,0],[0,0,1],[0,-1,0]])  # z -> up
elif long == 0: base = np.array([[0,1,0],[1,0,0],[0,0,1]])
panels = []
for deg in (0, 90, 35):
    R = rot('y', deg) @ base
    panels += [view(R, False), view(R, True)]
Wt = sum(p.shape[1] for p in panels) + 10 * len(panels)
out = np.full((H, Wt, 3), 255, np.uint8); x = 0
for p in panels: out[:, x:x + p.shape[1]] = p; x += p.shape[1] + 10
Image.fromarray(out).save(sys.argv[2]); print(out.shape)

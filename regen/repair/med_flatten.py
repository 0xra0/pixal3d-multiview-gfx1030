"""Flatten the cuirass medallion disc in each LOD's GL and DX normal maps (the high-poly disc is a zero-thickness
double layer, so its bake picked front or back skin at random). usage:
python3 -I med_flatten.py <tris_dir> <base_textures_dir> <out_textures_dir> [--rebake DIR] [--dry]
With --rebake the disc takes DIR/rebake_lodN.npy (med_rebake.py, back skin removed) instead of flat normals.
Texels whose surface point lies inside the disc cylinder (front-facing, front of the cuirass) blend to flat
(0,0,1): full inside R_FULL, linear to the baked value at R_OUT. Bake padding outside the UV islands follows the
weight of its nearest covered texel."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

# Disc axis (along Y) in the LOD0 GLB import frame, fitted from the front-view ray grid (med_diag.py): grid centre
# (c.x, c.z + 0.165 size) plus the fitted offset (-0.00017, -0.00628). size = LOD0 bbox max extent.
SIZE = 0.9809634635457769
DISC_X = 0.00032653 - 0.00016655
DISC_Z = 0.48939252 + 0.165 * SIZE - 0.00627856
R_FULL, R_OUT = 0.113 * SIZE, 0.120 * SIZE   # double layer ends ~0.110*size; bezel starts beyond
FRONT_Y = -0.15                              # disc dome sits at y -0.19..-0.25; the back plate is at y > 0
PAD_PX = 16

tris_dir, base_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
dry = "--dry" in sys.argv
rebake_dir = Path(sys.argv[sys.argv.index("--rebake") + 1]) if "--rebake" in sys.argv else None
for k in range(4):
    t = np.load(tris_dir / f"tris_lod{k}.npz")
    uv, pos, nrm = t["uv"].astype(np.float64), t["pos"].astype(np.float64), t["normal"]
    gl = np.asarray(Image.open(base_dir / f"lod{k}/normal_lod0.png")).copy()
    dx = np.asarray(Image.open(base_dir / f"lod{k}/normal_dx_lod0.png")).copy()
    gl_path, dx_path = out_dir / f"lod{k}/normal_lod0.png", out_dir / f"lod{k}/normal_dx_lod0.png"
    T = gl.shape[0]
    assert gl.shape == dx.shape == (T, T, 4)
    covered = np.zeros((T, T), bool); weight = np.zeros((T, T))
    px = uv[..., 0] * T - 0.5; py = (1 - uv[..., 1]) * T - 0.5   # texel-centre coordinates, row 0 = top (v = 1)
    near = np.hypot(pos[..., 0].mean(1) - DISC_X, pos[..., 2].mean(1) - DISC_Z) < R_OUT + 0.05 * SIZE
    for i in range(len(uv)):
        x0, x1 = int(np.floor(px[i].min())), int(np.ceil(px[i].max()))
        y0, y1 = int(np.floor(py[i].min())), int(np.ceil(py[i].max()))
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, T - 1), min(y1, T - 1)
        if x1 < x0 or y1 < y0:
            continue
        gy, gx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
        (ax, bx, cx), (ay, by, cy) = px[i], py[i]
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-12:
            continue
        l0 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
        l1 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
        l2 = 1 - l0 - l1
        inside = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
        covered[gy[inside], gx[inside]] = True
        if not near[i] or nrm[i, 1] >= 0:
            continue
        p = l0[..., None] * pos[i, 0] + l1[..., None] * pos[i, 1] + l2[..., None] * pos[i, 2]
        r = np.hypot(p[..., 0] - DISC_X, p[..., 2] - DISC_Z)
        w = np.clip((R_OUT - r) / (R_OUT - R_FULL), 0, 1) * (p[..., 1] < FRONT_Y)
        sel = inside & (w > 0)
        weight[gy[sel], gx[sel]] = np.maximum(weight[gy[sel], gx[sel]], w[sel])
    # bake padding: uncovered texels take the weight of the nearest covered texel within PAD_PX
    dist, (iy, ix) = ndimage.distance_transform_edt(~covered, return_indices=True)
    pad = ~covered & (dist <= PAD_PX)
    weight[pad] = weight[iy[pad], ix[pad]]
    m = weight > 0
    n_old = gl[m, :3].astype(np.float64) / 255 * 2 - 1
    w = weight[m][:, None]
    if rebake_dir:
        rb = np.load(rebake_dir / f"rebake_lod{k}.npy")[..., :3].astype(np.float64) * 2 - 1
        rb = np.where(covered[..., None], rb, rb[iy, ix])          # padding: nearest covered texel
        orig = gl[..., :3].astype(np.float64) / 255 * 2 - 1
        out_disc = covered & (weight == 0)
        dev = np.degrees(np.arccos(np.clip((rb[out_disc] * orig[out_disc]).sum(1) / np.linalg.norm(rb[out_disc], axis=1)
                                           / np.linalg.norm(orig[out_disc], axis=1), -1, 1)))
        print(f"FLAT lod{k} rebake vs original outside disc: angle p50 {np.percentile(dev, 50):.2f} p90 "
              f"{np.percentile(dev, 90):.2f} p99 {np.percentile(dev, 99):.2f} deg; rebake disc z<0.6 "
              f"{(rb[covered & (weight >= 1)][:, 2] < 0.6).mean():.3f} (original {(orig[covered & (weight >= 1)][:, 2] < 0.6).mean():.3f})")
        target = rb[m]
    else:
        target = np.array([0, 0, 1.0])
    n_new = n_old * (1 - w) + target * w
    n_new /= np.linalg.norm(n_new, axis=1, keepdims=True)
    enc = np.clip(np.round((n_new + 1) / 2 * 255), 0, 255).astype(np.uint8)
    if not rebake_dir:
        enc[weight[m] >= 1] = (128, 128, 255)   # exactly the bake's flat value
    before_bad = (n_old[:, 2] < 0.6).mean()
    gl[m, :3] = enc
    dx[m, :3] = enc
    dx[m, 1] = 255 - enc[:, 1]
    print(f"FLAT lod{k} {T}px covered {covered.mean():.3f}; texels changed {m.sum()} (full {(weight >= 1).sum()}, "
          f"padding {(m & pad).sum()}); of them baked z<0.6 before: {before_bad:.2f}")
    if rebake_dir:   # AO was baked through the same double layer: same mask, scalar blend; orm.png R == ao.png
        ao = np.asarray(Image.open(base_dir / f"lod{k}/ao.png")).copy()
        orm = np.asarray(Image.open(base_dir / f"lod{k}/orm.png")).copy()
        new = np.load(rebake_dir / f"ao_lod{k}.npy")[..., 0].astype(np.float64)
        new = np.where(covered, new, new[iy, ix])
        val = np.clip(np.round((ao[m, 0] / 255 * (1 - w[:, 0]) + new[m] * w[:, 0]) * 255), 0, 255).astype(np.uint8)
        print(f"FLAT lod{k} AO disc mean {ao[m & (weight >= 1), 0].mean() / 255:.3f} -> {val[weight[m] >= 1].mean() / 255:.3f}")
        ao[m, 0] = ao[m, 1] = ao[m, 2] = val
        orm[m, 0] = val
    if not dry:
        Image.fromarray(gl).save(gl_path)
        Image.fromarray(dx).save(dx_path)
        if rebake_dir:
            Image.fromarray(ao).save(out_dir / f"lod{k}/ao.png")
            Image.fromarray(orm).save(out_dir / f"lod{k}/orm.png")
        Image.fromarray((weight * 255).astype(np.uint8)).save(tris_dir / f"mask_lod{k}.png")

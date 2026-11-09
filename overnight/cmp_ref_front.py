"""Reference front vs generated UltraTex views: side-by-side image plus a horizontal-band score.

Band score = vertical-gradient energy / horizontal-gradient energy inside the object mask.
Horizontal stripes raise d/dy without raising d/dx, so a striped image scores well above 1.
"""
import sys
import numpy as np
from PIL import Image

def load_grey(img):
    rgba = np.asarray(img.convert("RGBA"), dtype=np.float32) / 255
    lum = rgba[..., :3] @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    # Object mask: alpha if present, else anything not near-white / near-uniform background.
    mask = rgba[..., 3] > 0.5
    if mask.all():
        bg = np.median(np.concatenate([lum[0], lum[-1], lum[:, 0], lum[:, -1]]))
        mask = np.abs(lum - bg) > 0.04
    return lum, mask


def band_score(img):
    lum, mask = load_grey(img)
    dy = np.abs(np.diff(lum, axis=0))[:, :-1]
    dx = np.abs(np.diff(lum, axis=1))[:-1, :]
    m = mask[1:, 1:] & mask[:-1, :-1]
    return float((dy[m] ** 2).mean() / max((dx[m] ** 2).mean(), 1e-9)), float(m.mean())


if __name__ == "__main__":
    ref_path, views_path, normals_path, out_path = sys.argv[1:5]
    ref = Image.open(ref_path)
    views = Image.open(views_path)
    w, h = views.size
    tile = (w // 3, h // 2)
    names = ["front", "side_a", "side_b", "back", "top", "bottom"]
    tiles = {n: views.crop(((i % 3) * tile[0], (i // 3) * tile[1], (i % 3 + 1) * tile[0], (i // 3 + 1) * tile[1]))
             for i, n in enumerate(names)}
    print("ref", ref.size, ref.mode, "views", views.size, "tile", tile)
    s, cov = band_score(ref)
    print(f"ref            band {s:.3f}  mask {cov:.2f}")
    for n, t in tiles.items():
        s, cov = band_score(t)
        print(f"gen {n:10s} band {s:.3f}  mask {cov:.2f}")

    side = 768
    panel = Image.new("RGB", (side * 3, side), (40, 40, 40))
    for i, im in enumerate([ref, tiles["front"], Image.open(normals_path)]):
        im = im.convert("RGBA")
        im.thumbnail((side, side))
        panel.paste(im, (i * side + (side - im.width) // 2, (side - im.height) // 2), im)
    panel.save(out_path)
    print("wrote", out_path)

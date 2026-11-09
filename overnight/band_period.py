"""Dominant vertical period of horizontal stripes in a view tile (row-profile spectrum of the high-passed image)."""
import sys
import numpy as np
from PIL import Image
views = Image.open(sys.argv[1]); w, h = views.size; t = w // 3
for name, (cx, cy) in {"front": (0, 0), "back": (0, 1)}.items():
    a = np.asarray(views.crop((cx * t, cy * t, cx * t + t, cy * t + t)).convert("L"), np.float32)
    a = a[:, t // 4: 3 * t // 4]                    # central columns, inside the plate
    hp = a - np.convolve(a.mean(1), np.ones(65) / 65, "same")[:, None]   # remove slow shading
    prof = hp.mean(1)[100:-100]
    spec = np.abs(np.fft.rfft(prof - prof.mean())) ** 2
    f = np.fft.rfftfreq(len(prof))
    sel = (f > 1 / 128) & (f < 1 / 6)
    top = np.argsort(spec[sel])[::-1][:5]
    print(name, "top periods px:", [round(1 / f[sel][i], 1) for i in top],
          "share of band power in 28-36px:", round(spec[sel][(1/f[sel] > 28) & (1/f[sel] < 36)].sum() / spec[sel].sum(), 3))

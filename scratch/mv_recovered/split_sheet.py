"""Split a turnaround sheet (front|left|back|right in one row) into 4 RGBA views on
equal HxH canvases. Background removed with rembg isnet on the whole sheet; panels are
found from the mask's column occupancy (not a blind equal split). Vertical placement is
kept as-is so all views share a baseline; each view is centred horizontally.
usage: split_sheet.py sheet.png outdir"""
import os, sys
import numpy as np
from PIL import Image
os.environ.setdefault("U2NET_HOME", "/mnt/ssd/ComfyUI/models/background_removal")
from rembg import new_session, remove
sheet = Image.open(sys.argv[1]).convert("RGB"); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
W, H = sheet.size
rgba = remove(sheet, session=new_session("isnet-general-use", providers=["CPUExecutionProvider"]))
a = np.asarray(rgba)[..., 3]
cols = (a > 32).sum(0) > 2
runs, x = [], 0
while x < W:
    if cols[x]:
        s = x
        while x < W and cols[x]: x += 1
        runs.append([s, x])
    x += 1
# merge runs separated by small gaps (thin parts can break a view into pieces)
merged = []
for r in runs:
    if merged and r[0] - merged[-1][1] < W // 40: merged[-1][1] = r[1]
    else: merged.append(r)
merged = [r for r in merged if r[1] - r[0] > 3]
print("panels found:", merged)
if len(merged) != 4:
    print("expected 4 views; falling back to equal split"); merged = [[i * W // 4, (i + 1) * W // 4] for i in range(4)]
for name, (x0, x1) in zip(["front", "left", "back", "right"], merged):
    crop = rgba.crop((max(x0 - 8, 0), 0, min(x1 + 8, W), H))
    canvas = Image.new("RGBA", (H, H), (0, 0, 0, 0))
    canvas.paste(crop, ((H - crop.width) // 2, 0))
    canvas.save(f"{out}/{name}.png"); print(name, "width", x1 - x0)

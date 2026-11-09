"""Lower-back metrics per GLB (raw axes): web roughness of the outer layer and shell thickness.
python back_metrics.py a.glb [b.glb ...]   (ComfyUI python: trimesh + scipy)"""
import sys
import numpy as np
import trimesh
from scipy import ndimage

ST = 0.005
for path in sys.argv[1:]:
    v = np.asarray(trimesh.load(path, force="mesh", process=False).vertices, float)
    x, y, z = v.T
    sel = (z > -0.09) & (z < 0.23) & (np.abs(x) < 0.30) & (np.abs(np.abs(x) - 0.14) > 0.02) & (-y > 0.10)
    ix = ((x[sel] + 0.30) / ST).astype(int); iz = ((z[sel] + 0.09) / ST).astype(int)
    shape = (iz.max() + 1, ix.max() + 1)
    outer = np.full(shape, -np.inf); inner = np.full(shape, np.inf)
    np.maximum.at(outer, (iz, ix), -y[sel]); np.minimum.at(inner, (iz, ix), -y[sel])
    ok = np.isfinite(outer)
    fill = outer[tuple(ndimage.distance_transform_edt(~ok, return_distances=False, return_indices=True))]
    rough = np.abs(fill - ndimage.gaussian_filter(fill, 3.0))[ok]            # 1.5 cm high-pass: terraces/peaks
    thick = (outer - inner)[ok]
    print(f"{path.split('/')[-1]:28s} roughness p50 {1000*np.median(rough):.2f} p95 {1000*np.percentile(rough,95):.2f} mm | "
          f"thickness p50 {1000*np.median(thick):.2f} mm, bins < 0.5 mm: {100*(thick < 0.0005).mean():.0f}%")

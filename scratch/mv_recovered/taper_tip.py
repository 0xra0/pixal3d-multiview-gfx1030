# Taper the blade end of a sword GLB into a point (vertex colours kept).
import sys, numpy as np, trimesh
src, dst, L = sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.08
m = trimesh.load(src, force="mesh"); v = m.vertices.copy()
ax = int(np.argmax(m.extents)); o = [i for i in range(3) if i != ax]
lo, hi = v[:, ax].min(), v[:, ax].max()
def width(end, sgn):  # width near each end tells blade (narrow) from pommel
    s = v[np.abs(v[:, ax] - end) < 0.02]; return np.ptp(s[:, o[0]])
end, sgn = (lo, 1) if width(lo, 1) < width(hi, -1) else (hi, -1)
d = (v[:, ax] - end) * sgn                        # distance from blade end
sel = d < L
ref = v[(d > L) & (d < L + 0.02)][:, o].mean(0)   # blade centreline
k = np.clip(d[sel] / L, 0, 1) ** 0.8              # 0 at tip -> 1 at L
v[np.ix_(sel, o)] = ref + (v[np.ix_(sel, o)] - ref) * k[:, None]
v[sel, ax] -= sgn * (1 - k) * 0.02                # pull the point out 2 cm
m.vertices = v; m.export(dst); print("tapered", sel.sum(), "verts at", "lo" if sgn > 0 else "hi")

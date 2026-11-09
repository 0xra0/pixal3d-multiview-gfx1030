import sys, json, math, numpy as np, trimesh
src, dst = sys.argv[1], sys.argv[2]
s = trimesh.load(src)                      # Scene
# Raw Pixal3D: content is Z-up inside Y-up glTF, so the content's up axis is raw Z.
R = trimesh.transformations.rotation_matrix(math.pi, [0, 0, 1])
s.apply_transform(R)
s.export(dst)
for p in (src, dst):
    b = open(p, 'rb').read(); n = int.from_bytes(b[12:16], 'little')
    d = json.loads(b[20:20+n])
    print(p.split('/')[-1], 'generator=', d['asset'].get('generator'), 'bounds=', np.round(trimesh.load(p).bounds, 3).tolist())

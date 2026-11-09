"""blender -b --python back_rays_bl.py -- a.glb [b.glb ...]
Rays from behind (file -Y) toward the front (file +Y, Pixal3D's front camera side) through each raw GLB's middle
60%: surfaces crossed per ray. Closed torso shell ~4 (back outer/inner, front inner/outer); open back ~2."""
import sys, bpy
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
for path in sys.argv[sys.argv.index("--") + 1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)
    obs = [o for o in bpy.data.objects if o.type == "MESH"]
    dg = bpy.context.evaluated_depsgraph_get()
    verts, polys = [], []
    for o in obs:
        me = o.evaluated_get(dg).to_mesh()
        base = len(verts)
        verts += [o.matrix_world @ v.co for v in me.vertices]
        polys += [[base + i for i in p.vertices] for p in me.polygons]
    tree = BVHTree.FromPolygons(verts, polys)
    # glTF import turns file +Y up into Blender +Z, file Z into Blender -Y: file +Y (front cam) = Blender +Z?
    # Do it axis-free: report counts along all three axes, both signs give the same crossing counts.
    xs = [v.x for v in verts]; ys = [v.y for v in verts]; zs = [v.z for v in verts]
    lo = Vector((min(xs), min(ys), min(zs))); hi = Vector((max(xs), max(ys), max(zs)))
    print(path.split("/")[-1], "faces", len(polys), "size", tuple(round(c, 3) for c in hi - lo))
    for axis in range(3):
        a, b = [i for i in range(3) if i != axis]
        counts = Counter(); grid = [[" "] * 25 for _ in range(25)]
        for i in range(25):
            for j in range(25):
                p = lo.copy(); p[a] = lo[a] + (hi[a] - lo[a]) * (0.2 + 0.6 * i / 24)
                p[b] = lo[b] + (hi[b] - lo[b]) * (0.2 + 0.6 * j / 24); p[axis] = lo[axis] - 1
                d = Vector((0, 0, 0)); d[axis] = 1
                n = 0
                while True:
                    hit = tree.ray_cast(p, d)
                    if hit[0] is None: break
                    n += 1; p = hit[0] + d * 1e-5
                counts[n] += 1; grid[24 - j][i] = str(min(n, 9))
        print("  along axis", "XYZ"[axis], dict(sorted(counts.items())))
        if axis == 2:
            print("\n".join("    " + "".join(r) for r in grid))

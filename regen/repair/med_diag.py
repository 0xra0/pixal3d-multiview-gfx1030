"""Medallion normal-map defect: test "near-coincident opposite-facing high surfaces" on a front-view ray grid.
blender -b --factory-startup --python med_diag.py -- lod0.glb high.glb normal_lod0.png out_prefix
Per grid ray (front view, +Y): first high hit facing, gap to next high hit and its facing, and the baked
normal map's tangent-space z where the same ray hits LOD0. Writes <out>_grid.npz and a 4-panel PNG."""
import sys
sys.dont_write_bytecode = True
import bpy
import bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

lod_path, high_path, nmap_path, out = sys.argv[sys.argv.index("--") + 1:][:4]
bpy.ops.wm.read_factory_settings(use_empty=True)


sys.path.insert(0, "/mnt/ssd/work/pixal3d-mv")
import prep_mesh


def load(path, kit_import=False):
    before = set(bpy.data.objects)
    if kit_import:  # same orientation handling as the asset build (source_up auto, yaw 0)
        prep_mesh.import_mesh(path, visible_only=True, source_up="auto", yaw=0)
    else:
        bpy.ops.import_scene.gltf(filepath=path)
    objs = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    bm = bmesh.new()
    for o in objs:
        m = o.data.copy()
        m.transform(o.matrix_world)
        bm.from_mesh(m)
    bm.faces.ensure_lookup_table()
    return bm


low, high = load(lod_path), load(high_path, kit_import=True)
lo_l = np.array([min(v.co[i] for v in low.verts) for i in range(3)]); hi_l = np.array([max(v.co[i] for v in low.verts) for i in range(3)])
lo_h = np.array([min(v.co[i] for v in high.verts) for i in range(3)]); hi_h = np.array([max(v.co[i] for v in high.verts) for i in range(3)])
shift = Vector(((lo_l + hi_l) / 2 - (lo_h + hi_h) / 2).tolist())
print("MED low bbox", lo_l, hi_l, "high bbox", lo_h, hi_h, "shift", shift)
for v in high.verts:
    v.co += shift
size = float(max(hi_l - lo_l)); c = (lo_l + hi_l) / 2
cage = 0.01 * size
uv = low.loops.layers.uv.active
print("MED uv layer", uv, "size", size, "cage", cage)
bt_low, bt_high = BVHTree.FromBMesh(low), BVHTree.FromBMesh(high)
img = bpy.data.images.load(nmap_path)
W, H = img.size
px = np.array(img.pixels[:], np.float32).reshape(H, W, img.channels)

# disc estimate from the render_maps.py framing: centre x=c.x, z=c.z+0.165*size, radius ~0.11*size; grid 0.3*size wide
N = 160
half = 0.15 * size
xs = np.linspace(c[0] - half, c[0] + half, N)
zs = np.linspace(c[2] + 0.165 * size + half, c[2] + 0.165 * size - half, N)
d = Vector((0, 1, 0))
y0 = lo_l[1] - 0.1 * size
first_back = np.full((N, N), np.nan); gap = np.full((N, N), np.nan); next_opp = np.full((N, N), np.nan)
nz = np.full((N, N), np.nan); nhits = np.zeros((N, N))
for j, z in enumerate(zs):
    for i, x in enumerate(xs):
        o = Vector((x, y0, z))
        hits = []
        p = o
        for _ in range(6):
            loc, nrm, idx, dist = bt_high.ray_cast(p, d)
            if loc is None:
                break
            hits.append((loc, nrm))
            p = loc + d * 1e-6
        nhits[j, i] = len(hits)
        if hits:
            first_back[j, i] = float(hits[0][1].dot(d) > 0)
            if len(hits) > 1:
                gap[j, i] = (hits[1][0] - hits[0][0]).length / size
                next_opp[j, i] = float(hits[1][1].dot(d) > 0)
        loc, nrm, idx, dist = bt_low.ray_cast(o, d)
        if loc is not None:
            f = low.faces[idx]
            # barycentric UV on the (triangulated) face
            vs = [l.vert.co for l in f.loops][:3]; uvs = [l[uv].uv for l in f.loops][:3]
            from mathutils.geometry import barycentric_transform
            b = barycentric_transform(loc, *vs, Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))
            u = sum(b[k] * uvs[k].x for k in range(3)); v = sum(b[k] * uvs[k].y for k in range(3))
            pxv = px[min(H - 1, max(0, int(v * H))), min(W - 1, max(0, int(u * W)))]
            nz[j, i] = pxv[2] * 2 - 1
np.savez(out + "_grid.npz", first_back=first_back, gap=gap, next_opp=next_opp, nz=nz, nhits=nhits)
disc = np.zeros((N, N), bool)
yy, xx = np.mgrid[0:N, 0:N]
disc[(xx - N / 2) ** 2 + (yy - N / 2) ** 2 < (0.10 / 0.30 * N) ** 2] = True
bad = disc & (nz < 0.6)
thin_opp = (gap < cage / size) & (next_opp == 0)  # next surface within cage distance and facing the ray: a stacked front layer
print(f"MED disc rays {disc.sum()}; normal z<0.6 {bad.sum()}; first hit back-facing {np.nansum(first_back[disc])}; "
      f"second hit within cage {np.nansum((gap < cage / size)[disc])}; of those, stacked front-facing layer {np.nansum(thin_opp[disc])}")
print(f"MED among bad rays: first back {np.nansum(first_back[bad])}, gap<cage {np.nansum((gap < cage / size)[bad])}, "
      f"stacked {np.nansum(thin_opp[bad])}; among good disc rays: first back {np.nansum(first_back[disc & ~bad])}, "
      f"gap<cage {np.nansum((gap < cage / size)[disc & ~bad])}")
print("MED gap percentiles in disc (fraction of size)", np.nanpercentile(gap[disc], [1, 10, 50, 90]))


def to_img(a, lo, hi):
    a = np.nan_to_num((a - lo) / (hi - lo), nan=0.0).clip(0, 1)
    return np.repeat(a[..., None], 3, -1)


panels = [to_img(nz, -0.2, 1), to_img(first_back, 0, 1), to_img(-np.log10(np.where(gap > 0, gap, 1)), 1, 4), to_img(thin_opp.astype(float), 0, 1)]
canvas = np.concatenate(panels, 1)
im = bpy.data.images.new("o", canvas.shape[1], canvas.shape[0])
im.pixels = np.concatenate([canvas[::-1], np.ones(canvas.shape[:2] + (1,))], -1).ravel()
im.filepath_raw = out + "_grid.png"; im.file_format = "PNG"; im.save()

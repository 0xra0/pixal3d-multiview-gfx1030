"""Flag LOD faces whose nearest high-poly surface is a zero-thickness double layer (faces of both orientations within
EPS). blender -b --factory-startup --python med_flag.py -- high.glb out_prefix lod0.glb [lod1.glb ...]
Prints where flagged faces cluster and saves <out>_lodN_flags.npy (bool per face, glTF import face order)."""
import sys
sys.dont_write_bytecode = True
import bpy, bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0, "/mnt/ssd/work/pixal3d-mv")
import prep_mesh

EPS = 1e-5
argv = sys.argv[sys.argv.index("--") + 1:]
high_path, out, lods = argv[0], argv[1], argv[2:]
bpy.ops.wm.read_factory_settings(use_empty=True)
prep_mesh.import_mesh(high_path, visible_only=True, source_up="auto", yaw=0)
ho = [x for x in bpy.data.objects if x.type == "MESH"][0]
hb = bmesh.new(); hb.from_mesh(ho.data); hb.transform(ho.matrix_world); hb.normal_update(); hb.faces.ensure_lookup_table()
hco = np.array([v.co[:] for v in hb.verts]); hlo, hhi = hco.min(0), hco.max(0)
bt = BVHTree.FromBMesh(hb)
hn = np.array([f.normal[:] for f in hb.faces])

for k, path in enumerate(lods):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    objs = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    assert len(objs) == 1, objs
    lb = bmesh.new(); lb.from_mesh(objs[0].data); lb.transform(objs[0].matrix_world); lb.normal_update()
    lco = np.array([v.co[:] for v in lb.verts]); llo, lhi = lco.min(0), lco.max(0)
    shift = Vector(((hlo + hhi) / 2 - (llo + lhi) / 2).tolist())  # low (pivot base) -> high frame
    flags = np.zeros(len(lb.faces), bool); cent = np.zeros((len(lb.faces), 3))
    for i, f in enumerate(lb.faces):
        p = f.calc_center_median() + shift
        cent[i] = p[:]
        loc, nrm, idx, dist = bt.find_nearest(p)
        near = bt.find_nearest_range(loc, EPS)
        dots = hn[[j for (_, _, j, _) in near]] @ np.array(nrm[:])
        flags[i] = (dots < -0.5).any()
    np.save(f"{out}_lod{k}_flags.npy", flags)
    fc = cent[flags]
    print(f"FLAG lod{k} faces {len(flags)} flagged {flags.sum()}")
    if len(fc):
        size = (hhi - hlo).max()
        # coarse spatial histogram: where are they (x,z on a 10x10 front grid, y sign)
        gx = ((fc[:, 0] - hlo[0]) / (hhi[0] - hlo[0]) * 10).astype(int).clip(0, 9)
        gz = ((fc[:, 2] - hlo[2]) / (hhi[2] - hlo[2]) * 10).astype(int).clip(0, 9)
        H = np.zeros((10, 10), int)
        np.add.at(H, (9 - gz, gx), 1)
        print(f"FLAG lod{k} front-grid counts (rows top->bottom, x left->right); front y<0: {(fc[:, 1] < (hlo[1] + hhi[1]) / 2).mean():.2f}")
        for row in H:
            print("FLAG   " + " ".join(f"{v:4d}" for v in row))
        c = fc.mean(0)
        print(f"FLAG lod{k} centroid {np.round(c, 4)} extent x {np.round(np.percentile(fc[:, 0], [2, 98]), 4)} "
              f"z {np.round(np.percentile(fc[:, 2], [2, 98]), 4)} y {np.round(np.percentile(fc[:, 1], [2, 98]), 4)} (size {size:.3f})")

"""High-poly disc faces: orientation toward the viewer, winding consistency, stored vs computed normals.
blender -b --factory-startup --python med_winding.py -- high.glb"""
import sys
sys.dont_write_bytecode = True
import bpy, bmesh
import numpy as np
from mathutils import Vector
sys.path.insert(0, "/mnt/ssd/work/pixal3d-mv")
import prep_mesh
src = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
prep_mesh.import_mesh(src, visible_only=True, source_up="auto", yaw=0)
objs = [o for o in bpy.data.objects if o.type == "MESH"]
print("WIND objects", [(o.name, len(o.data.polygons), o.data.has_custom_normals if hasattr(o.data, "has_custom_normals") else None) for o in objs])
o = objs[0]; me = o.data
bm = bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world); bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
co = np.array([v.co[:] for v in bm.verts])
lo, hi = co.min(0), co.max(0); size = (hi - lo).max(); c = (lo + hi) / 2
# disc centre in high coordinates: low z=c+0.165*size maps to high (low bbox z-centre 0.4893 -> high 0)
dc = np.array([c[0], 0, c[2] + 0.165 * size]); r = 0.10 * size
sel = [f for f in bm.faces if (f.calc_center_median().x - dc[0]) ** 2 + (f.calc_center_median().z - dc[2]) ** 2 < r * r
       and f.calc_center_median().y < c[1]]
print("WIND size", size, "disc faces (front half)", len(sel))
ny = np.array([f.normal.y for f in sel])
print(f"WIND face normal toward viewer (y<-0.3) {(ny < -0.3).mean():.3f}, away (y>0.3) {(ny > 0.3).mean():.3f}, sideways {((abs(ny) <= 0.3)).mean():.3f}")
sset = set(sel); incons = tot = 0
for f in sel:
    for e in f.edges:
        lf = [g for g in e.link_faces if g in sset and g is not f]
        if len(lf) != 1: continue
        g = lf[0]; tot += 1
        a = [l for l in f.loops if l.edge is e][0]; b = [l for l in g.loops if l.edge is e][0]
        incons += a.vert is b.vert   # consistent winding traverses a shared edge in opposite directions
print(f"WIND shared-edge pairs {tot}, inconsistent winding {incons} ({incons / max(tot, 1):.3f})")
# stored (glTF) normals vs face normals on the disc
cn = np.empty(len(me.loops) * 3, np.float32); me.corner_normals.foreach_get("vector", cn) if hasattr(me, "corner_normals") else None
cn = cn.reshape(-1, 3)
rot = np.array(o.matrix_world.to_3x3())
agree = []
for f in sel:
    p = me.polygons[f.index]
    n = (rot @ cn[p.loop_start:p.loop_start + p.loop_total].mean(0)); n /= (np.linalg.norm(n) + 1e-12)
    agree.append(float(n @ np.array(f.normal[:])))
agree = np.array(agree)
print(f"WIND corner-normal . face-normal on disc: p1 {np.percentile(agree, 1):.3f} p10 {np.percentile(agree, 10):.3f} median {np.median(agree):.3f}; below 0: {(agree < 0).mean():.3f}")
cny = np.array([(rot @ cn[me.polygons[f.index].loop_start:me.polygons[f.index].loop_start + me.polygons[f.index].loop_total].mean(0))[1] for f in sel])
print(f"WIND corner normals toward viewer {(cny < -0.1).mean():.3f}, away {(cny > 0.1).mean():.3f}")
# control: same test on the whole front of the cuirass outside the disc
ctl = [f for f in bm.faces if f.calc_center_median().y < c[1] - 0.1 * size and f not in sset][:200000]
cy = np.array([f.normal.y for f in ctl])
print(f"WIND control front faces {len(ctl)}: toward {(cy < -0.3).mean():.3f} away {(cy > 0.3).mean():.3f}")

import bpy, sys, bmesh
from mathutils.bvhtree import BVHTree
a = sys.argv[sys.argv.index("--")+1:]
def load(p):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.import_scene.gltf(filepath=p)
    obs=[o for o in bpy.context.selected_objects if o.type=="MESH"]
    bm=bmesh.new()
    for o in obs:
        m=o.data.copy(); m.transform(o.matrix_world); bm.from_mesh(m)
    bm.faces.ensure_lookup_table(); return bm
ref=load(a[0]); tree=BVHTree.FromBMesh(ref)
for p in a[1:]:
    bm=load(p); tot=bad=0.0; n=nb=0
    for f in bm.faces:
        c=f.calc_center_median(); hit=tree.find_nearest(c)
        if hit[0] is None: continue
        ar=f.calc_area(); tot+=ar; n+=1
        if f.normal.dot(ref.faces[hit[2]].normal) < 0: bad+=ar; nb+=1
    print("FOLD", p.split("/")[-1], f"faces {n} reversed {nb} ({100*nb/n:.1f}%) area {100*bad/tot:.1f}%")

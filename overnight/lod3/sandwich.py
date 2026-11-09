import bpy, bmesh, sys
sys.path.insert(0, "/mnt/ssd/work/pixal3d-mv"); import prep_mesh as prep
glb = sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=glb)
obj = next(o for o in bpy.context.scene.objects if o.type == "MESH")
bpy.context.view_layer.objects.active = obj; obj.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=1e-6); bpy.ops.mesh.separate(type="LOOSE"); bpy.ops.object.mode_set(mode="OBJECT")
parts = [o for o in bpy.context.scene.objects if o.type == "MESH" and 4 < len(o.data.polygons) <= 64]
def run(src, target, offset):
    o = src.copy(); o.data = src.data.copy(); bpy.context.scene.collection.objects.link(o)
    m = o.modifiers.new("d", "DECIMATE"); m.ratio = max(1, target - offset) / len(o.data.polygons); m.use_collapse_triangulate = True
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier=m.name)
    raw = len(o.data.polygons)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_area() <= 1e-20], context="FACES")
    prep.remove_duplicate_faces(bm); prep.remove_loose(bm); kept = len(bm.faces); bm.free()
    bpy.data.objects.remove(o, do_unlink=True); return raw, kept
for offset in (1, 0):
    res = [run(p, 4, offset) for p in parts]
    print("OFFSET", offset, "parts", len(res), "erased", sum(k == 0 for _, k in res),
          "raw sizes", sorted(set(r for r, _ in res)), "max kept", max(k for _, k in res))

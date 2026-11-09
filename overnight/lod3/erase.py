# Which LOD0 components does collapse-decimation erase, and at what target do they survive?
import bpy, bmesh, sys, collections
glb = sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
obj = next(o for o in bpy.context.scene.objects if o.type == "MESH")
bpy.context.view_layer.objects.active = obj; obj.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=1e-6); bpy.ops.mesh.separate(type="LOOSE"); bpy.ops.object.mode_set(mode="OBJECT")
parts = [o for o in bpy.context.scene.objects if o.type == "MESH"]
def trial(src, target):
    o = src.copy(); o.data = src.data.copy(); bpy.context.scene.collection.objects.link(o)
    m = o.modifiers.new("d", "DECIMATE"); m.ratio = max(1, target-1)/len(o.data.polygons); m.use_collapse_triangulate = True
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier=m.name)
    bm = bmesh.new(); bm.from_mesh(o.data)
    raw = len(bm.faces); nz = sum(1 for f in bm.faces if f.calc_area() > 1e-20)
    bm.free(); bpy.data.objects.remove(o, do_unlink=True); return raw, nz
hist = collections.Counter(len(p.data.polygons) for p in parts)
print("PARTS", len(parts), "sizes", sorted(hist.items())[:15])
for p in sorted(parts, key=lambda p: len(p.data.polygons))[:8] + sorted(parts, key=lambda p: len(p.data.polygons))[100:104]:
    n = len(p.data.polygons)
    print("PART", n, {t: trial(p, t) for t in (4, 6, 8, 12, 16) if t < n})

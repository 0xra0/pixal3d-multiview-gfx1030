"""blender -b -P lod_shards.py -- <lod.glb> : largest triangles, their normal and the base colour texel at their UV centre."""
import sys, bpy, numpy as np
glb = sys.argv[sys.argv.index("--") + 1]
bpy.ops.import_scene.gltf(filepath=glb)
obj = max((o for o in bpy.context.scene.objects if o.type == "MESH"), key=lambda o: len(o.data.polygons))
me = obj.data; me.calc_loop_triangles()
img = next(i for i in bpy.data.images if i.colorspace_settings.name == "sRGB" and i.size[0] > 0); print("IMGS", [(i.name, i.colorspace_settings.name) for i in bpy.data.images])
w, h = img.size; px = np.array(img.pixels[:], np.float32).reshape(h, w, 4)
uv = me.uv_layers.active.data
areas = np.array([t.area for t in me.loop_triangles]); order = np.argsort(-areas)
tot = areas.sum(); print("tris", len(areas), "area top20 share", round(areas[order[:20]].sum() / tot, 3), "img", img.name, w)
for i in order[:12]:
    t = me.loop_triangles[i]; c = np.mean([uv[l].uv[:] for l in t.loops], 0)
    col = px[min(h - 1, int(c[1] * h)), min(w - 1, int(c[0] * w)), :3]
    print(f"area {areas[i]*1e4:.1f}cm2 normal {np.round(t.normal[:],2)} uv {np.round(c,3)} rgb {np.round(col,2)}")

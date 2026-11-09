"""Test Loopcut's sculpt brushes (studio_vendor/handlers/sculpt.py) on the cuirass lower back, headless.
blender -b --factory-startup --python loopcut_sculpt_test.py -- in.glb out_prefix
Writes <out_prefix>_smooth.glb and <out_prefix>_flatten.glb (glTF coords = raw coords on a round trip).
Raw axes: up is -Z, front is +Y; Blender import maps raw (x, y, z) -> (x, -z, y)."""
import sys
sys.dont_write_bytecode = True          # never write __pycache__ into the Loopcut tree
sys.path.insert(0, "/mnt/sata/loopcut/scripts/addons_core/loopcut")
import bpy
from studio_vendor.handlers import sculpt as S

src, prefix = sys.argv[sys.argv.index("--") + 1:][:2]


def load():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=src)
    obj = next(o for o in bpy.context.scene.objects if o.type == "MESH")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if obj.parent:                       # keep the world transform on the mesh itself
        bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    import bmesh                          # the glTF import keeps coincident unconnected vertices; brushes tear them apart
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bm.to_mesh(obj.data); bm.free(); obj.data.update()
    print("LOOPCUT welded to", len(obj.data.vertices), "vertices")
    return obj


def rows(obj):
    """Horizontal strokes over the lower back (raw z -0.11 .. 0.25), snapped to the outer back surface."""
    strokes = []
    for i in range(19):
        zr = -0.11 + 0.02 * i
        rough = [[xr, -zr, -0.40] for xr in [-0.32 + 0.04 * k for k in range(17)]]   # Blender coords, outside the back
        hits = S.surface_points(obj.name, points=rough)["points"]
        strokes.append([h["co"] for h in hits if h["hit"]])
    return strokes


def run(brush, radius, strength, passes, out, front=False):
    import time
    obj = load()
    strokes = rows(obj)
    moved, t = 0, time.perf_counter()
    for _ in range(passes):
        for pts in strokes:
            moved = max(moved, S.sculpt_stroke(obj.name, brush, pts, radius, strength=strength, symmetry="",
                                               front_faces_only=front)["verts_moved"])
    took = time.perf_counter() - t
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_apply=True)
    print(f"LOOPCUT {brush} front={front} r={radius} s={strength} x{passes}: verts touched/stroke up to {moved}, "
          f"{took:.1f} s -> {out}")


# extra args pick runs: smooth (default), smooth_front, flatten, flatten_front
for job in sys.argv[sys.argv.index("--") + 3:] or ["smooth"]:
    brush, front = job.split("_")[0], job.endswith("_front")
    run(brush, 0.03, 1.0, 8, f"{prefix}_{job}.glb", front)
# flatten without front_faces_only collapses the two shell layers into shards (tested 2026-11-08)

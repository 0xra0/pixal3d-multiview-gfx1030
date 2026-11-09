import bpy, bmesh, sys
sys.path.insert(0, "/mnt/ssd/work/pixal3d-mv")
import prep_mesh as prep
from asset_config import parse_asset
args = parse_asset(["in.glb", "out"])
src = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
obj = prep.import_mesh(src)
def count(bm, tag):
    seen, n, single = set(), 0, 0
    for f in bm.faces:
        if f in seen: continue
        stack, size = [f], 0; seen.add(f)
        while stack:
            g = stack.pop(); size += 1
            for v in g.verts:
                for h in v.link_faces:
                    if h not in seen: seen.add(h); stack.append(h)
        n += 1; single += size == 1
    print("REP", tag, "components", n, "single-face", single, "faces", len(bm.faces))
prep.edit_mesh(obj, lambda bm: count(bm, "import"))
stats = prep.edit_mesh(obj, lambda bm: prep.repair(bm, args))
print("REP stats", stats)
prep.edit_mesh(obj, lambda bm: count(bm, "repair"))

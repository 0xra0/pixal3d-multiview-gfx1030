"""Full pa.py texture run at 1024, tex5's seed and mesh, to compare dense (new default) with tex5 (sparse)."""
import sys
sys.path.insert(0, "/mnt/ssd/work/pixal3d-mv")
import pa
pa.new_seed = lambda seed=None, bits=0: (print("  seed 84262749 (pinned to tex5)"), 84262749)[1]
pa.texture("vampire_chestplate", "/mnt/ssd/work/overnight/a7/meshes/vampire_chestplate_LOD0.glb", 1024)

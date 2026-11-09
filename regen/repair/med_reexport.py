"""Re-export every LOD of an asset .blend with the kit's own export_lod (same GLB/FBX settings as the build),
after its texture PNGs were edited on disk. blender -b --factory-startup asset.blend --python med_reexport.py -- name"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from types import SimpleNamespace
import bpy
sys.path.insert(0, "/mnt/ssd/work/pixal3d-mv")
import build_asset as B

name = sys.argv[sys.argv.index("--") + 1]
folder = Path(bpy.data.filepath).parent / "meshes"
for im in bpy.data.images:
    if im.source == "FILE":
        im.reload()
args = SimpleNamespace(name=name, formats=["glb", "fbx", "blend"], engine="witcher3")
for i in range(4):
    obj = bpy.data.objects[f"{name}_LOD{i}"]
    obj.hide_set(False)
    files, metrics = B.export_lod(obj, i, [], args, folder)
    print("REEXPORT", i, files, metrics, flush=True)

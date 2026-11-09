# Medallion REDengine reference exports

These are supplemental static geometry handoffs, not native game mods.

- `cyberpunk.glb`: material-free GLB with two named LOD_1 chunks, UV0, normals and tangents; all 39,985 triangles retained. Import into a compatible existing `.mesh` in WolvenKit and map both chunks to the same native material.
- `witcher3.fbx`: render geometry only, with tangents and embedded preview textures. Import via REDkit and configure native materials and physics.
- `export_checks.json`: checked chunk counts. Native import is not_run.

Both files correspond to the parent sample's LOD0. Its maps are under `../textures/lod0/`; `normal_lod0.png` uses OpenGL convention. Native shader conventions must be configured in the mod tools. The new presets generate both normal conventions when you rebuild. Other source LODs use separate atlases and must not share this material without reprojecting.

The source lacks final materials and has surface/open-edge/UV-efficiency review flags. See the parent review.html and the project REDENGINE.md. These exports have not been tested inside either game.

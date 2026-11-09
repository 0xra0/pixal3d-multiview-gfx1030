# Local evals 20261108-230158

{'label': 'IQ2_XS + skills v1, vram reserve 3072', 'model': 'strata', 'base_url': 'http://127.0.0.1:8099/v1', 'skills': '/mnt/sata/loopcut/local-skills', 'started': '2026-11-08 23:01:58'}

**10/13 passed**, 2754 s, 75 steps, 28 failed calls

Against 20261108-224206: won none, lost none

| task | result | s | steps | failed calls | detail |
|---|---|---|---|---|---|
| red_sphere | PASS | 107 | 3 | 1 | size (1.000, 1.000, 1.000), bottom 1.000, centre (0.000, 0.000, 1.500), base colour (1.0, 0.0, 0.0) |
| steel_material | FAIL | 142 | 4 | 2 | metallic 1.00, roughness 0.50, base colour (0.050, 0.050, 0.055) |
| modifier_stack | PASS | 204 | 5 | 2 | mirror x True, bevel width 0.0200, segments 3 |
| triangle_budget | PASS | 124 | 3 | 1 | 5000 triangles in the mesh itself, modifiers [], size (2.400, 2.001, 1.599) |
| mesh_cleanup | PASS | 122 | 6 | 2 | 8 vertices (8 distinct), 0 not on a face, 6 faces |
| base_pivot | PASS | 70 | 1 | 0 | origin (0.000, 0.000, 0.000), world bounds (-0.400, -0.400, 0.000)..(0.400, 0.400, 2.000), lowest vertex above origin 0.000 |
| real_size | PASS | 62 | 1 | 0 | size (0.256, 0.026, 1.280), scale (1.000, 1.000, 1.000) |
| uv_unwrap | PASS | 38 | 1 | 0 | 0 grid cells overlap, 41750 covered, 0 UVs outside 0-1 |
| lods | PASS | 89 | 1 | 0 | Barrel 3072 (was 3072); LOD1 1536, LOD2 768, LOD3 384 |
| export_glb | PASS | 315 | 13 | 6 | magic b'glTF', nodes ['Gem'], exported triangles 116, Gem evaluated 116 |
| door_keys | PASS | 106 | 3 | 2 | Z at 1: 0.0 deg, at 48: 90.0 deg, frame_end 48 |
| gn_scatter | FAIL | 1201 | 34 | 12 | timed out after 1200 s |
| longsword | FAIL | 174 | 0 | 0 | no mesh object named Longsword; objects [] |

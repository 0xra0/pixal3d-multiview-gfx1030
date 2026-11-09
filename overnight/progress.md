# Overnight 2026-11-03 23:43 → 06:00

Goal: improve 3D modelling/creation pipeline (kit /mnt/ssd/work/pixal3d-mv).

## Done
- Tried "ABF only merged islands" in sculpt smart_uv: isolated 1306→1269, fill 48.4→48.3%, +10 s. No gain → reverted (backup packtest/prep_mesh.py.bak-merge2 = current).

## Findings
- GameAssets/vampire_chestplate (08:26 build, pre-merge): LOD0 20k tris, 6455 UV islands, coverage 23.7% (gate 40%), relax_charts rejected (20.2% < 22.7%), 938 isolated faces, 112 components (most 1-face shards), basecolor_black 32%.

## In progress
- a1: rebuild chestplate asset with uv_merge_faces=20 → /mnt/ssd/work/overnight/a1
- a1 (merge20, smart): coverage 23.7→31.2%, isolated 4339, 6:45 wall, 2.0 GB.
- xatlas (ComfyUI env py3.12, 0.0.11) on LOD0 offline: coverage 44.4%, 2973 charts, 7 s.
- Added: xatlas_worker.py (stdin/stdout npz), prep_mesh.unwrap_uv/xatlas_uv, --uv-method xatlas|smart (default xatlas, quads→smart), asset_geometry uses unwrap_uv, skips relax for xatlas, report uv.method/method_fallback. Backups overnight/*.bak-xatlas.
- a2 running (xatlas).
- a2 xatlas raw: 31.4% (fix_uv_overlaps repacked whole atlas after 2 folds). Fixed: worker cuts folded faces loose as separate meshes (xatlas welds colocal verts within one mesh) and re-charts until fold-free (≤8 passes).
- a3 xatlas fold-free: coverage 44.1% (gate pass), islands 3106, subpx 20, isolated 0, 4:03 wall. uv_coverage issue gone.
- Dust: source chestplate 116 comps / 91 lone open triangles (fins on closed surface = 249 of 265 boundary edges). Added drop_open_dust (--dust-size 0.01, open shells < 1% diag; closed parts kept) → 25 comps. Necklace -7 faces, pendant -6. Backups overnight/*.bak-dust.
- Stale test fixed (test_uv_fallback: v2 re-unwrap means 0 isolated is valid). Blender suites 12+9 OK, pytest 26 OK.
- n3 necklace (xatlas, pre-dust) running.
- n3 necklace: xatlas failed (297 zero-UV faces: xatlas absolute epsilons vs sub-mm tris) → Smart fallback 30.3%, 6356 isolated, 15:44 wall. Fix: worker rescales to 100-unit bbox. Necklace offline 44.8%. Test now uses 2 mm grid; mutation (no rescale) fails it.
- n4 + a4 (all fixes) running.
- n4 necklace all fixes: cov 27.9→45.2%, islands 6092→3219, subpx 829→59, isolated 1151→0, open_topology gone, 15:44→11:07.
- a4 chestplate all fixes: cov 44.0%, subpx 4, open_topology gone, comps 112→25. BUT 8:40 (a3 4:03): batch_bake_parts early-returned at ≤32 parts → 25 bake groups vs 6. Removed early return (bak overnight/asset_geometry.py.bak-batch). a5 running.
- a5 (always batch): 3:19 wall, 3 bake groups, same quality. Also skip Blender repack candidates for xatlas (always lost 44→30%).
- Production rebuild via pa.py asset (both) — backups in overnight/gameassets-backup.
- Tried xatlas on sculpt quad cage (fan tris + split torn quads loose): torn 6637→3613 after 8 passes, never converges, +220 s. Reverted to triangle-only (bak overnight/xatlas_worker.py.bak-tri). Sculpt stays Smart UV.
- Docs: README (--uv-method, --dust-size), GAME_ASSET_PIPELINE, CHANGES.md 2026-11-04.
- Profile necklace (n5, 634 s): bake = 570 s; 7 maps × 34 groups × 4 LODs; per-call overhead dominates.
- Constant channels (Roughness/Metallic/Alpha unlinked, Emission black) now filled instead of baked (asset_bake.constant_channel; bak overnight/asset_bake.py.bak-const). n6: 5:21 vs 10:41; basecolor/normal/metal/emission identical; roughness differs only at island edges where old 1-sample bake blended 0.5 toward black (old was wrong).
- GPU (HIP RX 6800) bake tried: 355 s vs 320 s CPU → removed option.
- Spatial batching of non-tiny parts (disjoint ray-grown AABBs, size ratio ≤2, ≤32/group; bak *.bak-group). n8 running.
- n8 spatial batching: necklace 3:17 (groups 34→16), texel diffs negligible. Tests 26/9/12 OK.
- Production GameAssets rebuilt (pa.py asset): chestplate 2:07, necklace 3:17. Original backups: overnight/gameassets-backup.
- 3DGenStudio auto_uv: not modified (upstream app); candidate for xatlas later.
- Sculpt profile s1 running (backup of current sculpt output: /mnt/ssd/work/sculpt/uv3_sculpt.*).
- Sculpt: hiding multires (show_viewport False) during UV: 271→201 s, identical GLB/OBJ/UV (bak overnight/prep_mesh.py.bak-mrhide).
- ComfyUI launched (task bdwugziu1, log overnight/comfy.log) for UltraTex test: pa.py texture vampire_chestplate 1024 → tex1.log. STOP ComfyUI after (by PID, check /proc/PID/comm).
- UltraTex texture failed validation: ComfyUI core renamed LoadBackgroundRemovalModel input bg_removal_model→bg_removal_name. Fixed workflows/04_texture.json node 3 (node 4 RemoveBackground keeps bg_removal_model). Backups overnight/wf-bak.
- pa.py check now validates every workflow against live /object_info (workflow_drift; unit test). Would have flagged the rename. bak overnight/pa.py.bak-drift.
- tex1 (UltraTex 1024 on xatlas LOD0) running.
- tex1 UltraTex 1024 on xatlas LOD0: success 2982 s (~50 min) → output/UltraTex/vampire_chestplate_00001_.glb. Looks BAD: light-grey per-chart camouflage vs dark reference (renders overnight/tex1_pair.png). UltraTex = 6 generated views back-projected to UV, so UV charts shouldn't decide content.
- Added SaveImage of sampler view atlas (node 30) + prep normal views (node 31) to 04_texture.json, prefixes set in pa.py. tex2 rerun to split: views bad (generation/normals of noisy LOD0) vs bake bad.
- tex2 crashed: ComfyUI HIP illegal memory access in GGUF dequant during 2nd sampler (ROCm flake; tex1 identical run succeeded). Saved normal views prove ROOT CAUSE of bad texture: mesh lies on its back — UltraTex "front" view = top view.
- Pixal3D MV GLBs are Z-up in Y-up glTF (sword/chestplate tallest=Z; plain Trellis2 tallest=Y). GameAssets lie on their back in every engine; pivot base wrong axis.
- Added --source-up y|z (import rotates +90° X), default y (no behaviour change; user decision). a6 (--source-up z): upright, base z=0, front faces -Y. Test added (13 Blender integration OK). bak overnight/*.bak-up.
- tex3: UltraTex on upright a6 LOD0 running (ComfyUI relaunched, log comfy2.log).
- tex3 done (3564 s): view atlas upright, front matches reference silhouette/medallion; render tex3_front.png dark plate, no camouflage. Hypothesis confirmed. ComfyUI stopped (pid 1710616), VRAM 1%.
06:19 source-up default -> auto (trimesh->z); pytest 28, integration 13 OK

## 2026-11-04 evening — `--source-up auto` default, end-to-end test
- a7 (Pixal3D trimesh GLB, auto): `PREP source-up z`, LOD0 19998 faces, upright 0.77 m on +Y.
- a8 (re-import of a7 Blender export, auto): `PREP source-up y`, 19982 faces, wall 3:22.69; bounds match a7 within ~1 mm → no double rotation.
- tex4 (UltraTex 1024 on a7 LOD0, seed 1069181026, provenance OK → prep skipped): albedo pass 25 steps 1331 s (53.2 s/step, peak 5.4 GB); MR LoRA pass 25 steps 1313 s (52.5 s/step, peak 7.5 GB); bake 2048² ~10 min; server total 01:00:28 → `UltraTex/vampire_chestplate_00003_.glb` (+ _albedo/_orm).
- pa.py client hit PA_MAX_WAIT=3600 at 3604 s and exited 1 while the server finished 24 s later. 1024 runs on this mesh need PA_MAX_WAIT≈5400. Timeout message ("may still be loading") is misleading here.
- tex4_front.png (render_front.py, headless EEVEE ortho): upright, dark plate, medallion + gems placed, no camouflage; some pale smears lower-centre and horizontal ripple patterns.
- ComfyUI stopped (pid 1724021), VRAM 3%.
- 21:56 pa.py: PA_MAX_WAIT default 3600→5400 (pa.py:39, docstring, README:54); timeout message now says the prompt may still be running and names /history/<pid>. Backups overnight/pa.py.bak-maxwait, README.md.bak-maxwait. Rerun as tex5 (ComfyUI pid 2003581, log comfy5.log) to confirm exit 0.

## 22:58 tex5 result
- pa.py texture (PA_MAX_WAIT 5400) exit 0, wall 58:01; output UltraTex/vampire_chestplate_00004_.glb (+ _albedo/_orm png).
- Render overnight/tex5_front.png: upright, medallion + gems placed; horizontal ripple banding still present (also seen in tex4) — open question whether it comes from LOD0 surface stepping or the texture.
- ComfyUI pid 2003581 stopped by PID; no leaked main.py / blender -b; VRAM 165 MiB.

## 06:20 tex5 banding: geometry vs texture
- render_bare.py (grey material, same camera as render_front.py) -> bare_lod0.png, bare_tex5.png. Both have the same geometry (19998 faces, same bounds).
- Geometry has concentric ridges at the neck only, plus shredded shard faces and holes around the gems. No straight horizontal bands across chest/belly.
- Front conditioning normal map (normals_00021) has no bands either.
- The bands are already in the generated front view (views_00003 top-left), weaker in back/sides -> painted by the image model, then baked. Not a remesh/geometry fault.
- Albedo atlas is thousands of tiny islands (confetti UVs) from the shredded mesh.
- Cause of the painted bands: not tested.

## 2026-11-06 (RAM now 47 GB, VRAM 16 GB)
### Chestplate bands: where they come from
- cmp_ref_front.py: reference front.png vs tex5 views_00003 front vs normals_00021 -> cmp_ref_front.png. Band score (d/dy energy / d/dx energy in mask): reference 0.884, tex5 front 1.913. The reference has no bands; the model adds them.
- Ruled out: SLA Triton kernel on ROCm (sla_check.py: topk 1.0 rel err 0.0024; sla_check2.py: topk 0.2/0.5 vs masked exact with same block map 0.0022), block-row periodicity (band_period.py: no 32 px peak), reference stretching (fit is a uniform scale).
- views_test.py = albedo sampler only, scores every tile, appends to views_test.tsv.
- 512, tex5 seed 84262749 (base_s1): clean, front 0.893 back 0.815 sides 0.794/0.863; 475 s, 10.5 s/step, 11.5 GB peak. -> bands depend on resolution.
- 512 with token_chunk 1024 (chunk1024_s1; 512 normally runs as one 5815-token chunk): front 0.891, same as base; 920 s. -> chunking is exact and not the cause.

### NAF rerun (medallion_pendant 4242, default launch_comfy_qwen.sh = real NAF flex), 2026-11-06
- Final decode subdiv 0: parents 7,977 / active 7,977 (same as the 10-31 flex run; shim run was 6811/8017).
- Decoder mesh: 2,199,746 verts / 4,762,646 faces (10-31: 4.04M). After remesh+simplify: 289,118 faces (target 300k).
- No CuMesh error, no traceback. Prompt time 22:41. Mesh QA 1.012, IoU front 0.89 / left 0.69 / back 0.89 / right 0.57 (side warnings).

### GPU crash during dense1024 (2026-11-06 21:31)
- NAF rerun finished before the crash (21:25, exit 0): subdiv0 7,977/7,977, 2,199,746 verts / 4,762,646 faces, no CuMesh error, QA 1.014. Same as run 1, so this result repeats.
- dense1024 (attention=ultratex_sparse, topk=1.0): the sampler started at 21:30:17. At about 21:30:36 the gfx ring timed out (mpvpaper, then Hyprland). Hyprland's ring reset failed, so the GPU was fully reset. ComfyUI (pid 59883) lost its KFD queues and died. Hyprland restarted.
- The earlier "interrupted" dense run looks the same: its sampler started at 19:20:25 and the log stopped at 19:21:08. That makes it 2 out of 2 dense runs that hung within about a minute of the first step.
- The sparse run at the same 1024 resolution (tex5) ran for about an hour without trouble. Cause: the Triton block-sparse kernel at top-k 1.0, about 17.5k tokens with chunk 8192, makes very long kernels. They starve the gfx queue past amdgpu's 10 s lockup timeout. There is no VM fault in dmesg, so this is a timeout, not a bad memory access.
- At 21:20 (during the NAF decode), "pin framebuffer -12" means VRAM was full and the compositor could not pin a frame. It is a separate issue and did no harm.
- Not run: 1536 sparse.

### dense1024 result + second GPU crash (2026-11-06 22:15)
- dense1024_cd_s1 (comfy_default, seed 84262749, 1024): front 0.731 back 0.748 sides 0.777/0.770, 1382 s, no GPU reset. Visually clean, no bands. vs sparse tex5 front 1.913, ref 0.884 -> top-k sparse attention is the band source at 1024.
- First dense step 36.6 s vs ~53 s/step sparse: dense is faster too.
- sparse1536_s1: 16282/55296 target + 20344 ref tokens, ultratex_sparse top-k 0.2, reserve 3.4 GB. GPU hung before the first step finished (~22:10), with mpvpaper paused. ComfyUI and the Claude session died; no reboot (uptime from 20:51).
- Logs: vt_sparse1536_crash.log, comfy8_crash.log. dmesg not readable without sudo.
- Old mpvpaper 211079 still SIGSTOPped (state T); the session started a new mpvpaper 427481.

### sparse1536 rerun result (2026-11-06 23:45)
- Survived: no GPU reset with Loupe and mpvpaper closed. The 22:10 crash was likely the Loupe GPU draw mid-kernel.
- sparse1536_s1 (ultratex_sparse top-k 0.2, seed 84262749): 5129 s total (85 min), first step 189.9 s.
- band_score front 0.749 / back 0.800 / sides 0.831 0.863. Clean image, no horizontal chest bands.
- Comparison (front): ref 0.884, 512 sparse 0.893, 1024 sparse 1.913 (bands), 1024 dense 0.731, 1536 sparse 0.749.
- So the bands appear with sparse at 1024 only, not at 512 or 1536. Single seed: it could be resolution-specific
  (block/top-k layout at 4096 tokens/view) or seed luck. Dense 1024 is still the best quality per minute (23 min vs 85).

## 2026-11-07 05:58 — 2048 dense (comfy_default) test: OOM, no output
- Tokens: 27827/98304 target + 34869 ref + 512 text = ~63.2k (1.7x the 1024 run).
- OOM in step 1, first single-block attention (sub_quadratic_attention all_values/all_weights):
  15.24 GiB allocated, 174 MiB free, non-releasable only ~0.3 GiB → not fragmentation, it doesn't fit.
- 1451 s wall, almost all of it load/prep before sampling. No views produced.
- Implication: workflow now comfy_default → `pa.py texture ... 2048` will OOM. Dense verified only at 1024;
  1536 was sparse. Backup of sparse workflow: 04_texture.json.bak-sparse-20261107.
- ComfyUI stopped by PID (exit 143 = our SIGTERM). VRAM 0%. No leftover processes.

## 2026-11-07 09:30 — 1536 dense (comfy_default) test, running
- Token correction: 1024 = 7.8k target + 9.7k ref (~18k), 1536 = 16.3k + 20.3k (~37k), 2048 = 27.8k + 34.9k (~63k).
  (Earlier report wrongly labelled ~37k as 1024.)
- 1536 dense passed step 1 (no OOM): first step 240 s, VRAM 15.3 GiB used. Sparse 1536 was 190 s first / 155 s avg, 25 steps.
- ETA: ~25 × ~200 s ≈ 85 min of sampling after the ~20 min load. comfy11.log, vt_dense1536.log.

## 2026-11-07 10:56 — 1536 dense result + pa.py attention by resolution (done)
- dense1536_cd_s1: 25 steps in 5944 s (237.7 s/step), peak 14.1 GB, total 7202 s. Bands: front 0.731, back 0.820, sides 0.790/0.842.
- vs sparse1536_s1: 155.3 s/step, 5129 s, front 0.749. Both are clean at 1536; dense is 53% slower.
- pa.py (backup pa.py.bak-attn-20261107): DENSE_MAX_RES = 1024. texture() sets attention on 18/20:
  comfy_default for res <= 1024, ultratex_sparse for 1536/2048. Syntax-checked.
- ComfyUI stopped (PID 3659900, SIGTERM), VRAM 0.11 GiB, no leftover processes.

## 2026-11-07 11:05 — tex6: full pa.py texture at 1024 (dense via DENSE_MAX_RES), running
- tex6_run.py: pa.texture(vampire_chestplate, a7/meshes/vampire_chestplate_LOD0.glb, 1024), seed pinned to tex5's 84262749.
- Compare with tex5 (sparse, 3481 s, front band score 1.913 on views). Logs: comfy12.log, tex6.log. Output: ComfyUI/output/UltraTex/vampire_chestplate_*.

## 2026-11-07 11:50 — tex6 result (full pa.py texture, 1024 dense)
- exit 0, prompt 45:19 (tex5 sparse 57:59). Both samplers attention=comfy_default, 35.6 s/step, peak 13.3 GB (tex5 53 s/step, 7.5 GB).
- Output: UltraTex/vampire_chestplate_00005_.glb, views_00004, normals_00025-30.
- Views band score: front 0.731 back 0.748 sides 0.777/0.770 (tex5 1.913/0.932/0.830/0.820; ref 0.884). Same as views_test dense1024.
- tex6_front.png / tex5_vs_tex6_front.png: horizontal bands gone; dark plate, ornament + centre gem readable. Remaining faceted shard patches = mesh/confetti-UV issue noted 06:20, not attention.
- ComfyUI (pid 104593) stopped.

## 11:55 production upright rebuild (user consent "so start")
- Backup of current production: overnight/gameassets-backup-20261107 (chestplate + necklace + build logs).
- pa.py asset vampire_chestplate 3D/vampire_chestplate_00002_.glb and medallion_necklace 3D/medallion_necklace_00001_.glb, --source-up auto default. Logs overnight/upright_<name>.log.
- Note: same Pixal3D source meshes, so the shard/hole faces around the gems stay; this fixes orientation only.

### result (rebuild done)
- both exit 0; chestplate 2:17, necklace 3:24. asset_report source_up "auto".
- LOD0 extents (x,y,z) new vs old: chestplate [0.593 0.773 0.333] vs [0.593 0.333 0.773]; necklace [0.564 0.911 0.513] vs [0.564 0.513 0.911]. Now tall on +Y, min y ~0 (on ground). Faces unchanged (19998 / 19912). Matches a7.
- rep.py: chestplate cov 0.4315 isl 3183 subpx 4 (old 0.4397/3099/4); necklace cov 0.4478 isl 3214 subpx 63 (old 0.4516/3219/59). Same issues as before.
- note: the log has no "PREP source-up z" line; orientation verified from bounds instead.
- no leaked blender -b (only mcp-for-blender 424828).
- shards around gems remain: same source mesh.

## 12:10 reroll (user: "regenerate with a different seed")
- QA of current sources: chestplate 00002 score 1.332 (best of 00002..00007, only 149 frags) - but QA doesn't see the gem shards.
  necklace 00001 score 0.633 (IoU 0.60, 2271 frags, left view IoU 0.43) -> clearly worth rerolling.
- raw_cmp/chest_montage.png (render_raw.py, grey, upright): 00002 rough all over, blobs instead of skulls/gem, no medallion disc;
  00003/05/07 (older rerolls, same views) much cleaner with medallion disc; 05/07 have flat faceted patches in the disc; 03 clean disc.
- ComfyUI started (task bk4zjqfbi, log comfy_regen.log). STOP it after by PID.
- PA_NO_FIX=1 pa.py mesh medallion_necklace --tries 3; then vampire_chestplate --tries 2 (raw only; no GameAssets writes). logs regen_*.log.
- note: pa.py mesh updates PixelArtistry/<name>.run.json mesh record.

### reroll result (13:35)
- necklace (47 min): 00002 seed 1223348551 0.757 | 00003 seed 2085665171 0.765 (pa.py "best") | 00004 seed 1306496631 0.730. old 00001 0.633.
- chestplate (45 min): 00008 seed 911786298 1.211 (two stray chips widen bbox to 0.99 m) | 00009 seed 138990498 1.247. old 00002 1.332.
- ComfyUI stopped (PID 431348, comm python3.12). run.json mesh records now point at necklace 00003 / chestplate 00009.
- renders raw_cmp/chest_montage2.png, neck_montage.png:
  chest 00009 = cleanest + most faithful (disc, bat-wing plates, clasp under disc, no flat facets). 00003 second.
  neck 00002 = cleanest frame, hexagram right (small bump grid in centre). 00003 (top score) has a wrong sun symbol + ribbon chain. 00004 rougher frame. 00001 shredded frame/spike.
- picks: chestplate 00009, necklace 00002. Production rebuild NOT run (needs consent).

## 14:00 production rebuild from reroll picks (user: "yes, rebuild both with 00009 and 00002")
- Backup of upright builds: overnight/gameassets-backup-20261107-reroll.
- overnight/reroll_build.sh: pa.py asset chestplate 3D/vampire_chestplate_00009_.glb, then necklace 3D/medallion_necklace_00002_.glb. Logs overnight/reroll_<name>.log.

### result (14:10)
- both exit 0: chestplate 2:48, necklace 2:37. status review_required, technical_passed true, the same 3 standard notes (scale_unverified, subpixel_islands, surface_review). options.source_up auto.
- LOD0: chestplate ext [0.576 0.768 0.333] min y 0, 19998 faces; necklace ext [0.552 0.915 0.507] min y 0, 19998 faces. Upright on +Y.
- previews: raw_cmp/reroll_prod_previews.png, reroll_neck_6views.png. Chestplate clean, medallion disc, no gem shards. Necklace frame clean, hexagram present.
- pre-existing quirk (old upright build the same, raw_cmp/old_upright_00_03.png): the necklace star faces the opposite way to the chestplate front (star in preview high_03, chestplate front in high_00). Needs a 180° turn to match. Not changed.
- no leaked blender -b (only mcp-for-blender 424828).

## 14:55 necklace rotated 180° (user consent)
- pa.py unchanged. Source copy rotated 180° about raw Z (content up): overnight/rot180.py -> overnight/rot180/medallion_necklace_00002_rot180.glb (generator still trimesh, so source-up auto=z).
- Backup of previous build: overnight/gameassets-backup-20261107-rot180/medallion_necklace
- Rebuild: exit 0, wall 2:37.7; review_required, validation_passed True, same 3 standard notes; LOD0 0.552x0.915x0.507, min y 0, 19998 faces.
- Check: raw_cmp/rot180_check.png — star now in high_00 (same view as chestplate front), plain back in high_03.
- No leaked processes (only mcp-for-blender 424828).

## 15:25 pa.py --yaw added (user consent)
- `--yaw DEG` in mesh_config.add_options → shared by `pa.py asset/all/mesh` (via parse_asset → build_asset.py) and `prep/fix` (prep_mesh.py). Default 0. Positive = CCW seen from above.
- prep_mesh.import_mesh(yaw=): turn about world Z applied after the source-up stand-up, before transform_apply. Logged as `PREP yaw N`. Recorded in asset_report options.yaw.
- Also added "yaw" to PA_LEGACY_PREP allowed set in pa.py.
- Backup: overnight/pa-backup-20261107-yaw/ (mesh_config, prep_mesh, build_asset, pa).
- Verified: parse 0/180/-90, nan rejected; Blender import of original 00002 with yaw=180 == rot180 copy with yaw=0 (153431 verts, max diff 3e-8). tests/test_pipeline.py 8 passed. The cattrs/register_class tracebacks also appear in the production build log, so they were there before.
- Equivalent rebuild now: `pa.py asset medallion_necklace /mnt/ssd/ComfyUI/output/3D/medallion_necklace_00002_.glb --yaw 180` (not run; the current build from the rot180 copy is geometrically identical).

## 15:30 "add 1-7" (user consent for all seven)
- 7 checked, not a bug: each LOD has <lod>.report.json stub (unwrap smart, exported, validated) → texture() skips re-prep; xatlas UVs kept.
- 6 checked, not a bug: PREP source-up z is in GameAssets/<name>.build.log; terminal only echoes ASSET/PREP WARNING lines.
- 5 cause: `pa.py asset` never wrote run.json. Added rt.pick() (pa_runtime.py) + record in pa.py asset CLI. Unit test test_hand_pick_becomes_the_recorded_reconstruction. Backups *.bak-pick.
- 3: Blender test test_yaw_turns_about_up_after_standing_upright (15/15 OK). Unit 15+22 OK.
- 4: README row, GAME_ASSET_PIPELINE note, CHANGES.md section.
- 2: --size-meters already existed. Necklace rebuild: pa.py asset medallion_necklace 3D/..._00002_.glb --yaw 180 --size-meters 0.45 → overnight/necklace_yaw_rebuild.log. Old build backed up to overnight/backup_necklace_rot180/.
- 1: ComfyUI started (comfy13.log). tex7: pa.py texture vampire_chestplate 1024 → tex7_chestplate.log. Necklace texture after rebuild. STOP ComfyUI after by PID.
- 15:32 necklace rebuild OK: PREP yaw 180.0 in build log; report source 3D/..._00002_.glb, yaw 180, size 0.45 (scale 0.491); run.json mesh → 00002 picked, asset recorded. Bounds = old rot180 build × 0.491 (same facing). Issues left: subpixel_islands, surface_review.
- tex8 (necklace texture) chained: tex7_exit.sh writes tex7_chestplate.exit; tex8_chain.sh waits for it, runs only if exit 0 → tex8_necklace.log / .exit. Then STOP ComfyUI by PID.

## 16:20 texture runs
- tex7 chestplate UltraTex 1024: exit 0, 2696 s -> UltraTex/vampire_chestplate_00006_.glb (basecolor + MR 2048², on production xatlas UVs). Views: upright, medallion + red gem on front; back view also got a medallion (UltraTex invents a second front).
- Chain bug: tex7_exit.sh copied the harness line "[exited with code 0]" but tex8_chain.sh grepped "^exit 0" -> necklace never started. Started it by hand 16:17 (wrapper PID 1737059, python 1737066), detached, writes tex8_necklace.exit.

## 16:39 necklace texture + facing check
- tex8 necklace UltraTex 1024: exit 0, ~22 min -> UltraTex/medallion_necklace_00001_.glb (+ _albedo, _orm, views_00001, normals). ComfyUI stopped (TaskStop bzam85avo), port 8188 free, no leftover python.
- Renders (overnight/r_grid.jpg, render_tex.py, Workbench, cols -Y/+Y/+X/-X): chestplate medallion disc at -Y, UltraTex front painted there (correct). Necklace hexagram relief at +Y, UltraTex painted the reference star flat onto the plain -Y disc -> WRONG side.
- Geometry check: current LOD0 == hand-rot180 build (median 0.18 mm vs 25 mm turned), so --yaw works; the premise was wrong.
- Root cause: asset_quality.previews angle 0 camera = center + forward(+Y, thinnest axis) -> high_00 views from +Y = asset back; high_03 = -Y = glTF front. 14:00 note compared necklace high_00 vs chestplate high_00 (chestplate high_00 = ridged back, overnight/chest_high00_03.jpg). Original 00002 (star at -Y) was correct.
- Fix needs: rebuild necklace from 00002 with --yaw 0 --size-meters 0.45, re-texture (~22 min). Optional: make high_00 the -Y front. Both await user.
- CHANGES.md corrected (backup CHANGES.md.bak-facing).

## 16:45 user: "yes, do both"
- asset_quality.previews: forward = -thin axis, so view 0 = glTF front (-Y). Backup asset_quality.py.bak-front. Test test_first_preview_is_the_gltf_front (plate + arm on +X; first version compared mean column and passed before the fix because the bbox centring cancels it -> rewritten to check which edge the arm sticks out of; failed before, passes after). Blender 16/16, unit 46/46 (system py, test_parts skipped: no trimesh), test_parts 8/8 in ComfyUI env.
- Docs: GAME_ASSET_PIPELINE.md previews line (bak-front), CHANGES.md.
- Necklace rebuild --yaw 0 --size-meters 0.45: exit 0, 2:38. PREP yaw 0.0, review_required, ext 0.271x0.449x0.249. vs yaw180 build: turned 0.15 mm / same 25 mm. high_00 = hexagram (overnight/neck_yaw0_high00_03.jpg). Backup overnight/backup_necklace_yaw180/ (dir, build.log, run.json).
- ComfyUI started (bg b3vuugqvg, comfy14.log). tex9 necklace texture started 16:50, wrapper PID 1934154 -> tex9_necklace.exit.

## 17:15 necklace tex9 done
- pa.py texture medallion_necklace 1024 → exit 0, wall 22:24 → UltraTex/medallion_necklace_00002_.glb (+_albedo/_orm, views_00002, normals 9-12).
- render_tex.py TEXTURE → rt_neck9_grid.jpg: front (−Y) hexagram texture on hexagram relief = reference; back plain disc. BOUNDS (-0.136,-0.125,0)-(0.136,0.124,0.45).
- ComfyUI (b3vuugqvg) stopped; :8188 free; no leftover python/blender jobs.
- 00001 (yaw-180 build) superseded. Chestplate previews still pre-fix (high_00 = back) until next rebuild.

## 17:40 --texture-from
- Added pa.py asset --texture-from (asset_bake.painted_sources + uv_triangles, build_asset hook, asset_config option); W3 default 5.01. Backups *.bak-texfrom. Tests: Blender assets 10/10, integration 16/16, unit 46/46, test_parts 8/8 (run from tests/ with LD_LIBRARY_PATH=/opt/rocm/lib), ruff clean.
- First rebuild with witcher3 default pivot source: atlas mismatch (2503 vs 2522 charts). With --pivot base: matches. Premise verified: generic LOD0 vs UltraTex UV compare maxd 0.
- Rebuilt necklace (3:50) and chestplate (3:45) as witcher3 --pivot base with UltraTex 00002/00006. Renders rt_neckW3_grid.jpg, rt_chestW3_grid.jpg, rt_chest_lod_cmp.jpg. Old packages in backup_*_generic.
- Chestplate LOD2 grey shards pre-exist in the generic LOD2 (decimation).

## 18:35 LOD budget fix + chestplate back refine
- LOD1+ budgets: every LOD0 component shrinks by the LOD ratio (weights = what each lacks after its 4-tri minimum); sqrt(area) kept for LOD0 only. Fixes chestplate LOD2 grey shards (205 studs ate the budget, plate kept ~15%). Blender assets 11/11, unit 46 OK.
- Back medallion: UltraTex masked refine (chest_backfix/run_backfix.py, back view edited, keep_mask 0 there, denoise .65). Pass 1 859 s; pass 2 running. Packages not yet rebuilt with the LOD fix.
- 18:38 refine #1 (denoise .65) exit 0: medallion+gem gone but the masked area stayed my flat dark fill (mean |new−edit| 3.3/255 in mask). Cause: flow schedule at t≤.65 = last 13/25 steps, structure already fixed; a flat init stays flat. Output `UltraTex/vampire_chestplate_backfix_00001_.glb` rejected.
- 18:45 refine #2: DENOISE=0.9 → run2.log.
- 19:23 refine #2 (denoise .9, 21/25 steps) exit 0: still flat (in-mask |new−edit| 3.74, run1↔run2 3.62). Premise "too few steps" was wrong. Back-view normals show a smooth round boss in the geometry; sigil/runes/gem were paint only. RePaint keeps the masked area within ~4/255 of its init at any denoise, so the init decides the look. `_00002_` rejected.
- 19:35 refine #3: init `view2_edit2.png` = blurred plate colour (non-stroke pixels, σ30) + procedural multi-scale grain at the plate's std 6 + faint scratches; BACK_EDIT env in run_backfix.py (.bak-edit2). DENOISE .65 → run3.log.
- 20:05 refine #3 exit 0 → `UltraTex/vampire_chestplate_backfix_00003_.glb`. Back disc: 0 red px, in-mask |new−edit| 5.4, lum std 6.2 (edit 6.4); `back_compare3.png`. ComfyUI stopped (PID 2272646, comm checked).
- 20:10 chestplate rebuilt W3 --pivot base --texture-from backfix_00003 (4:00, miss 0). Necklace rebuilt (3:53, miss 0). Backups: backup_vampire_chestplate_w3_00006, backup_medallion_necklace_w3_prelodfix.
- LOD folds (reversed area vs LOD0, `lodfold/`): chest LOD2 33→21%, necklace LOD2 24.5→10.4%; LOD3 unchanged ~33–37%. MeshLab quadric (preservenormal on/off) 44% — not a decimator bug; thin two-sided shell at a ~1.4k-tri/side budget. At 135 px (LOD2 switch size) new LOD2 ≈ LOD0 (`lod2_ingame_size.png`). LOD3 > LOD2 count on chest (erased studs kept whole) — open.
- Tests: blender_assets + blender_integration OK; unittest discover 51 OK (ComfyUI env + LD_LIBRARY_PATH=/opt/rocm/lib).

## 2026-11-07 20:45 — LOD3 > LOD2 fixed
- reduce_part aim `max(4, target-1)` (was `max(1, target-1)`): closed 4-tri minimums were erased (2 coincident faces) and restored whole. LOD0 unchanged; atlas check passes.
- Chestplate `--lod-ratios 1,.5,.35,.15`: LOD1-3 9,888/6,906/4,496 tris (was 10,122/5,624/5,734), folds 3.8/8.9/33.5%. Necklace: 9,854/4,928/2,884 (was 10,160/5,792/4,392). Miss 0 everywhere.
- Tests: blender_assets OK (new closed-part test), blender_integration 16 OK, unittest 51 OK.
- Leftover temp dirs from the stopped first-attempt builds: GameAssets/medallion_necklace.building__9o1gkxm, vampire_chestplate.building_jh82c09u (not deleted).

## 2026-11-07 20:55 — cleanup
- Deleted: 2 `*.building_*` temp dirs, `GameAssets/{vampire_chestplate,medallion_necklace}.previous` (byte-identical to backup_*_w3_backfix/_lodfix), 7 generic-engine backups, backup_medallion_necklace_w3_prelodfix, backup_vampire_chestplate_w3_00006.
- Kept: backup_vampire_chestplate_w3_backfix, backup_medallion_necklace_w3_lodfix (rollback for LOD3 fix), vampire_chestplate_ab(.previous) untouched.
- LOD before/after clay sheets: lod3/look/*_before_after.png

## 2026-11-07 21:35 — necklace stray sliver removed
- Sliver = source island of 1628 tris, 0.273 (source units) from the main body; only far island. Removed by buffer edit (sliver/drop_island.py; Blender glTF re-export split every vertex, rejected) -> 3D/medallion_necklace_00002_nosliver.glb (383 islands, main unchanged).
- Chain sliver/chain.sh: build -> pa.py texture 1024 (23 min, UltraTex/medallion_necklace_00003_.glb) -> build --texture-from. Exit 0, ComfyUI stopped by PID.
- Result: 240 components, y extent ±0.052 (was ±0.125, pivot was 7 cm off), collision box depth 0.105 (was 0.249), LOD tris 19998/9854/4928/2826, projection miss 0 all LODs, same 5 review flags.
- New paint: front good (red centre glyph); BACK disc now plain grey (old paint had an engraved sigil). Renders sliver/necklace_sliver_before_after.png, back_front_crop.png.
- Rollback: backup_medallion_necklace_w3_sliver/ (+ old paint UltraTex/medallion_necklace_00002_.glb, source 00002_.glb untouched).

## 2026-11-07 21:50 — --detail-spec + `pa.py prompts` dry run
pa_prompt_support.py: --detail-spec JSON (large/medium/small/materials/views{front,left,back,right}/avoid), validated at load; detail block appended per stage; separate side/back views get only large+materials+own view notes; avoid appended to negative (auto CFG 1.5). prompt_fingerprint() recorded on front/views stages so --resume can't reuse images from other prompts (None when unset = old records still reusable).
pa.py: view=view passed in views(); new `prompts` command (dry run, no ComfyUI). Example: examples/detail_spec_example.json.
Verified: no-spec output identical to old module (3 option sets x front/sheet); bad specs rejected; dry run -> detail_prompts_dryrun.txt. No GPU run yet.
Backups: pa.py.bak-detail, pa_prompt_support.py.bak-detail.

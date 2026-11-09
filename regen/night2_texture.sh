#!/usr/bin/env bash
# Retry of steps 3 only (texturing) from night_2026-11-08.sh, 2026-11-09 00:5x.
# Overnight 2026-11-08 (user OK'd: "after testing doing texturing"):
# 1. Loopcut local evals --no-skills on Strata (A/B against the skills run)
# 2. stop Strata (by PID, comm checked) - it cannot share the GPU with ComfyUI
# 3. ComfyUI + UltraTex 1536 (2048 ran out of memory twice on 2026-11-08) for the Loopcut-smoothed cuirass and the
#    pendant, each followed by the asset rebuild with --texture-from (same source and geometry options as the build
#    that was painted, see GAME_ASSET_PIPELINE.md "Final texture from UltraTex")
set -uo pipefail
W=/mnt/ssd/work/regen
KIT=/mnt/ssd/work/pixal3d-mv
GA=/mnt/ssd/ComfyUI/output/GameAssets
UT=/mnt/ssd/ComfyUI/output/UltraTex
LOG=$W/night.log
export PA_TEXTURE_MEMORY_FACTOR=16   # retry: 12 (auto) left the desktop without VRAM and died on hipErrorUnknown
CLEAN_PATH=$(echo "$PATH" | tr : '\n' | grep -v '.local/bin' | paste -sd:)
step() { echo "$(date '+%m-%d %H:%M:%S') $*" >> "$LOG"; }
fail() { step "FAILED: $*"; exit 1; }

step "retry texturing, PA_TEXTURE_MEMORY_FACTOR=$PA_TEXTURE_MEMORY_FACTOR"
# ---- 3. ComfyUI
pgrep -x witcher3.exe >/dev/null && fail "witcher3.exe running"
cd "$KIT" || fail cd
./launch_comfy_qwen.sh > "$W/night_comfy2.log" 2>&1 &
COMFY=$!
stop_comfy() {
  if [ -r "/proc/$COMFY/comm" ]; then kill "$COMFY"; step "ComfyUI $COMFY stopped"; fi
}
trap stop_comfy EXIT
for _ in $(seq 120); do curl -sf http://127.0.0.1:8188/system_stats >/dev/null && break; sleep 5; done
curl -sf http://127.0.0.1:8188/system_stats >/dev/null || fail "ComfyUI did not come up"
step "ComfyUI up ($COMFY)"

# views-name | asset name | LOD0 to paint | asset source | geometry flags of the painted build
paint() {
  local views=$1 asset=$2 lod0=$3 src=$4; shift 4
  local before painted
  mkdir -p "$W/pre-paint"
  [ -e "$W/pre-paint/$asset" ] || cp -a "$GA/$asset" "$W/pre-paint/$asset" || fail "$asset backup"
  step "$asset: UltraTex 1536 on $lod0"
  before=$(ls "$UT" | grep -E "^${views}_[0-9]+_\.glb$" | sort | tail -1)
  PATH=$CLEAN_PATH PA_MAX_WAIT=21600 /usr/bin/python3 pa.py texture "$views" "$lod0" 1536 > "$W/night2_$asset.texture.log" 2>&1 \
    || { step "FAILED: $asset texture"; return 1; }
  painted=$(ls "$UT" | grep -E "^${views}_[0-9]+_\.glb$" | sort | tail -1)
  [ -n "$painted" ] && [ "$painted" != "$before" ] || { step "FAILED: $asset: no new UltraTex GLB"; return 1; }
  step "$asset: painted $painted"
  PATH=$CLEAN_PATH python3 pa.py asset "$asset" "$src" "$@" --texture-from "$UT/$painted" > "$W/night2_$asset.asset.log" 2>&1 \
    || { step "FAILED: $asset asset rebuild (backup in $W/pre-paint/$asset)"; return 1; }
  step "$asset: rebuilt with paint"
}

paint vampire_chestplate_v3 vampire_chestplate_v3_lc "$GA/vampire_chestplate_v3_lc/meshes/vampire_chestplate_v3_lc_LOD0.glb" \
  /mnt/ssd/work/regen/repair/lc2_smooth_w.glb --engine witcher3 --pivot base --lod-ratios 1,.5,.35,.15
paint medallion_pendant_v3 medallion_pendant_v3 "$GA/medallion_pendant_v3/meshes/medallion_pendant_v3_LOD0.glb" \
  /mnt/ssd/ComfyUI/output/3D/medallion_pendant_v3_00005_.glb --engine witcher3 --pivot base --size-meters 0.075 --yaw 0 \
  --lod-ratios 1,.5,.25,.125
step "night done"

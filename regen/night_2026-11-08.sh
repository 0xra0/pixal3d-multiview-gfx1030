#!/usr/bin/env bash
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
CLEAN_PATH=$(echo "$PATH" | tr : '\n' | grep -v '.local/bin' | paste -sd:)
step() { echo "$(date '+%m-%d %H:%M:%S') $*" >> "$LOG"; }
fail() { step "FAILED: $*"; exit 1; }

# ---- 1. evals without skills
step "evals --no-skills"
mkdir -p /mnt/ssd/work/loopcut-local/tmp
(cd /mnt/sata/loopcut && TMPDIR=/mnt/ssd/work/loopcut-local/tmp PYTHONDONTWRITEBYTECODE=1 \
  python3 loopcut/harness/local_evals/run.py --label "IQ2_XS, no skills, vram reserve 3072" --no-skills \
  > /mnt/ssd/work/loopcut-local/eval-noskills-v1.log 2>&1) || step "evals exited non-zero (see eval-noskills-v1.log)"
step "evals done: $(tail -1 /mnt/ssd/work/loopcut-local/eval-noskills-v1.log)"

# ---- 2. stop Strata (Ctrl+C equivalent on its server, then the engine if it is left)
SRV=
for p in $(pgrep -f "serve/server.py --engine strata --config /mnt/ssd/Strata/strata-iq2_xs.json"); do
  grep -q python "/proc/$p/comm" 2>/dev/null && SRV=$p
done
if [ -n "$SRV" ]; then
  step "stopping Strata server $SRV"
  kill -INT "$SRV"
  for _ in $(seq 60); do [ -d "/proc/$SRV" ] || break; sleep 2; done
  [ -d "/proc/$SRV" ] && { kill -INT "$SRV"; sleep 10; }
fi
for p in $(pgrep -x strata) $(pgrep -x strata-vision); do
  c=$(cat "/proc/$p/comm" 2>/dev/null); [ "$c" = strata ] || [ "$c" = strata-vision ] || continue
  step "ending leftover $c $p"; kill "$p"
done
sleep 10
pgrep -x strata >/dev/null && fail "Strata engine still running"
step "Strata stopped; VRAM used $(( $(cat /sys/class/drm/card0/device/mem_info_vram_used)/1048576 )) MiB"

# ---- 3. ComfyUI
pgrep -x witcher3.exe >/dev/null && fail "witcher3.exe running"
cd "$KIT" || fail cd
./launch_comfy_qwen.sh > "$W/night_comfy.log" 2>&1 &
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
  PATH=$CLEAN_PATH PA_MAX_WAIT=21600 /usr/bin/python3 pa.py texture "$views" "$lod0" 1536 > "$W/night_$asset.texture.log" 2>&1 \
    || { step "FAILED: $asset texture"; return 1; }
  painted=$(ls "$UT" | grep -E "^${views}_[0-9]+_\.glb$" | sort | tail -1)
  [ -n "$painted" ] && [ "$painted" != "$before" ] || { step "FAILED: $asset: no new UltraTex GLB"; return 1; }
  step "$asset: painted $painted"
  PATH=$CLEAN_PATH python3 pa.py asset "$asset" "$src" "$@" --texture-from "$UT/$painted" > "$W/night_$asset.asset.log" 2>&1 \
    || { step "FAILED: $asset asset rebuild (backup in $W/pre-paint/$asset)"; return 1; }
  step "$asset: rebuilt with paint"
}

paint vampire_chestplate_v3 vampire_chestplate_v3_lc "$GA/vampire_chestplate_v3_lc/meshes/vampire_chestplate_v3_lc_LOD0.glb" \
  /mnt/ssd/work/regen/repair/lc2_smooth_w.glb --engine witcher3 --pivot base --lod-ratios 1,.5,.35,.15
paint medallion_pendant_v3 medallion_pendant_v3 "$GA/medallion_pendant_v3/meshes/medallion_pendant_v3_LOD0.glb" \
  /mnt/ssd/ComfyUI/output/3D/medallion_pendant_v3_00005_.glb --engine witcher3 --pivot base --size-meters 0.075 --yaw 0 \
  --lod-ratios 1,.5,.25,.125
step "night done"

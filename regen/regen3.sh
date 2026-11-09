#!/usr/bin/env bash
# Premise test: same cuirass views and seed as v3 try 1, left/right images exchanged so each side image goes to the
# Pixal3D camera that actually sees that side (az90 +X sees the object's left).
set -uo pipefail
W=/mnt/ssd/work/regen; KIT=/mnt/ssd/work/pixal3d-mv
CLEAN_PATH=$(echo "$PATH" | tr : '\n' | grep -v '.local/bin' | paste -sd:)
step() { echo "$(date '+%m-%d %H:%M:%S') $*" >> "$W/regen.log"; }
pgrep -x witcher3.exe >/dev/null && { step "lr test: witcher3.exe running"; exit 1; }
cd "$KIT" || exit 1
rm -f "$W/regen3.exit"
step "lr test: start ComfyUI"
./launch_comfy_qwen.sh > "$W/comfy3.log" 2>&1 &
COMFY=$!
stop_comfy() { if [ -r "/proc/$COMFY/comm" ] && grep -q python "/proc/$COMFY/comm"; then kill "$COMFY"; step "lr test: ComfyUI $COMFY stopped"; fi; }
trap stop_comfy EXIT
for _ in $(seq 120); do curl -sf http://127.0.0.1:8188/system_stats >/dev/null && break; sleep 5; done
PATH=$CLEAN_PATH PA_MAX_WAIT=14400 python3 pa.py mesh vampire_chestplate_v3lr 1777044552 --tries 1 \
  --engine witcher3 --pivot base --lod-ratios 1,.5,.35,.15 > "$W/vampire_chestplate_v3lr.log" 2>&1
rc=$?
step "lr test: pa.py mesh exit $rc"
echo "exit $rc" > "$W/regen3.exit"

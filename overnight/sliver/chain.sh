#!/usr/bin/env bash
# Necklace without the stray sliver: build -> UltraTex paint -> rebuild with the paint.
set -uo pipefail
S=/mnt/ssd/work/overnight/sliver
SRC=/mnt/ssd/ComfyUI/output/3D/medallion_necklace_00002_nosliver.glb
KIT=/mnt/ssd/work/pixal3d-mv
CLEAN_PATH=$(echo "$PATH" | tr : '\n' | grep -v '.local/bin' | paste -sd:)
FLAGS=(--engine witcher3 --pivot base --size-meters 0.45 --yaw 0)
step() { echo "$(date +%H:%M:%S) $*" >> "$S/chain.log"; }
fail() { step "FAILED: $*"; echo "exit 1" > "$S/chain.exit"; exit 1; }

pgrep -x witcher3.exe >/dev/null && fail "witcher3.exe running"
cd "$KIT" || fail cd

step "build 1 (no paint)"
PATH=$CLEAN_PATH python3 pa.py asset medallion_necklace "$SRC" "${FLAGS[@]}" > "$S/build1.log" 2>&1 || fail "build 1"

step "start ComfyUI"
./launch_comfy_qwen.sh > "$S/comfy.log" 2>&1 &
COMFY=$!
echo "$COMFY" > "$S/comfy.pid"
stop_comfy() {
  if [ -r "/proc/$COMFY/comm" ] && grep -q python "/proc/$COMFY/comm"; then kill "$COMFY"; step "ComfyUI $COMFY stopped"; fi
}
trap stop_comfy EXIT
for _ in $(seq 120); do curl -sf http://127.0.0.1:8188/system_stats >/dev/null && break; sleep 5; done
curl -sf http://127.0.0.1:8188/system_stats >/dev/null || fail "ComfyUI did not come up"

step "UltraTex texture"
before=$(ls /mnt/ssd/ComfyUI/output/UltraTex/medallion_necklace_*_.glb 2>/dev/null | sort | tail -1)
PA_MAX_WAIT=14400 /usr/bin/python3 pa.py texture medallion_necklace 1024 > "$S/texture.log" 2>&1 || fail texture
stop_comfy; trap - EXIT
painted=$(ls /mnt/ssd/ComfyUI/output/UltraTex/medallion_necklace_*_.glb | sort | tail -1)
[ "$painted" != "$before" ] || fail "no new UltraTex GLB"
step "painted $painted"

step "build 2 (--texture-from)"
PATH=$CLEAN_PATH python3 pa.py asset medallion_necklace "$SRC" "${FLAGS[@]}" --texture-from "$painted" > "$S/build2.log" 2>&1 || fail "build 2"
step done
echo "exit 0" > "$S/chain.exit"

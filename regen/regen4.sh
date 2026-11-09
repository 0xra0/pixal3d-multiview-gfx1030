#!/usr/bin/env bash
# v4: regenerate the v3 cuirass and pendant meshes after the side-camera fix (judged, 4 tries each).
# separate true views + detail spec -> Pixal3D mesh (3 tries, best kept) -> asset -> UltraTex 2048 -> asset with paint.
set -uo pipefail
W=/mnt/ssd/work/regen
KIT=/mnt/ssd/work/pixal3d-mv
IN=/mnt/ssd/ComfyUI/input
CLEAN_PATH=$(echo "$PATH" | tr : '\n' | grep -v '.local/bin' | paste -sd:)
step() { echo "$(date '+%m-%d %H:%M:%S') $*" >> "$W/regen.log"; }
fail() { step "FAILED: $*"; echo "exit 1" > "$W/regen.exit"; exit 1; }

pgrep -x witcher3.exe >/dev/null && fail "witcher3.exe running"
cd "$KIT" || fail cd

rm -f "$W/regen.exit"
step "start ComfyUI"
./launch_comfy_qwen.sh > "$W/comfy.log" 2>&1 &
COMFY=$!
echo "$COMFY" > "$W/comfy.pid"
stop_comfy() {
  if [ -r "/proc/$COMFY/comm" ] && grep -q python "/proc/$COMFY/comm"; then kill "$COMFY"; step "ComfyUI $COMFY stopped"; fi
}
trap stop_comfy EXIT
for _ in $(seq 120); do curl -sf http://127.0.0.1:8188/system_stats >/dev/null && break; sleep 5; done
curl -sf http://127.0.0.1:8188/system_stats >/dev/null || fail "ComfyUI did not come up"

# name | approved front | short description | spec | asset flags
# mode all: views + mesh + asset; mode mesh: the views in ComfyUI/input/<name>_views are kept (already checked)
build() {
  local mode=$1 name=$2 front=$3 desc=$4 spec=$5; shift 5
  step "$name: $mode"
  if [ "$mode" = paint ]; then
    :   # views and mesh already recorded in PixelArtistry/<name>.run.json
  elif [ "$mode" = mesh ]; then
    PATH=$CLEAN_PATH PA_MAX_WAIT=14400 python3 pa.py mesh "$name" --tries ${TRIES:-3} "$@" > "$W/$name.all.log" 2>&1 \
      || fail "$name mesh"
  else
    PATH=$CLEAN_PATH PA_MAX_WAIT=14400 python3 pa.py all "$name" "$front" "$desc" --separate-views --tries ${TRIES:-3} \
      --detail-spec "$spec" "$@" > "$W/$name.all.log" 2>&1 || fail "$name all"
  fi
  local raw
  raw=$(/usr/bin/python3 -I -c "import json,sys; print(json.load(open(sys.argv[1]))['stages']['mesh']['outputs'][0])" \
        "/mnt/ssd/ComfyUI/output/PixelArtistry/$name.run.json") || fail "$name: no mesh record"
  step "$name: mesh $raw"
  if [ "${NO_PAINT:-0}" = 1 ]; then step "$name: mesh only (NO_PAINT=1), paint later"; return; fi

  step "$name: UltraTex ${TEX_RES:-2048}"
  local before painted
  before=$(ls /mnt/ssd/ComfyUI/output/UltraTex/ | grep -E "^${name}_[0-9]+_\.glb$" | sort | tail -1)
  PATH=$CLEAN_PATH PA_MAX_WAIT=14400 /usr/bin/python3 pa.py texture "$name" "${TEX_RES:-2048}" > "$W/$name.texture.log" 2>&1 \
    || fail "$name texture"
  painted=$(ls /mnt/ssd/ComfyUI/output/UltraTex/ | grep -E "^${name}_[0-9]+_\.glb$" | sort | tail -1)
  [ -n "$painted" ] && [ "$painted" != "$before" ] || fail "$name: no new UltraTex GLB"
  step "$name: painted $painted"

  step "$name: asset with paint"
  PATH=$CLEAN_PATH python3 pa.py asset "$name" "$raw" "$@" --texture-from "/mnt/ssd/ComfyUI/output/UltraTex/$painted" \
    > "$W/$name.asset.log" 2>&1 || fail "$name asset"
  step "$name: done"
}

# after the side-camera fix (pa.generate feeds left.png to az90): views already checked, mesh only
export TRIES=4 NO_PAINT=1
build mesh vampire_chestplate_v3 - - - --engine witcher3 --pivot base --lod-ratios 1,.5,.35,.15
build mesh medallion_pendant_v3 - - - --engine witcher3 --pivot base --size-meters 0.075 --yaw 0
step "all done"
echo "exit 0" > "$W/regen.exit"

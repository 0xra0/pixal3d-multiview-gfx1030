#!/usr/bin/env bash
# The asset atlas is not reproducible run to run (bmesh element sets ordered by memory address in
# prep_mesh.repair / closed_boundaries, found 2026-11-09). pa.py asset --texture-from refuses a build whose LOD0
# atlas differs from the painted one, before anything is written, so retrying the same command until one run lands
# on the painted atlas is safe. usage: rebuild_until_match.sh <tries> <asset> <src> <painted.glb> [asset flags...]
set -uo pipefail
tries=$1 asset=$2 src=$3 painted=$4; shift 4
W=/mnt/ssd/work/regen
CLEAN_PATH=$(echo "$PATH" | tr : '\n' | grep -v '.local/bin' | paste -sd:)
cd /mnt/ssd/work/pixal3d-mv || exit 1
for i in $(seq "$tries"); do
  echo "$(date '+%m-%d %H:%M:%S') $asset: rebuild try $i/$tries" >> "$W/night.log"
  if PATH=$CLEAN_PATH python3 pa.py asset "$asset" "$src" "$@" --texture-from "$painted" > "$W/rebuild_${asset}_$i.log" 2>&1; then
    echo "$(date '+%m-%d %H:%M:%S') $asset: rebuilt with paint on try $i" >> "$W/night.log"
    exit 0
  fi
  grep -q "different LOD0 atlas" "$W/rebuild_${asset}_$i.log" || {
    echo "$(date '+%m-%d %H:%M:%S') FAILED: $asset rebuild try $i, not an atlas mismatch (see rebuild_${asset}_$i.log)" >> "$W/night.log"
    exit 1; }
done
echo "$(date '+%m-%d %H:%M:%S') FAILED: $asset: no atlas match in $tries tries" >> "$W/night.log"
exit 1

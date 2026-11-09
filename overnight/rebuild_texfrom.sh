#!/bin/sh
# Rebuild both packages as Witcher 3 targets with the UltraTex texture baked into every LOD.
cd /mnt/ssd/work/pixal3d-mv
export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v "$HOME/.local/bin" | paste -sd:)
U=/mnt/ssd/ComfyUI/output/UltraTex
S=/mnt/ssd/ComfyUI/output/3D
date +%T; /usr/bin/time -f "WALL %E" python3 pa.py asset medallion_necklace $S/medallion_necklace_00002_.glb --engine witcher3 --pivot base --size-meters 0.45 --yaw 0 --texture-from $U/medallion_necklace_00002_.glb; echo "EXIT necklace $?"
date +%T; /usr/bin/time -f "WALL %E" python3 pa.py asset vampire_chestplate $S/vampire_chestplate_00009_.glb --engine witcher3 --pivot base --texture-from $U/vampire_chestplate_00006_.glb; echo "EXIT chestplate $?"
date +%T

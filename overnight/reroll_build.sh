#!/bin/sh
export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v "$HOME/.local/bin" | paste -sd:)
cd /mnt/ssd/work/pixal3d-mv
O=/mnt/ssd/work/overnight
/usr/bin/time -f "wall %E" python3 pa.py asset vampire_chestplate /mnt/ssd/ComfyUI/output/3D/vampire_chestplate_00009_.glb > $O/reroll_vampire_chestplate.log 2>&1
echo "chest exit $?" >> $O/reroll_vampire_chestplate.log
/usr/bin/time -f "wall %E" python3 pa.py asset medallion_necklace /mnt/ssd/ComfyUI/output/3D/medallion_necklace_00002_.glb > $O/reroll_medallion_necklace.log 2>&1
echo "neck exit $?" >> $O/reroll_medallion_necklace.log

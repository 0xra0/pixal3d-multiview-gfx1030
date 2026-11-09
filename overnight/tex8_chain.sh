#!/usr/bin/env bash
# Wait for the chestplate texture (tex7) to finish OK, then texture the necklace.
until [ -s /mnt/ssd/work/overnight/tex7_chestplate.exit ]; do sleep 20; done
grep -q "^exit 0" /mnt/ssd/work/overnight/tex7_chestplate.exit || { echo "tex7 failed; necklace not started"; exit 1; }
cd /mnt/ssd/work/pixal3d-mv && /usr/bin/python3 pa.py texture medallion_necklace 1024 > /mnt/ssd/work/overnight/tex8_necklace.log 2>&1
echo "exit $?" > /mnt/ssd/work/overnight/tex8_necklace.exit

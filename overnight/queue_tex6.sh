#!/usr/bin/env bash
cd /mnt/ssd/work/overnight
until curl -sf http://127.0.0.1:8188/system_stats >/dev/null; do sleep 5; done
export PA_MAX_WAIT=14400
LD_LIBRARY_PATH=/opt/rocm/lib /mnt/ssd/conda-envs/ComfyUI/bin/python3.12 -I tex6_run.py > tex6.log 2>&1; echo "exit $?" >> tex6.log

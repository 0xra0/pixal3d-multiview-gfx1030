#!/usr/bin/env bash
# 2048 dense (comfy_default) albedo view test, same seed/mesh as the 512/1024/1536 runs.
cd /mnt/ssd/work/overnight
until curl -sf http://127.0.0.1:8188/system_stats >/dev/null; do sleep 5; done
export PA_MAX_WAIT=28800
PY=/mnt/ssd/conda-envs/ComfyUI/bin/python3.12
LD_LIBRARY_PATH=/opt/rocm/lib $PY -I views_test.py dense2048_cd_s1 84262749 2048 attention=comfy_default > vt_dense2048.log 2>&1; echo "exit $?" >> vt_dense2048.log

#!/usr/bin/env bash
# Rerun 1536 sparse after the 22:10 crash (Loupe opened mid-kernel). mpvpaper already killed by user.
cd /mnt/ssd/work/overnight
until curl -sf http://127.0.0.1:8188/system_stats >/dev/null; do sleep 5; done
export PA_MAX_WAIT=14400
PY=/mnt/ssd/conda-envs/ComfyUI/bin/python3.12
LD_LIBRARY_PATH=/opt/rocm/lib $PY -I views_test.py sparse1536_s1 84262749 1536 > vt_sparse1536.log 2>&1; echo "exit $?" >> vt_sparse1536.log

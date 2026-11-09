#!/usr/bin/env bash
# After the GPU crash: mpvpaper is paused (SIGSTOP). Run dense1024 (comfy_default), then 1536 sparse, then resume mpvpaper.
cd /mnt/ssd/work/overnight
MPV=211079
until curl -sf http://127.0.0.1:8188/system_stats >/dev/null; do sleep 5; done
export PA_MAX_WAIT=14400
PY=/mnt/ssd/conda-envs/ComfyUI/bin/python3.12
LD_LIBRARY_PATH=/opt/rocm/lib $PY -I views_test.py dense1024_cd_s1 84262749 1024 attention=comfy_default > vt_dense1024_cd.log 2>&1; echo "exit $?" >> vt_dense1024_cd.log
LD_LIBRARY_PATH=/opt/rocm/lib $PY -I views_test.py sparse1536_s1 84262749 1536 > vt_sparse1536.log 2>&1; echo "exit $?" >> vt_sparse1536.log
[ "$(cat /proc/$MPV/comm 2>/dev/null)" = mpvpaper ] && kill -CONT $MPV

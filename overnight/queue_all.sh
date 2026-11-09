#!/usr/bin/env bash
# After reboot: wait for ComfyUI, then NAF rerun, 1024 dense, 1536 sparse, one after the other.
cd /mnt/ssd/work/overnight
until curl -sf http://127.0.0.1:8188/system_stats >/dev/null; do sleep 5; done
export PA_MAX_WAIT=14400
PY=/mnt/ssd/conda-envs/ComfyUI/bin/python3.12
wc -l comfy7.log > naf_logstart.txt
(cd /mnt/ssd/work/pixal3d-mv && PA_NO_FIX=1 $PY pa.py mesh medallion_pendant 4242) > naf_rerun.log 2>&1; echo "exit $?" >> naf_rerun.log
LD_LIBRARY_PATH=/opt/rocm/lib $PY -I views_test.py dense1024_s1 84262749 1024 topk=1.0 > vt_dense1024.log 2>&1; echo "exit $?" >> vt_dense1024.log
LD_LIBRARY_PATH=/opt/rocm/lib $PY -I views_test.py sparse1536_s1 84262749 1536 > vt_sparse1536.log 2>&1; echo "exit $?" >> vt_sparse1536.log

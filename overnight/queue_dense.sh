#!/usr/bin/env bash
# Waits for the NAF rerun to finish, then runs the 1024 dense and 1536 sparse view tests one after the other.
cd /mnt/ssd/work/overnight
until grep -q "^exit " naf_rerun.log 2>/dev/null; do sleep 15; done
export PA_MAX_WAIT=14400
PY="/mnt/ssd/conda-envs/ComfyUI/bin/python3.12 -I"
LD_LIBRARY_PATH=/opt/rocm/lib $PY views_test.py dense1024_s1 84262749 1024 topk=1.0 > vt_dense1024.log 2>&1; echo "exit $?" >> vt_dense1024.log
LD_LIBRARY_PATH=/opt/rocm/lib $PY views_test.py sparse1536_s1 84262749 1536 > vt_sparse1536.log 2>&1; echo "exit $?" >> vt_sparse1536.log

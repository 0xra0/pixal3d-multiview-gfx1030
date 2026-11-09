#!/bin/sh
# run_one_test.sh <module> <TestCase> <method>  — one Blender unittest, ~/.local/bin stripped from PATH
cd /mnt/ssd/work/pixal3d-mv
PATH=$(echo "$PATH" | tr ':' '\n' | grep -v "$HOME/.local/bin" | paste -sd:) blender -b --factory-startup --python-exit-code 1 --python-expr "
import sys,unittest; sys.argv=['x']; sys.path.insert(0,'tests'); sys.path.insert(0,'.')
import $1 as t
r=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([t.$2('$3')])); sys.exit(0 if r.wasSuccessful() else 1)" 2>&1 | grep -v "cattrs\|register_class\|^ASSET\|^\s*$\|bl_pkg"

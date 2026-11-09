#!/usr/bin/env bash
while pgrep -f "pa.py texture vampire_chestplate" >/dev/null; do sleep 10; done
tail -1 /tmp/claude-1000/-mnt-ssd-3DGenStudio/6fe39179-3eac-4040-8de1-1a5a7fdddb21/tasks/bzj10pmsv.output > /mnt/ssd/work/overnight/tex7_chestplate.exit

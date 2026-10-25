#!/bin/bash
# CRAB scriptExe: input step on the job's RAW files (PSet.py from CRAB), then the ntuple step.
set -e
cmsRun -j FrameworkJobReport.xml -p PSet.py
cmsRun step2_crab_cfg.py > step2.log 2>&1 || { tail -50 step2.log; exit 80; }

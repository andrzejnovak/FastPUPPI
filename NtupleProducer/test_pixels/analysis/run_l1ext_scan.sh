#!/bin/bash
#SBATCH --job-name=l1ext_scan
#SBATCH --partition=submit
#SBATCH --cpus-per-task=1
#SBATCH --mem=6G
#SBATCH --time=02:00:00
#SBATCH --output=slurm_logs/l1ext_scan_%A_%a.out
# Association settings scan for l1ext.py on 200 HH4b events (one setting per array task)
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh` && cd /work/submit/novaka/l1pixels/analysis
SET=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" l1ext_val/settings.txt)
F=$(ls /scratch/submit/cms/novaka/l1pixels/local_v3/perfNano_HH4b_*.root | head -1)
env NEVT=200 $SET python3 l1ext_validate.py l1ext_val/scan_${SLURM_ARRAY_TASK_ID}.json $F

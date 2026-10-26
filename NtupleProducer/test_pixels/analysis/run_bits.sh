#!/bin/bash
#SBATCH --job-name=l1pix_bits
#SBATCH --partition=submit
#SBATCH --cpus-per-task=1
#SBATCH --mem=6G
#SBATCH --time=03:00:00
#SBATCH --output=slurm_logs/bits_%A_%a.out
# Bit-budget inputs: task 0 = targeted minimum bias (official events with HT > 90), task 1 = HH4b
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh` && cd /work/submit/novaka/l1pixels/analysis
if [ "$SLURM_ARRAY_TASK_ID" = 0 ]; then
  python3 bits_budget.py bits_mb.json MinBiasSel $(ls /scratch/submit/cms/novaka/l1pixels/local_mbsel_ext/perfNano_MinBiasSel_*.root | head -40)
else
  python3 bits_budget.py bits_hh.json HH4b $(ls /scratch/submit/cms/novaka/l1pixels/local_v3/perfNano_HH4b_*.root | head -3)
fi

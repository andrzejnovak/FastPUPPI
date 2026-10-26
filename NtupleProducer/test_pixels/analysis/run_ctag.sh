#!/bin/bash
#SBATCH --job-name=l1pix_ctag
#SBATCH --partition=submit
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=slurm_logs/ctag_%j.out
# Per-jet c-tagging on QCD jets: L1 NN, + OT-only displaced tracks, + L1 tracks with pixel hits, + HLT pixel tracks
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh` && cd /work/submit/novaka/l1pixels/analysis
export OMP_NUM_THREADS=8
python3 ctag_compare.py ctag_chain.json "OT only:lists_ot_QCDFlat.npz" "L1 + pixel:lists_l1ext_QCDFlat.npz" \
  "HLT pixel:lists_v3pt15_qcd.npz"

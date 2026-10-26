#!/bin/bash
#SBATCH --job-name=l1pix_curves
#SBATCH --partition=submit
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=08:00:00
#SBATCH --output=slurm_logs/curves_%j.out
# Efficiency vs rate curves (NN, HLT pixel, L1 pixel, perfect) for the summary page
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh` && cd /work/submit/novaka/l1pixels/analysis
export OMP_NUM_THREADS=8 MB_TOTAL=1999360 HT_MIN=150
V3=/scratch/submit/cms/novaka/l1pixels/local_v3
MB=/scratch/submit/cms/novaka/l1pixels/local_mbsel_ext
NEW=/scratch/submit/cms/novaka/l1pixels/local_mbnew
python3 direct_curves.py curves.json curves_flags.npz "$V3/perfNano_HH4b_*.root" "$MB/perfNano_MinBiasSel_*.root,$NEW/perfNano_MinBiasNew_*.root" \
  offline_flags2.npz lists_v3pt15_hh4b.npz:lists_v3pt15_qcd.npz:lists_mbsel_pt15.npz:lists_mbnew_pt15.npz \
  lists_l1ext_HH4b.npz:lists_l1ext_QCDFlat.npz:lists_l1ext_MinBiasSel.npz:lists_l1ext_MinBiasNew.npz

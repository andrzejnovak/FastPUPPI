#!/bin/bash
#SBATCH --job-name=l1pix_ctagcharm
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=8
#SBATCH --mem=10G
#SBATCH --time=02:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/ctag_charm_%j.out
# Per-jet c-tag ROC with the charm-oriented pixel summary (ctag_charm.py, charm_feats.py); QCD jets, L1 tracks + pixels,
# HLT pixel tracks as reference, VBF H->cc c jets as an extra-training statistics check.
# Runs a private copy of the scripts (CLAUDE.md rule); portable venv so it also runs on the tier3 CPUs.
set -e
A=/work/submit/novaka/l1pixels/analysis
S=/scratch/submit/cms/novaka/l1pixels/derived
OUT=${OUT:-$S/ctag_charm/ctag_charm.json}
W=$(mktemp -d /tmp/ctag_charm_${SLURM_JOB_ID:-local}_XXXX)
cp $A/ctag_charm.py $A/charm_feats.py $A/charm_feats2.py $A/train_sets.py $W/
source /work/submit/novaka/tools/ana-venv/bin/activate
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-8}
cd $W
python3 $W/ctag_charm.py $OUT $S/analysis/lists_l1ext_QCDFlat.npz $S/analysis/lists_v3pt15_qcd.npz \
  "$S/l1ext_parts/VBFHCC_perfNano_VBFHCC_*.npz"
rm -rf $W
echo DONE

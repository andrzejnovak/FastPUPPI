#!/bin/bash
#SBATCH --job-name=l1pix_btagv2
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=8
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/btag_v2check_%j.out
# b tag (HH->4b b vs QCD light) with the v2 summary (btag_v2check.py); private copy of the scripts, portable venv
set -e
A=/work/submit/novaka/l1pixels/analysis
S=/scratch/submit/cms/novaka/l1pixels/derived
W=$(mktemp -d /tmp/btagv2_${SLURM_JOB_ID:-local}_XXXX)
cp $A/btag_v2check.py $A/charm_feats2.py $A/train_sets.py $W/
source /work/submit/novaka/tools/ana-venv/bin/activate
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-8}
cd $W
python3 $W/btag_v2check.py $S/ctag_charm/btag_v2check.json $S/analysis/lists_l1ext_HH4b.npz $S/analysis/lists_l1ext_QCDFlat.npz
rm -rf $W
echo DONE

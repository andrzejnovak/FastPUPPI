#!/bin/bash
#SBATCH --job-name=l1pix_perfect
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=2
#SBATCH --mem=7G
#SBATCH --time=01:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/perfect_%j.out
# Perfect-b-tag ceiling with a flavour-aware minimum-bias rate (QCD P(n_b | HT)), perfect_ceiling.py
source /work/submit/novaka/tools/ana-venv/bin/activate
A=/work/submit/novaka/l1pixels/analysis
S=/scratch/submit/cms/novaka/l1pixels
WD=$(mktemp -d /tmp/l1pix_perfect.XXXX); cp $A/*.py $WD/
cd $A
export MB_TOTAL=1999360 PYTHONPATH=$WD
python3 $WD/perfect_ceiling.py $S/derived/perfect_ceiling.json $S/derived/perfect_ceiling_flags.npz \
  "$S/local_v3/perfNano_HH4b_*.root" "$S/local_mbsel_ext/perfNano_MinBiasSel_*.root,$S/local_mbnew/perfNano_MinBiasNew_*.root" \
  "$S/local_v3/perfNano_QCDFlat_*.root" offline_flags2.npz lists_l1ext_HH4b.npz lists_l1ext_QCDFlat.npz
rm -rf $WD

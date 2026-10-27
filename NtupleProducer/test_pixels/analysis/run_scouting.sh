#!/bin/bash
#SBATCH --job-name=l1pix_scout
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=4
#SBATCH --mem=7G
#SBATCH --time=03:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/scouting_%j.out
# HH->4b at L1-object level: triggered + scouting streams, minimum-bias background, kappa_lambda interval (scouting.py)
source /work/submit/novaka/tools/ana-venv/bin/activate
A=/work/submit/novaka/l1pixels/analysis
WD=$(mktemp -d /tmp/l1pix_scout.XXXX); cp $A/*.py $WD/
cd $A  # relative list paths
# PIXSUM=v2 SUF=_v2: recalibrated L1 pixel summary, with the matching seed_plane_v2.npz (run_v2.sh task 1)
export OMP_NUM_THREADS=4 MB_TOTAL=1999360 HT_MIN=150 PYTHONPATH=$WD PIXSUM=${PIXSUM:-v1}
S=/scratch/submit/cms/novaka/l1pixels
SP=seed_plane.npz; [ -n "$SUF" ] && SP=$S/derived/analysis_v2/seed_plane$SUF.npz
python3 $WD/scouting.py $S/derived/scouting/scouting$SUF.json "$S/local_v3/perfNano_HH4b_*.root" \
  "$S/local_mbsel_ext/perfNano_MinBiasSel_*.root,$S/local_mbnew/perfNano_MinBiasNew_*.root" \
  lists_l1ext_HH4b.npz:lists_l1ext_QCDFlat.npz:lists_l1ext_MinBiasSel.npz:lists_l1ext_MinBiasNew.npz \
  $SP "$S/genmhh/mhh_*.npz" "klreweight/nano_mhh_kl*.npz"
rm -rf $WD

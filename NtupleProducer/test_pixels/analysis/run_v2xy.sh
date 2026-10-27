#!/bin/bash
#SBATCH --job-name=l1pix_v2xy
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=4
#SBATCH --mem=7G
#SBATCH --time=02:00:00
#SBATCH --array=0-1
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/v2xy_%A_%a.out
# 0 = direct_curves with the recalibrated transverse-only summary (PIXSUM=v2xy); 1 = HH signal below the HT reach
source /work/submit/novaka/tools/ana-venv/bin/activate
A=/work/submit/novaka/l1pixels/analysis
D=/scratch/submit/cms/novaka/l1pixels/derived/analysis_v2
S=/scratch/submit/cms/novaka/l1pixels
WD=$(mktemp -d /tmp/l1pix_v2xy.XXXX); cp $A/*.py $WD/
cd $A
export OMP_NUM_THREADS=4 MB_TOTAL=1999360 HT_MIN=150 PYTHONPATH=$WD PIXSUM=v2xy
HH="$S/local_v3/perfNano_HH4b_*.root"; MB="$S/local_mbsel_ext/perfNano_MinBiasSel_*.root,$S/local_mbnew/perfNano_MinBiasNew_*.root"
HLT=lists_v3pt15_hh4b.npz:lists_v3pt15_qcd.npz:lists_mbsel_pt15.npz:lists_mbnew_pt15.npz
L1=lists_l1ext_HH4b.npz:lists_l1ext_QCDFlat.npz:lists_l1ext_MinBiasSel.npz:lists_l1ext_MinBiasNew.npz
case $SLURM_ARRAY_TASK_ID in
  0) python3 $WD/direct_curves.py $D/curves_v2xy.json $D/curves_v2xy_flags.npz "$HH" "$MB" offline_flags2.npz $HLT $L1 ;;
  1) python3 $WD/hh_ht_reach.py $S/derived/scouting/hh_ht_reach.json "$HH" "$S/genmhh/mhh_*.npz" "klreweight/nano_mhh_kl*.npz" ;;
esac
rm -rf $WD

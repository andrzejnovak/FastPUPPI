#!/bin/bash
#SBATCH --job-name=l1pix_v2
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=4
#SBATCH --mem=7G
#SBATCH --time=03:00:00
#SBATCH --array=0-2
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/v2_%A_%a.out
# Page inputs with the recalibrated 3D impact-parameter summary for L1 tracks with pixel hits (PIXSUM=v2,
# charm_feats2.summary2): 0 = direct_curves (tab 1, 4), 1 = seed_plane (tabs 3, 4; feeds scouting), 2 = tag_compare (tab 3)
source /work/submit/novaka/tools/ana-venv/bin/activate
A=/work/submit/novaka/l1pixels/analysis
D=/scratch/submit/cms/novaka/l1pixels/derived/analysis_v2
S=/scratch/submit/cms/novaka/l1pixels
WD=$(mktemp -d /tmp/l1pix_v2.XXXX); cp $A/*.py $WD/
cd $A  # relative list paths
export OMP_NUM_THREADS=4 MB_TOTAL=1999360 HT_MIN=150 PYTHONPATH=$WD PIXSUM=v2
HH="$S/local_v3/perfNano_HH4b_*.root"; MB="$S/local_mbsel_ext/perfNano_MinBiasSel_*.root,$S/local_mbnew/perfNano_MinBiasNew_*.root"
HLT=lists_v3pt15_hh4b.npz:lists_v3pt15_qcd.npz:lists_mbsel_pt15.npz:lists_mbnew_pt15.npz
L1=lists_l1ext_HH4b.npz:lists_l1ext_QCDFlat.npz:lists_l1ext_MinBiasSel.npz:lists_l1ext_MinBiasNew.npz
case $SLURM_ARRAY_TASK_ID in
  0) python3 $WD/direct_curves.py $D/curves_v2.json $D/curves_v2_flags.npz "$HH" "$MB" offline_flags2.npz $HLT $L1 ;;
  1) python3 $WD/seed_plane.py $D/seed_plane_v2.npz "$HH" "$MB" $HLT $L1 ;;
  2) OFFLINE="$S/offline/HH4b_*.npz:$S/offline/QCDFlat_*.npz" python3 $WD/tag_compare.py $D/tag_chain_v2.json \
       "OT only:lists_ot_HH4b.npz:lists_ot_QCDFlat.npz" "L1 + pixel:lists_l1ext_HH4b.npz:lists_l1ext_QCDFlat.npz" \
       "HLT pixel:lists_v3pt15_hh4b.npz:lists_v3pt15_qcd.npz" ;;
esac
rm -rf $WD

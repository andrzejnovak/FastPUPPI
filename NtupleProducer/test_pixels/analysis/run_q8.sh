#!/bin/bash
#SBATCH --job-name=l1pix_q8
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=4
#SBATCH --mem=7G
#SBATCH --time=03:00:00
#SBATCH --array=0-3
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/q8_%A_%a.out
# Seed and per-jet tagging with the 8-number pixel summary quantised to the 64-bit word (PIXSUM=q8, train_sets.quantize_summary):
# 0 = direct_curves, 1 = seed_plane, 2 = tag_compare; 3 = direct_curves unquantised in the same environment (reference)
PY="pixi run --manifest-path /work/submit/novaka/l1pixels/analysis/pixi.toml python"
A=/work/submit/novaka/l1pixels/analysis
D=/scratch/submit/cms/novaka/l1pixels/derived/analysis_q8
S=/scratch/submit/cms/novaka/l1pixels
WD=$(mktemp -d /tmp/l1pix_q8.XXXX); cp $A/*.py $WD/
cd $A  # relative list paths
export OMP_NUM_THREADS=4 MB_TOTAL=1999360 HT_MIN=150 PYTHONPATH=$WD PIXSUM=q8
HH="$S/local_v3/perfNano_HH4b_*.root"; MB="$S/local_mbsel_ext/perfNano_MinBiasSel_*.root,$S/local_mbnew/perfNano_MinBiasNew_*.root"
HLT=lists_v3pt15_hh4b.npz:lists_v3pt15_qcd.npz:lists_mbsel_pt15.npz:lists_mbnew_pt15.npz
L1=lists_l1ext_HH4b.npz:lists_l1ext_QCDFlat.npz:lists_l1ext_MinBiasSel.npz:lists_l1ext_MinBiasNew.npz
case $SLURM_ARRAY_TASK_ID in
  0) $PY $WD/direct_curves.py $D/curves_q8.json $D/curves_q8_flags.npz "$HH" "$MB" offline_flags2.npz $HLT $L1 ;;
  1) $PY $WD/seed_plane.py $D/seed_plane_q8.npz "$HH" "$MB" $HLT $L1 ;;
  2) OFFLINE="$S/offline/HH4b_*.npz:$S/offline/QCDFlat_*.npz" $PY $WD/tag_compare.py $D/tag_chain_q8.json \
       "OT only:lists_ot_HH4b.npz:lists_ot_QCDFlat.npz" "L1 + pixel:lists_l1ext_HH4b.npz:lists_l1ext_QCDFlat.npz" \
       "HLT pixel:lists_v3pt15_hh4b.npz:lists_v3pt15_qcd.npz" ;;
  3) PIXSUM=v1 $PY $WD/direct_curves.py $D/curves_ref.json $D/curves_ref_flags.npz "$HH" "$MB" offline_flags2.npz $HLT $L1 ;;
esac
rm -rf $WD

#!/bin/bash
#SBATCH --job-name=l1pix_variants
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=4
#SBATCH --mem=7G
#SBATCH --time=03:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/variants_%A_%a.out
# Deliverable variants: 0 = merge lists; 1 = per-jet ROC (pixel without barrel layer 1, OT-only summary);
# 2 = seed curves with the layer-1-less pixel tagger; 3 = seed curves with the OT-only summary (no pixels)
A=/work/submit/novaka/l1pixels/analysis; D=/scratch/submit/cms/novaka/l1pixels/derived; S=/scratch/submit/cms/novaka/l1pixels
WD=$(mktemp -d /tmp/l1pix_var.XXXX); cp $A/*.py $WD/
cd $A; export PYTHONPATH=$WD OMP_NUM_THREADS=4 MB_TOTAL=1999360 HT_MIN=150
PY="pixi run --manifest-path $A/pixi.toml python"
HH="$S/local_v3/perfNano_HH4b_*.root"; MB="$S/local_mbsel_ext/perfNano_MinBiasSel_*.root,$S/local_mbnew/perfNano_MinBiasNew_*.root"
HLT=lists_v3pt15_hh4b.npz:lists_v3pt15_qcd.npz:lists_mbsel_pt15.npz:lists_mbnew_pt15.npz
NOL1=$D/lists_l1ext_noL1_HH4b.npz:$D/lists_l1ext_noL1_QCDFlat.npz:$D/lists_l1ext_noL1_MinBiasSel.npz:$D/lists_l1ext_noL1_MinBiasNew.npz
OT=lists_ot_HH4b.npz:lists_ot_QCDFlat.npz:$D/lists_ot_MinBiasSel.npz:$D/lists_ot_MinBiasNew.npz
case $SLURM_ARRAY_TASK_ID in
  0) for s in HH4b QCDFlat MinBiasSel MinBiasNew; do $PY $WD/merge_lists.py $D/lists_l1ext_noL1_$s.npz $D/l1ext_parts_noL1/${s}_*.npz; done
     for s in MinBiasSel MinBiasNew; do $PY $WD/merge_lists.py $D/lists_ot_$s.npz $D/ot_parts_mb/${s}_*.npz; done ;;
  1) $PY $WD/tag_compare.py $D/tag_chain_variants.json "L1 + pixel:lists_l1ext_HH4b.npz:lists_l1ext_QCDFlat.npz" \
       "L1 + pixel, no barrel layer 1:$D/lists_l1ext_noL1_HH4b.npz:$D/lists_l1ext_noL1_QCDFlat.npz" "OT only:lists_ot_HH4b.npz:lists_ot_QCDFlat.npz" ;;
  2) $PY $WD/direct_curves.py $D/curves_noL1.json $D/curves_noL1_flags.npz "$HH" "$MB" offline_flags2.npz $HLT $NOL1 ;;
  3) $PY $WD/direct_curves.py $D/curves_ot.json $D/curves_ot_flags.npz "$HH" "$MB" offline_flags2.npz $HLT $OT ;;
esac
rm -rf $WD

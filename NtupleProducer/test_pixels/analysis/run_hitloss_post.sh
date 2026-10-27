#!/bin/bash
#SBATCH --job-name=l1pix_hlpost
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=4
#SBATCH --mem=7G
#SBATCH --time=03:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/hlpost_%j.out
# Pixel tagging with 10% of pixel clusters lost at random (l1ext HIT_LOSS=0.1): merge lists, per-jet ROC, seed curves
A=/work/submit/novaka/l1pixels/analysis; D=/scratch/submit/cms/novaka/l1pixels/derived; S=/scratch/submit/cms/novaka/l1pixels
WD=$(mktemp -d /tmp/l1pix_hl.XXXX); cp $A/*.py $WD/
cd $A; export PYTHONPATH=$WD OMP_NUM_THREADS=4 MB_TOTAL=1999360 HT_MIN=150
PY="pixi run --manifest-path $A/pixi.toml python"
for s in HH4b QCDFlat MinBiasSel MinBiasNew; do $PY $WD/merge_lists.py $D/lists_l1ext_hl10_$s.npz $D/l1ext_parts_hitloss10/${s}_*.npz; done
HH="$S/local_v3/perfNano_HH4b_*.root"; MB="$S/local_mbsel_ext/perfNano_MinBiasSel_*.root,$S/local_mbnew/perfNano_MinBiasNew_*.root"
HLT=lists_v3pt15_hh4b.npz:lists_v3pt15_qcd.npz:lists_mbsel_pt15.npz:lists_mbnew_pt15.npz
HL=$D/lists_l1ext_hl10_HH4b.npz:$D/lists_l1ext_hl10_QCDFlat.npz:$D/lists_l1ext_hl10_MinBiasSel.npz:$D/lists_l1ext_hl10_MinBiasNew.npz
$PY $WD/tag_compare.py $D/tag_chain_hl10.json "L1 + pixel:lists_l1ext_HH4b.npz:lists_l1ext_QCDFlat.npz" \
  "L1 + pixel, 10% hit loss:$D/lists_l1ext_hl10_HH4b.npz:$D/lists_l1ext_hl10_QCDFlat.npz"
$PY $WD/direct_curves.py $D/curves_hl10.json $D/curves_hl10_flags.npz "$HH" "$MB" offline_flags2.npz $HLT $HL
rm -rf $WD

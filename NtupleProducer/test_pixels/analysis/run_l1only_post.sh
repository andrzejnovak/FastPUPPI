#!/bin/bash
#SBATCH --job-name=l1pix_l1opost
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=4
#SBATCH --mem=7G
#SBATCH --time=03:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/l1opost_%j.out
# Pixel tagging with barrel layer 1 only (one-hit extension, l1ext KEEP_LIDS=1 MIN_HITS=1): the replaceable layer
A=/work/submit/novaka/l1pixels/analysis; D=/scratch/submit/cms/novaka/l1pixels/derived; S=/scratch/submit/cms/novaka/l1pixels
WD=$(mktemp -d /tmp/l1pix_hl.XXXX); cp $A/*.py $WD/
cd $A; export PYTHONPATH=$WD OMP_NUM_THREADS=4 MB_TOTAL=1999360 HT_MIN=150
PY="pixi run --manifest-path $A/pixi.toml python"
for s in HH4b QCDFlat MinBiasSel MinBiasNew; do $PY $WD/merge_lists.py $D/lists_l1ext_L1only_$s.npz $D/l1ext_parts_L1only/${s}_*.npz; done
HH="$S/local_v3/perfNano_HH4b_*.root"; MB="$S/local_mbsel_ext/perfNano_MinBiasSel_*.root,$S/local_mbnew/perfNano_MinBiasNew_*.root"
HLT=lists_v3pt15_hh4b.npz:lists_v3pt15_qcd.npz:lists_mbsel_pt15.npz:lists_mbnew_pt15.npz
L1O=$D/lists_l1ext_L1only_HH4b.npz:$D/lists_l1ext_L1only_QCDFlat.npz:$D/lists_l1ext_L1only_MinBiasSel.npz:$D/lists_l1ext_L1only_MinBiasNew.npz
$PY $WD/tag_compare.py $D/tag_chain_L1only.json "L1 + pixel:lists_l1ext_HH4b.npz:lists_l1ext_QCDFlat.npz" \
  "L1 + pixel, barrel layer 1 only:$D/lists_l1ext_L1only_HH4b.npz:$D/lists_l1ext_L1only_QCDFlat.npz"
$PY $WD/direct_curves.py $D/curves_L1only.json $D/curves_L1only_flags.npz "$HH" "$MB" offline_flags2.npz $HLT $L1O
rm -rf $WD

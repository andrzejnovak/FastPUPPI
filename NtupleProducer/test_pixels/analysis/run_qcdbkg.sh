#!/bin/bash
#SBATCH --job-name=l1pix_qcdbkg
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --time=06:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/qcdbkg_%A_%a.out
# kappa_lambda with the weighted pT-binned QCD background (kl_qcdbkg.py):
#   sbatch run_qcdbkg.sh merge     # per-bin pixel lists (from run_lists_variant.sh into $D/l1ext_parts_qcdpt)
#   sbatch run_qcdbkg.sh fit       # SEED_KHZ from the environment (default 2.5); OUTTAG names the output
A=/work/submit/novaka/l1pixels/analysis; D=/scratch/submit/cms/novaka/l1pixels/derived; S=/scratch/submit/cms/novaka/l1pixels
WD=$(mktemp -d /tmp/l1pix_qcdbkg.XXXX); cp $A/*.py $WD/
cd $A; export PYTHONPATH=$WD OMP_NUM_THREADS=4 MB_TOTAL=1999360 HT_MIN=150
PY="pixi run --manifest-path $A/pixi.toml python"
case $1 in
  merge)
    for b in $(ls $D/l1ext_parts_qcdpt/QCDPt*_*.npz | xargs -n1 basename | cut -d_ -f1 | sort -u); do
      $PY $WD/merge_lists.py $D/qcdpt_lists/lists_l1ext_$b.npz $D/l1ext_parts_qcdpt/${b}_*.npz
    done ;;
  fit)
    $PY $WD/kl_qcdbkg.py $D/kl_qcdbkg${OUTTAG}.json "$S/local_v3/perfNano_HH4b_*.root" \
      "$S/local_mbsel_ext/perfNano_MinBiasSel_*.root,$S/local_mbnew/perfNano_MinBiasNew_*.root" \
      lists_l1ext_HH4b.npz:lists_l1ext_QCDFlat.npz:lists_l1ext_MinBiasSel.npz:lists_l1ext_MinBiasNew.npz seed_plane.npz \
      "$S/genmhh/mhh_*.npz" "klreweight/nano_mhh_kl*.npz" $S/local_qcdpt $D/qcdpt_lists $S/offline_w ;;
esac
rm -rf $WD

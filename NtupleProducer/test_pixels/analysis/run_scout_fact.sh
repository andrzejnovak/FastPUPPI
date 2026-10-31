#!/bin/bash
#SBATCH --job-name=l1pix_scfact
#SBATCH --partition=submit-gpu-express
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/scfact_%A_%a.out
# Scouting fits with the factorised background (BKG_MODE=factorised): 0 = scout4b.py (L1 jets), 1 = scout_kin.py
A=/work/submit/novaka/l1pixels/analysis; D=/scratch/submit/cms/novaka/l1pixels/derived; S=/scratch/submit/cms/novaka/l1pixels
WD=$(mktemp -d /tmp/l1pix_scfact.XXXX); cp $A/*.py $WD/
cd $A; export PYTHONPATH=$WD MB_TOTAL=1999360 HT_MIN=150 BKG_MODE=factorised
PY="pixi run --manifest-path $A/pixi.toml python"
case $SLURM_ARRAY_TASK_ID in
  0) $PY $WD/scout4b.py $D/scout4b_fact.json "$S/local_v3/perfNano_HH4b_*.root" lists_l1ext_HH4b.npz seed_plane.npz "$S/genmhh/mhh_*.npz" \
       "klreweight/nano_mhh_kl*.npz" $D/scouting/scouting.json $D/norm_check.json $S/local_qcdpt $S/offline_w $S/privgen ;;
  1) $PY $WD/scout_kin.py $D/scout_kin_fact.json seed_plane.npz "$S/genmhh/mhh_*.npz" "klreweight/nano_mhh_kl*.npz" \
       $D/norm_check.json "$S/offline/HH4b_*.npz" "$S/local_v3/perfNano_HH4b_*.root" $S/local_qcdpt $S/offline_w $S/privgen ;;
esac
rm -rf $WD

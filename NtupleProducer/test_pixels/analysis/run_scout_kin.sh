#!/bin/bash
#SBATCH --job-name=l1pix_sckin
#SBATCH --partition=submit-gpu-express
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/sckin_%j.out
# Scouting ceiling with offline-quality and generator-level jets + perfect tags (scout_kin.py)
A=/work/submit/novaka/l1pixels/analysis; D=/scratch/submit/cms/novaka/l1pixels/derived; S=/scratch/submit/cms/novaka/l1pixels
WD=$(mktemp -d /tmp/l1pix_sckin.XXXX); cp $A/*.py $WD/
cd $A; export PYTHONPATH=$WD MB_TOTAL=1999360 HT_MIN=150
pixi run --manifest-path $A/pixi.toml python $WD/scout_kin.py $D/scout_kin.json seed_plane.npz "$S/genmhh/mhh_*.npz" "klreweight/nano_mhh_kl*.npz" \
  $D/norm_check.json "$S/offline/HH4b_*.npz" "$S/local_v3/perfNano_HH4b_*.root" $S/local_qcdpt $S/offline_w $S/privgen
rm -rf $WD

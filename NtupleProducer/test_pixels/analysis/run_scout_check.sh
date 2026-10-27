#!/bin/bash
#SBATCH --job-name=l1pix_scchk
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=2
#SBATCH --mem=14G
#SBATCH --time=04:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/scchk_%j.out
# 40 MHz scouting with the weighted pT-binned QCD background (scout_check.py)
A=/work/submit/novaka/l1pixels/analysis; D=/scratch/submit/cms/novaka/l1pixels/derived; S=/scratch/submit/cms/novaka/l1pixels
WD=$(mktemp -d /tmp/l1pix_scchk.XXXX); cp $A/*.py $WD/
cd $A; export PYTHONPATH=$WD MB_TOTAL=1999360 HT_MIN=150
pixi run --manifest-path $A/pixi.toml python $WD/scout_check.py $D/scout_check.json "$S/local_v3/perfNano_HH4b_*.root" lists_l1ext_HH4b.npz \
  seed_plane.npz "$S/genmhh/mhh_*.npz" "klreweight/nano_mhh_kl*.npz" $D/scouting/scouting.json $S/local_qcdpt $S/offline_w
rm -rf $WD

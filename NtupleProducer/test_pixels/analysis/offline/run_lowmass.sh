#!/bin/bash
#SBATCH --job-name=l1pix_lowmass
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=2
#SBATCH --mem=6G
#SBATCH --time=02:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/offline/logs/lowmass_%j.out
# Offline selection vs generator m_HH: cutflow and low-mass-friendly variants (offline_lowmass.py), pixi env
O=/work/submit/novaka/l1pixels/offline; A=/work/submit/novaka/l1pixels/analysis; S=/scratch/submit/cms/novaka/l1pixels
WD=$(mktemp -d /tmp/l1pix_lowmass.XXXX); cp $O/offline_lowmass.py $O/b_response.json $WD/
cd $A
pixi run --manifest-path $A/pixi.toml python $WD/offline_lowmass.py $S/derived/offline_lowmass.json \
  "$S/offline/HH4b_*.npz" "$S/offline/QCDFlat_*.npz" "$S/genmhh/mhh_*.npz" "klreweight/nano_mhh_kl*.npz"
rm -rf $WD

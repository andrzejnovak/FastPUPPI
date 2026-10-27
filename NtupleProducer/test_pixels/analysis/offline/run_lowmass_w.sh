#!/bin/bash
#SBATCH --job-name=l1pix_lowmassw
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=2
#SBATCH --mem=10G
#SBATCH --time=06:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/offline/logs/lowmassw_%j.out
# Low-mass offline selection with the weighted pT-binned QCD background and real UParT tags (offline_lowmass_w.py)
O=/work/submit/novaka/l1pixels/offline; A=/work/submit/novaka/l1pixels/analysis; S=/scratch/submit/cms/novaka/l1pixels
WD=$(mktemp -d /tmp/l1pix_lowmassw.XXXX); cp $O/offline_lowmass_w.py $O/b_response.json $WD/
cd $A
pixi run --manifest-path $A/pixi.toml python $WD/offline_lowmass_w.py $S/derived/offline_lowmass_w.json \
  "$S/offline/HH4b_*.npz" "$S/offline/QCDFlat_*.npz" "$S/genmhh/mhh_*.npz" "klreweight/nano_mhh_kl*.npz" "$S/offline_w/QCDPt*_*.npz"
rm -rf $WD

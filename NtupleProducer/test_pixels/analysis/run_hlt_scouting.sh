#!/bin/bash
#SBATCH --job-name=l1pix_hltsc
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=2
#SBATCH --mem=10G
#SBATCH --time=04:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/hltsc_%j.out
# HLT scouting for L1-accepted crossings: HH->4b acceptance vs HLT output rate (hlt_scouting.py). OUT, QDIR overridable.
A=/work/submit/novaka/l1pixels/analysis; D=/scratch/submit/cms/novaka/l1pixels/derived; S=/scratch/submit/cms/novaka/l1pixels
WD=$(mktemp -d /tmp/l1pix_hltsc.XXXX); cp $A/*.py $WD/
cd $A; export PYTHONPATH=$WD MB_TOTAL=1999360 HT_MIN=150
pixi run --manifest-path $A/pixi.toml python $WD/hlt_scouting.py ${OUT:-$D/hlt_scouting.json} seed_plane.npz "$S/offline/HH4b_*.npz" \
  "$S/genmhh/mhh_*.npz" "klreweight/nano_mhh_kl*.npz" $D/offline_lowmass_flags.npz ${QDIR:-$S/local_qcdpt} $S/offline_w
rm -rf $WD

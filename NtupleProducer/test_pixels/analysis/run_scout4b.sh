#!/bin/bash
#SBATCH --job-name=l1pix_sc4b
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=2
#SBATCH --mem=14G
#SBATCH --time=04:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/sc4b_%j.out
# 40 MHz scouting with the genuine-4b background from the private QCD4b sample (scout4b.py). "cache" builds the
# pT-binned QCD cache only.
A=/work/submit/novaka/l1pixels/analysis; D=/scratch/submit/cms/novaka/l1pixels/derived; S=/scratch/submit/cms/novaka/l1pixels
WD=$(mktemp -d /tmp/l1pix_sc4b.XXXX); cp $A/*.py $WD/
cd $A; export PYTHONPATH=$WD MB_TOTAL=1999360 HT_MIN=150
PY="pixi run --manifest-path $A/pixi.toml python"
if [ "$1" = cache ]; then
  $PY -c "import sys; sys.argv=['x']; import scout4b, kl_qcdbkg as KQ, numpy as np, glob
qf = np.concatenate([np.load(f)['upart'][(np.load(f)['pt'] > 30) & (np.load(f)['flav'] == 0)] for f in sorted(glob.glob('$S/offline/QCDFlat_*.npz'))])
KQ.UPART_M = float(np.quantile(qf, 0.99)); scout4b.read_qcdpt('$S/local_qcdpt', '$S/offline_w')"
else
  $PY $WD/scout4b.py $D/scout4b.json "$S/local_v3/perfNano_HH4b_*.root" lists_l1ext_HH4b.npz seed_plane.npz "$S/genmhh/mhh_*.npz" \
    "klreweight/nano_mhh_kl*.npz" $D/scouting/scouting.json $D/norm_check.json $S/local_qcdpt $S/offline_w $S/privgen
fi
rm -rf $WD

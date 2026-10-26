#!/bin/bash
#SBATCH --job-name=l1pix_off2
#SBATCH --partition=submit
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
#SBATCH --output=slurm_logs/offline2_%j.out
# Offline selection with the b-jet response correction, then the L1 comparison on selected events (HLT pixel, L1-extended)
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh` && cd /work/submit/novaka/l1pixels/analysis
OFF=/scratch/submit/cms/novaka/l1pixels/offline
GEN="/scratch/submit/cms/novaka/l1pixels/genmhh/mhh_*.npz"; KL="klreweight/nano_mhh_kl*.npz"
python3 ../offline/offline_sel.py offline_flags2.npz offline_sel2.json "$OFF/HH4b_*.npz" "$OFF/QCDFlat_*.npz"
python3 -c "
import numpy as np
o=np.load('offline_flags2.npz'); s=o['4b_nomass']
print('corrected m1 quantiles (4b):', np.percentile(o['mh1'][s],[10,25,50,75,90]).round(0), ' m2:', np.percentile(o['mh2'][s],[10,25,50,75,90]).round(0))
print('mass-window efficiency for 4b events: corrected', o['resolved_4b'][s].mean().round(3), ' uncorrected', o['resolved_4b_noreg'][s].mean().round(3))"
for sel in resolved_4b 3b_mass; do
  for tag in direct_rate2 direct_rate_l1ext; do
    echo "=== offline $sel (b-response corrected), $tag"; SEL=offline_flags2.npz:$sel python3 kl_direct.py ${tag}_flags.npz "$GEN" "$KL" kl_${tag}_off2_$sel.json | grep -v "alone_1\|alone_2\|pixel>2"
  done
done

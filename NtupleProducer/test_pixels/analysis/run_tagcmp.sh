#!/bin/bash
#SBATCH --job-name=l1pix_tagcmp
#SBATCH --partition=submit
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --time=02:00:00
#SBATCH --output=slurm_logs/tagcmp_%j.out
# Per-jet tagging chain for the page: L1 NN baseline, + OT-only displaced tracks, + L1 tracks with pixel hits,
# + HLT pixel tracks, and offline UParT as a reference
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh` && cd /work/submit/novaka/l1pixels/analysis
export OMP_NUM_THREADS=8
for s in HH4b QCDFlat; do [ -f lists_ot_$s.npz ] || python3 merge_lists.py lists_ot_$s.npz ot_parts/${s}_*.npz; done
OFFLINE="/ceph/submit/data/user/n/novaka/l1pixels/offline/HH4b_*.npz:/ceph/submit/data/user/n/novaka/l1pixels/offline/QCDFlat_*.npz" \
python3 tag_compare.py tag_chain.json "OT only:lists_ot_HH4b.npz:lists_ot_QCDFlat.npz" \
  "L1 + pixel:lists_l1ext_HH4b.npz:lists_l1ext_QCDFlat.npz" "HLT pixel:lists_v3pt15_hh4b.npz:lists_v3pt15_qcd.npz"

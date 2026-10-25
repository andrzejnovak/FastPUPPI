#!/bin/bash
#SBATCH --job-name=l1pix_direct
#SBATCH --partition=submit
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=08:00:00
#SBATCH --output=slurm_logs/direct_%j.out
# run_direct.sh : per-jet lists (jets > 15 GeV) for the extended samples, then the direct rate test
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh` && cd /work/submit/novaka/l1pixels/analysis
export OMP_NUM_THREADS=8 JET_PTMIN=15
V3=/ceph/submit/data/user/n/novaka/l1pixels/local_v3
MB=/ceph/submit/data/user/n/novaka/l1pixels/local_mbsel_ext
[ -f lists_v3pt15_hh4b.npz ] || python3 make_lists.py lists_v3pt15_hh4b.npz HH4b $V3/perfNano_HH4b_*.root &
[ -f lists_v3pt15_qcd.npz ] || python3 make_lists.py lists_v3pt15_qcd.npz QCDFlat $V3/perfNano_QCDFlat_*.root &
[ -f lists_mbsel_pt15.npz ] || python3 make_lists.py lists_mbsel_pt15.npz MinBiasSel $MB/perfNano_MinBiasSel_*.root &
wait
python3 direct_rate.py direct_rate.json "$V3/perfNano_HH4b_*.root" "$MB/perfNano_MinBiasSel_*.root" lists_v3pt15_hh4b.npz lists_v3pt15_qcd.npz lists_mbsel_pt15.npz

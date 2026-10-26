#!/bin/bash
#SBATCH --job-name=l1pix_direct2
#SBATCH --partition=submit
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=08:00:00
#SBATCH --output=slurm_logs/direct2_%j.out
# run_direct2.sh : direct rate test with all minimum bias: the first targeted sample (official events, emulated HT > 90)
# plus the new one (the other 1.34M events, stored 14_0 HT > 60; validated complete for b-tagged seeds above HT 150)
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh` && cd /work/submit/novaka/l1pixels/analysis
export OMP_NUM_THREADS=8 JET_PTMIN=15 MB_TOTAL=1999360 HT_MIN=150
V3=/scratch/submit/cms/novaka/l1pixels/local_v3
MB=/scratch/submit/cms/novaka/l1pixels/local_mbsel_ext
NEW=/scratch/submit/cms/novaka/l1pixels/local_mbnew
[ -f lists_mbnew_pt15.npz ] || python3 make_lists.py lists_mbnew_pt15.npz MinBiasNew $NEW/perfNano_MinBiasNew_*.root
python3 direct_rate.py direct_rate2.json "$V3/perfNano_HH4b_*.root" "$MB/perfNano_MinBiasSel_*.root,$NEW/perfNano_MinBiasNew_*.root" \
  lists_v3pt15_hh4b.npz lists_v3pt15_qcd.npz lists_mbsel_pt15.npz,lists_mbnew_pt15.npz
python3 kl_direct.py direct_rate2_flags.npz "/scratch/submit/cms/novaka/l1pixels/genmhh/mhh_*.npz" "klreweight/nano_mhh_kl*.npz" kl_direct2.json

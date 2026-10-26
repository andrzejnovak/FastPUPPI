#!/bin/bash
#SBATCH --job-name=l1ext_direct
#SBATCH --partition=submit
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=08:00:00
#SBATCH --output=slurm_logs/l1ext_direct_%j.out
# Direct rate test with the realistic-L1 pixel tagger (L1 tracks extended into the pixels), and the analysis-level
# selection for both the HLT-pixel and the L1-extended taggers
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh` && cd /work/submit/novaka/l1pixels/analysis
export OMP_NUM_THREADS=8 MB_TOTAL=1999360 HT_MIN=150
P=l1ext_parts
for s in HH4b QCDFlat MinBiasSel MinBiasNew; do
  [ -f lists_l1ext_$s.npz ] || python3 merge_lists.py lists_l1ext_$s.npz $P/${s}_*.npz
done
V3=/scratch/submit/cms/novaka/l1pixels/local_v3
MB=/scratch/submit/cms/novaka/l1pixels/local_mbsel_ext
NEW=/scratch/submit/cms/novaka/l1pixels/local_mbnew
python3 direct_rate.py direct_rate_l1ext.json "$V3/perfNano_HH4b_*.root" "$MB/perfNano_MinBiasSel_*.root,$NEW/perfNano_MinBiasNew_*.root" \
  lists_l1ext_HH4b.npz lists_l1ext_QCDFlat.npz lists_l1ext_MinBiasSel.npz,lists_l1ext_MinBiasNew.npz
GEN="/scratch/submit/cms/novaka/l1pixels/genmhh/mhh_*.npz"; KL="klreweight/nano_mhh_kl*.npz"
OFF=/scratch/submit/cms/novaka/l1pixels/offline
echo "=== generator fiducial, L1-extended"; python3 kl_direct.py direct_rate_l1ext_flags.npz "$GEN" "$KL" kl_direct_l1ext.json
python3 ../offline/offline_sel.py offline_flags.npz offline_sel.json "$OFF/HH4b_*.npz" "$OFF/QCDFlat_*.npz"
for sel in resolved_4b 3b_mass 4b_nomass 4j; do
  for tag in direct_rate2 direct_rate_l1ext; do
    echo "=== offline $sel, $tag"; SEL=offline_flags.npz:$sel python3 kl_direct.py ${tag}_flags.npz "$GEN" "$KL" kl_${tag}_off_$sel.json
  done
done

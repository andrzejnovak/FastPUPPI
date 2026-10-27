#!/bin/bash
#SBATCH --job-name=l1pix_vbfcharm
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=04:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/vbf_ctag_charm_%j.out
# VBF H -> cc (or bb) seed on top of the menu with the charm-oriented pixel summary (vbf_ctag_charm.py).
# Same inputs as run_vbf_ctag.sh; runs a private copy of the scripts; portable venv for the tier3 CPUs.
# sbatch [--export=ALL,WHICH=bb] run_vbf_ctag_charm.sh
set -e
A=/work/submit/novaka/l1pixels/analysis
S=/scratch/submit/cms/novaka/l1pixels
D=$S/derived
P=$D/l1ext_parts
W=$(mktemp -d /tmp/vbf_charm_${SLURM_JOB_ID:-local}_XXXX)
cp $A/vbf_ctag_charm.py $A/vbf_ctag.py $A/vbf_menu.py $A/train_sets.py $A/charm_feats.py $A/charm_feats2.py $W/
source /work/submit/novaka/tools/ana-venv/bin/activate
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-2}
cd $W
MB="$S/local_mbsel_ext/perfNano_MinBiasSel_*.root,$S/local_mbnew/perfNano_MinBiasNew_*.root,$S/local_mbvbf/perfNano_MinBiasVBF_*.root"
MBL="$D/analysis/lists_l1ext_MinBiasSel.npz,$D/analysis/lists_l1ext_MinBiasNew.npz,$P/MinBiasVBF_*.npz"
mkdir -p $D/ctag_charm
case ${WHICH:-cc} in
  cc) python3 $W/vbf_ctag_charm.py $D/ctag_charm/vbf_ctag_charm${OUTTAG}_cc.json "$S/local_v3/perfNano_VBFHCC_*.root" "$P/VBFHCC_*.npz" "$MB" "$MBL" $D/analysis/lists_l1ext_QCDFlat.npz 4 ;;
  bb) python3 $W/vbf_ctag_charm.py $D/ctag_charm/vbf_ctag_charm${OUTTAG}_bb.json "$S/local_v3/perfNano_VBFHBB_*.root" "$P/VBFHBB_*.npz" "$MB" "$MBL" $D/analysis/lists_l1ext_QCDFlat.npz 5 ;;
esac
rm -rf $W
echo DONE

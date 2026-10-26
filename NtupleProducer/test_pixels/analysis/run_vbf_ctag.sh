#!/bin/bash
#SBATCH --job-name=l1pix_vbfctag
#SBATCH --partition=submit
#SBATCH --cpus-per-task=2
#SBATCH --mem=6G
#SBATCH --time=03:00:00
#SBATCH --output=slurm_logs/vbf_ctag_%j.out
# VBF H -> cc (c tag) and H -> bb (b tag): looser VBF seed + two tagged central jets on top of the menu (vbf_ctag.py)
# portable python (pip wheels) so it also runs on the older tier3 CPUs; the CMSSW 17 python needs x86-64-v3
source /work/submit/novaka/tools/ana-venv/bin/activate
cd /work/submit/novaka/l1pixels/analysis
export OMP_NUM_THREADS=2
S=/scratch/submit/cms/novaka/l1pixels
P=$S/derived/l1ext_parts
MB="$S/local_mbsel_ext/perfNano_MinBiasSel_*.root,$S/local_mbnew/perfNano_MinBiasNew_*.root,$S/local_mbvbf/perfNano_MinBiasVBF_*.root"
MBL="lists_l1ext_MinBiasSel.npz,lists_l1ext_MinBiasNew.npz,$P/MinBiasVBF_*.npz"
# WHICH=cc (default) or bb: sbatch --export=ALL,WHICH=bb run_vbf_ctag.sh
case ${WHICH:-cc} in
  cc) python3 vbf_ctag.py vbf_ctag_cc.json "$S/local_v3/perfNano_VBFHCC_*.root" "$P/VBFHCC_*.npz" "$MB" "$MBL" lists_l1ext_QCDFlat.npz 4 ;;
  bb) python3 vbf_ctag.py vbf_ctag_bb.json "$S/local_v3/perfNano_VBFHBB_*.root" "$P/VBFHBB_*.npz" "$MB" "$MBL" lists_l1ext_QCDFlat.npz 5 ;;
esac

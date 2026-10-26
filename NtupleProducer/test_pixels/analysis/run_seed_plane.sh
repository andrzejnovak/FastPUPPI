#!/bin/bash
#SBATCH --job-name=l1pix_plane
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=4
#SBATCH --mem=7G
#SBATCH --time=03:00:00
#SBATCH --output=slurm_logs/seed_plane_%j.out
# Per-event score sums and per-jet scores for the thesis-style plots (seed_plane.py); portable python for tier3
source /work/submit/novaka/tools/ana-venv/bin/activate
cd /work/submit/novaka/l1pixels/analysis
export OMP_NUM_THREADS=4 MB_TOTAL=1999360 HT_MIN=150
S=/scratch/submit/cms/novaka/l1pixels
python3 seed_plane.py seed_plane.npz "$S/local_v3/perfNano_HH4b_*.root" \
  "$S/local_mbsel_ext/perfNano_MinBiasSel_*.root,$S/local_mbnew/perfNano_MinBiasNew_*.root" \
  lists_v3pt15_hh4b.npz:lists_v3pt15_qcd.npz:lists_mbsel_pt15.npz:lists_mbnew_pt15.npz \
  lists_l1ext_HH4b.npz:lists_l1ext_QCDFlat.npz:lists_l1ext_MinBiasSel.npz:lists_l1ext_MinBiasNew.npz

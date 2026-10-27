#!/bin/bash
#SBATCH --job-name=l1pix_htctrl
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=1
#SBATCH --mem=6G
#SBATCH --time=02:00:00
#SBATCH --output=slurm_logs/ht_control_%j.out
# Control for the HH->4b seeds: the same added rate spent on lower menu HT thresholds (ht_control.py)
source /work/submit/novaka/tools/ana-venv/bin/activate
cd /work/submit/novaka/l1pixels/analysis
S=/scratch/submit/cms/novaka/l1pixels
python3 ht_control.py ht_control_flags.npz "$S/local_v3/perfNano_HH4b_*.root" \
  "$S/local_mbsel_ext/perfNano_MinBiasSel_*.root,$S/local_mbnew/perfNano_MinBiasNew_*.root" 1 2.5 5 10 15

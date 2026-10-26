#!/bin/bash
#SBATCH --job-name=l1pix_zhmet
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=1
#SBATCH --mem=6G
#SBATCH --time=01:00:00
#SBATCH --output=slurm_logs/zh_met_%j.out
# ZH(nunu) menu efficiency vs generator MET on all private files (zh_met.py)
source /work/submit/novaka/tools/ana-venv/bin/activate
cd /work/submit/novaka/l1pixels/analysis
P=/scratch/submit/cms/novaka/l1pixels/privgen
python3 zh_met.py zh_met.json "ZHnunu_bb:$P/perfNano_ZHnunu_bb_*.root" "ZHnunu_cc:$P/perfNano_ZHnunu_cc_*.root"

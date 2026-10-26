#!/bin/bash
#SBATCH --job-name=l1pix_offscen
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=02:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/offscen_%j.out
# Offline HH->4b selections from today's proxy to softer ones (offline_scenarios.py)
source /work/submit/novaka/tools/ana-venv/bin/activate
cd /work/submit/novaka/l1pixels/offline
O=/scratch/submit/cms/novaka/l1pixels/offline
python3 offline_scenarios.py /work/submit/novaka/l1pixels/analysis/offline_scenarios.npz offline_scenarios.json "$O/HH4b_*.npz" "$O/QCDFlat_*.npz"

#!/bin/bash
#SBATCH --job-name=ratecheck
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=1
#SBATCH --mem=6G
#SBATCH --time=00:30:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/rate_check_%j.out
source /work/submit/novaka/tools/ana-venv/bin/activate
WD=$(mktemp -d /tmp/ratecheck.XXXX); cp /work/submit/novaka/l1pixels/analysis/rate_check.py $WD/
python3 $WD/rate_check.py /scratch/submit/cms/novaka/l1pixels/derived/ratecheck/rate_check.json
rm -rf $WD

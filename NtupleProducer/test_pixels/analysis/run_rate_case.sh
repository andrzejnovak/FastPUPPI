#!/bin/bash
#SBATCH --job-name=l1pix_ratecase
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=01:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/ratecase_%j.out
# Rate case: tagged HH->4b seeds vs the menu's HT seeds at equal rate / efficiency (rate_case.py), pixi env
A=/work/submit/novaka/l1pixels/analysis
WD=$(mktemp -d /tmp/l1pix_ratecase.XXXX); cp $A/*.py $WD/
cd $A; export PYTHONPATH=$WD
pixi run --manifest-path $A/pixi.toml python $WD/rate_case.py /scratch/submit/cms/novaka/l1pixels/derived/rate_case.json
rm -rf $WD

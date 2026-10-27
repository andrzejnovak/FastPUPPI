#!/bin/bash
#SBATCH --job-name=l1pix_pageplots
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=2
#SBATCH --mem=7G
#SBATCH --time=01:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/pageplots_%j.out
# Page plots (make_page_plots.py -> plots_page/, plot_scouting.py) in the pixi environment (no CMSSW needed)
A=/work/submit/novaka/l1pixels/analysis
WD=$(mktemp -d /tmp/l1pix_pageplots.XXXX); cp $A/*.py $WD/
cd $A
export PYTHONPATH=$WD
pixi run --manifest-path $A/pixi.toml python $WD/make_page_plots.py && pixi run --manifest-path $A/pixi.toml python $WD/plot_scouting.py
rm -rf $WD

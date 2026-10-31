#!/bin/bash
#SBATCH --job-name=render_deck
#SBATCH --partition=submit-gpu-express
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --output=/work/submit/novaka/l1pixels/review/deck_render/render_%j.log
cd /work/submit/novaka/tools/render
pixi run python render_deck.py /work/submit/novaka/l1pixels/review/deck_render/src pixdeck_blobs.json /work/submit/novaka/l1pixels/review/deck_render/png ${SCALE:-0.5}

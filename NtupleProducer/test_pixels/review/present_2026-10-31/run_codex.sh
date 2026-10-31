#!/bin/bash
#SBATCH --job-name=codex_present
#SBATCH --partition=submit-gpu-express
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=01:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/review/present_2026-10-31/codex_run.log
# Codex audit of the presentation page for a CMS + ATLAS audience (read-only), as its own job
D=/work/submit/novaka/l1pixels/review/present_2026-10-31
cd $D
ARGS=(); for f in figs/*.png; do ARGS+=(-i "$f"); done
/home/submit/novaka/.pixi/bin/codex exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort=high -C $D \
  --add-dir /work/submit/novaka/l1pixels --add-dir /scratch/submit/cms/novaka/l1pixels/derived \
  --output-last-message $D/codex_review.md "${ARGS[@]}" - < PROMPT.md

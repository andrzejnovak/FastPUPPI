#!/bin/bash
#SBATCH --job-name=deck_review
#SBATCH --partition=submit-gpu-express
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=01:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/review/deck_2026-10-31/review_%A_%a.log
# Read-only reviews of the slide deck: task 0 = Codex, task 1 = agy (Gemini). Same prompt (PROMPT.md).
D=/work/submit/novaka/l1pixels/review/deck_2026-10-31; cd $D
case $SLURM_ARRAY_TASK_ID in
  0) ARGS=(); for f in figs/*.png; do ARGS+=(-i "$f"); done
     /home/submit/novaka/.pixi/bin/codex exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort=high -C $D \
       --output-last-message $D/codex_review.md "${ARGS[@]}" - < PROMPT.md ;;
  1) timeout 3000 /home/submit/novaka/.local/bin/agy --model gemini-4-argon-high --mode plan --add-dir $D \
       -p "$(cat PROMPT.md)" > $D/agy_review.md 2> $D/agy_stderr.log ;;
esac

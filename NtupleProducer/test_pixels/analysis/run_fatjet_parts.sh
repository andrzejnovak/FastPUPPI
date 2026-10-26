#!/bin/bash
#SBATCH --job-name=l1pix_fatjet
#SBATCH --partition=submit
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=02:00:00
#SBATCH --output=slurm_logs/fatjet_%A_%a.out
# Large-jet tables (fatjet_parts.py) for one line "SAMPLE FLAV file1 [file2 ...]" of $LIST, into $OUTDIR
read SAMPLE FL FILES <<< "$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" $LIST)"
OUT=$OUTDIR/${SAMPLE}_$(basename ${FILES%% *} .root).npz
[ -f $OUT ] && exit 0
source /work/submit/novaka/tools/ana-venv/bin/activate  # portable python: also runs on tier3
cd /work/submit/novaka/l1pixels/analysis
FLAV=$FL python3 fatjet_parts.py $OUT.tmp.npz $SAMPLE $FILES && mv $OUT.tmp.npz $OUT && echo DONE

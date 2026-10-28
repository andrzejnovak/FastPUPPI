#!/bin/bash
#SBATCH --job-name=privgen4b
#SBATCH --partition=submit
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=12:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/privgen/logs/slurm_%A_%a.out
# One line of $JOBS per array task: sample idx nevents
LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" ${JOBS:-/work/submit/novaka/l1pixels/privgen/jobs_test.txt})
echo "$(hostname) $LINE"
/work/submit/novaka/l1pixels/privgen/run_privgen_4b.sh $LINE

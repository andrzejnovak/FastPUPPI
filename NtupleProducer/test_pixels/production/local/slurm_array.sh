#!/bin/bash
#SBATCH --job-name=l1pix
#SBATCH --partition=submit
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=04:00:00
#SBATCH --output=slurm_logs/%A_%a.out
# One line of jobs_todo.txt per array task: sample idx lfn maxEvents
LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" jobs_todo.txt)
echo "$(hostname) $LINE"
./run_local.sh $LINE

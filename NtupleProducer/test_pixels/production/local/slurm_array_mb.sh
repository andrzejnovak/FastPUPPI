#!/bin/bash
#SBATCH --job-name=l1pixmb
#SBATCH --partition=submit
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=08:00:00
#SBATCH --output=slurm_logs/%A_%a.out
# One line of jobs_mb.txt per array task: sample idx lfn maxEvents
LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" jobs_mb.txt)
echo "$(hostname) $LINE"
./run_mb.sh $LINE

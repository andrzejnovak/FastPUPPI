#!/bin/bash
#SBATCH --job-name=l1pixv3
#SBATCH --partition=submit
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=08:00:00
#SBATCH --output=slurm_logs/%A_%a.out
# One line of jobs_v3.txt per array task: sample idx lfn maxEvents
LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" jobs_v3.txt)
echo "$(hostname) $LINE"
./run_v3.sh $LINE

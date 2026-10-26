#!/bin/bash
#SBATCH --job-name=l1seed
#SBATCH --partition=submit
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=01:00:00
#SBATCH --output=slurm_logs/l1seed_%j.out
# run_l1_seed.sh <outdir> [rate_kHz] : L1 HH->4b seed, NN vs perfect b-tag, on official151X ntuples
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/ngv2/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh` && cd /work/submit/novaka/l1pixels/analysis
D=/scratch/submit/cms/novaka/l1pixels/official151X
python3 l1_seed.py $1 "$D/perfNano_HH4b_*.root" "$D/perfNano_MinBias_*.root" ${2:-14}

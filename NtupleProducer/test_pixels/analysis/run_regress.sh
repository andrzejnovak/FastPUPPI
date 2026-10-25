#!/bin/bash
#SBATCH --job-name=l1pix_regress
#SBATCH --partition=submit
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=12:00:00
#SBATCH --output=slurm_logs/regress_%j.out
# run_regress.sh <tag> : can a network recover track information from pixel hits? (uses lists_<tag>_*.npz)
TAG=$1
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh` && cd /work/submit/novaka/l1pixels/analysis
export OMP_NUM_THREADS=8 TF_NUM_INTRAOP_THREADS=8
python3 regress_hits.py regress_${TAG} lists_${TAG}_hh4b.npz lists_${TAG}_qcd.npz

#!/bin/bash
#SBATCH --job-name=l1pix_budget
#SBATCH --partition=submit
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=03:00:00
#SBATCH --output=slurm_logs/budget_%j.out
# run_budget.sh <tag> : lists from local_v2 ntuples + training/bandwidth study into budget_<tag>/
TAG=$1
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh` && cd /work/submit/novaka/l1pixels/analysis
D=/scratch/submit/cms/novaka/l1pixels/local_v2
export OMP_NUM_THREADS=8 TF_NUM_INTRAOP_THREADS=8
[ -f lists_${TAG}_hh4b.npz ] || python3 make_lists.py lists_${TAG}_hh4b.npz HH4b $D/perfNano_HH4b_*.root &
[ -f lists_${TAG}_qcd.npz ] || python3 make_lists.py lists_${TAG}_qcd.npz QCDFlat $D/perfNano_QCDFlat_*.root &
wait
python3 train_sets.py budget_${TAG} lists_${TAG}_hh4b.npz lists_${TAG}_qcd.npz

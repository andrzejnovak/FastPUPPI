#!/bin/bash
#SBATCH --job-name=l1pix_mbmis
#SBATCH --partition=submit
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --time=06:00:00
#SBATCH --output=slurm_logs/mbmis_%j.out
# run_mb_mistag.sh : lists from the minimum-bias pixel ntuples, then pixel-tagger fake rates on minimum-bias jets
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh` && cd /work/submit/novaka/l1pixels/analysis
export OMP_NUM_THREADS=8 TF_NUM_INTRAOP_THREADS=8
python3 make_lists.py lists_mb_minbias.npz MinBias /scratch/submit/cms/novaka/l1pixels/local_mb/perfNano_MinBias_*.root
python3 mb_mistag.py mb_mistag.json lists_full_hh4b.npz lists_full_qcd.npz lists_mb_minbias.npz

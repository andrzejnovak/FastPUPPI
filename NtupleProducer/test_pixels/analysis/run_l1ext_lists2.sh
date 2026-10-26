#!/bin/bash
#SBATCH --job-name=l1ext_lists
#SBATCH --partition=submit
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=04:00:00
#SBATCH --output=slurm_logs/l1ext_lists_%A_%a.out
# As run_l1ext_lists.sh, for any list of "SAMPLE FILE [FILE ...]" lines: sbatch --export=ALL,LIST=...,OUTDIR=... --array=...
read SAMPLE F <<< "$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" $LIST)"
OUT=$OUTDIR/${SAMPLE}_$(basename ${F%% *} .root).npz
[ -f $OUT ] && exit 0
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh` && cd /work/submit/novaka/l1pixels/analysis
export JET_PTMIN=15
python3 make_l1ext_lists.py $OUT.tmp.npz $SAMPLE $F && mv $OUT.tmp.npz $OUT && echo DONE

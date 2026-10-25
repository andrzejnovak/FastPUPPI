#!/bin/bash
#SBATCH --job-name=ot_lists
#SBATCH --partition=submit
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=04:00:00
#SBATCH --output=slurm_logs/ot_lists_%A_%a.out
# Per-jet lists with L1 tracks extended into the pixels (make_l1ext_lists.py), one ntuple file per task
read SAMPLE F <<< "$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" /work/submit/novaka/l1pixels/analysis/ot_parts/files.txt)"
OUT=/work/submit/novaka/l1pixels/analysis/ot_parts/${SAMPLE}_$(basename $F .root).npz
[ -f $OUT ] && exit 0
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh` && cd /work/submit/novaka/l1pixels/analysis
export JET_PTMIN=15 MODE=otonly
python3 make_l1ext_lists.py $OUT.tmp.npz $SAMPLE $F && mv $OUT.tmp.npz $OUT && echo DONE

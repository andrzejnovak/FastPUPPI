#!/bin/bash
#SBATCH --job-name=l1pixoff
#SBATCH --partition=submit
#SBATCH --cpus-per-task=1
#SBATCH --mem=3G
#SBATCH --time=02:00:00
#SBATCH --output=logs/%A_%a.out
# Offline jets for the v3 HH4b and QCD files (one line of ../local/jobs_v3.txt per task)
read SAMPLE IDX LFN NEV <<< "$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" /work/submit/novaka/l1pixels/local/jobs_v3.txt)"
OUT=/scratch/submit/cms/novaka/l1pixels/offline/${SAMPLE}_${IDX}.npz
[ -f $OUT ] && exit 0
export X509_USER_PROXY=$HOME/x509up_u248613
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh`
WD=$(mktemp -d /tmp/l1pixoff_${SLURM_ARRAY_TASK_ID}.XXXX); cd $WD
python3 /work/submit/novaka/l1pixels/offline/dump_offline.py out.npz $LFN 2>&1 | grep -v -i warning && cp out.npz $OUT && echo DONE
cd /; rm -rf $WD

#!/bin/bash
#SBATCH --job-name=l1pixjscan
#SBATCH --partition=submit
#SBATCH --cpus-per-task=1
#SBATCH --mem=3G
#SBATCH --time=04:00:00
#SBATCH --output=scan_logs/j_%A_%a.out
# Stored-L1-jet scan of all MinBias files, 100 files per task (125 tasks)
IDX=$SLURM_ARRAY_TASK_ID
OUT=/scratch/submit/cms/novaka/l1pixels/mbjscan/scan_${IDX}.npz
[ -f $OUT ] && exit 0
export X509_USER_PROXY=$HOME/x509up_u248613
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh` && cd /work/submit/novaka/l1pixels/mbsel
LFNS=$(sed -n "$((IDX*100+1)),$((IDX*100+100))p" file_lumi.txt | cut -d' ' -f1)
WD=$(mktemp -d /tmp/l1pixjscan_${IDX}.XXXX); cd $WD
python3 /work/submit/novaka/l1pixels/mbsel/scan_jets.py scan.npz $LFNS 2>&1 | grep -v -i warning && cp scan.npz $OUT && echo DONE $IDX
cd /; rm -rf $WD

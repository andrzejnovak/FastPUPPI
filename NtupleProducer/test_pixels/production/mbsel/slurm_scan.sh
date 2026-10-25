#!/bin/bash
#SBATCH --job-name=l1pixscan
#SBATCH --partition=submit
#SBATCH --cpus-per-task=1
#SBATCH --mem=3G
#SBATCH --time=04:00:00
#SBATCH --output=scan_logs/%A_%a.out
# Stored-L1-HT scan of all MinBias files, 100 files per task (125 tasks)
IDX=$SLURM_ARRAY_TASK_ID
OUT=/ceph/submit/data/user/n/novaka/l1pixels/mbscan/scan_${IDX}.npz
[ -f $OUT ] && exit 0
export X509_USER_PROXY=$HOME/x509up_u248613
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh` && cd /work/submit/novaka/l1pixels/mbsel
LFNS=$(sed -n "$((IDX*100+1)),$((IDX*100+100))p" file_lumi.txt | cut -d' ' -f1)
WD=$(mktemp -d /tmp/l1pixscan_${IDX}.XXXX); cd $WD
python3 /work/submit/novaka/l1pixels/mbsel/scan_ht.py scan.npz $LFNS 2>&1 | grep -v -i warning && cp scan.npz $OUT && echo DONE $IDX
cd /; rm -rf $WD

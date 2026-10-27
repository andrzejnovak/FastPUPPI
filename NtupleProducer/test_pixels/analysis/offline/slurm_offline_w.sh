#!/bin/bash
#SBATCH --job-name=l1pixoffw
#SBATCH --partition=submit
#SBATCH --cpus-per-task=1
#SBATCH --mem=3G
#SBATCH --time=02:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/offline/logs_w/%A_%a.out
# Offline jets + generator weight / pT-hat / cross-section (dump_offline.py) for the QCD background validation:
# one line of offline_w/jobs.txt (sample idx lfn) per task. Runs a private copy of the dump script.
O=/scratch/submit/cms/novaka/l1pixels/offline_w
read SAMPLE IDX LFN <<< "$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" $O/jobs.txt)"
OUT=$O/${SAMPLE}_${IDX}.npz
[ -f $OUT ] && exit 0
export X509_USER_PROXY=$HOME/x509up_u248613
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh`
WD=$(mktemp -d /tmp/l1pixoffw_${SLURM_ARRAY_TASK_ID}.XXXX); cp /work/submit/novaka/l1pixels/offline/dump_offline.py $WD/; cd $WD
python3 dump_offline.py out.npz $LFN 2>&1 | grep -v -i warning && cp out.npz $OUT.tmp && mv $OUT.tmp $OUT && echo DONE
cd /; rm -rf $WD

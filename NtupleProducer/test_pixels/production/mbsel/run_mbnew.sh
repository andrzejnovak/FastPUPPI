#!/bin/bash
#SBATCH --job-name=l1pixmbnew
#SBATCH --partition=submit
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=08:00:00
#SBATCH --output=slurm_logs/%A_%a.out
# Targeted minimum-bias production: new events (not in the official ntuples) with stored 14_0 L1 HT > 60 GeV (select_new.py).
# One line of jobs_new60.txt per task: "lfn|run:lumi:event,...;lfn|...". Input step + ntuple step, output to /ceph.
IDX=$SLURM_ARRAY_TASK_ID
OUT=/ceph/submit/data/user/n/novaka/l1pixels/local_mbnew
[ -f $OUT/perfNano_MinBiasNew_${IDX}.root ] && exit 0
LINE=$(sed -n "$((IDX+1))p" /work/submit/novaka/l1pixels/mbsel/jobs_new60.txt)
FILES=$(echo "$LINE" | tr ';' '\n' | cut -d'|' -f1 | sed 's#^#root://cms-xrd-global.cern.ch/#' | paste -sd,)
EVENTS=$(echo "$LINE" | tr ';' '\n' | cut -d'|' -f2 | paste -sd,)
echo "$(hostname) job $IDX: $(echo $FILES | tr ',' '\n' | wc -l) files, $(echo $EVENTS | tr ',' '\n' | wc -l) events"
export X509_USER_PROXY=$HOME/x509up_u248613
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/ngv2/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh`
T=$CMSSW_BASE/src/FastPUPPI/NtupleProducer/test_pixels
WD=$(mktemp -d /tmp/l1pixsel_${IDX}.XXXX); cd $WD
cmsRun $T/step1_cfg.py inputFiles=$FILES events=$EVENTS clusters=True out=inputs.root > step1.log 2>&1 || { tail -30 step1.log; echo "FAIL step1 $IDX"; exit 1; }
cmsRun $T/step2_cfg.py inputFiles=file:inputs.root out=perfNano.root extended=True > step2.log 2>&1 || { tail -30 step2.log; echo "FAIL step2 $IDX"; exit 2; }
grep -c "Begin processing" step1.log | sed 's/^/events processed: /'
cp perfNano.root $OUT/perfNano_MinBiasNew_${IDX}.root && echo "DONE $IDX"
cd /; rm -rf $WD

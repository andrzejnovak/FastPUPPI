#!/bin/bash
#SBATCH --job-name=l1pixmbv2
#SBATCH --partition=submit
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=08:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/osg/logs/slurm_mb_%A_%a.out
# Minimum-bias re-run with R = 0.8 jets on Slurm, for jobs that failed on OSG (one line of $LIST per task:
# "jobsfile idx outname outdir", as mb_osg_jobs.txt). Output to /ceph, skipped if it already exists.
read JOBS IDX OUTNAME OUTDIR <<< "$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" $LIST)"
OUT=/scratch/submit/cms/novaka/l1pixels/$OUTDIR/$OUTNAME
[ -f $OUT ] && exit 0
LINE=$(sed -n "$((IDX+1))p" /work/submit/novaka/l1pixels/osg/$JOBS)
FILES=$(echo "$LINE" | tr ';' '\n' | cut -d'|' -f1 | sed 's#^#root://cms-xrd-global.cern.ch/#' | paste -sd,)
EVENTS=$(echo "$LINE" | tr ';' '\n' | cut -d'|' -f2 | paste -sd,)
export X509_USER_PROXY=$HOME/x509up_u248613
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/ngv2/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh`
T=$CMSSW_BASE/src/FastPUPPI/NtupleProducer/test_pixels
WD=$(mktemp -d /tmp/l1pixmbv2_${IDX}.XXXX); cd $WD
cmsRun $T/step1_cfg.py inputFiles=$FILES events=$EVENTS clusters=True out=inputs.root > step1.log 2>&1 || { tail -30 step1.log; echo "FAIL step1 $OUTNAME"; exit 1; }
cmsRun $T/step2_cfg.py inputFiles=file:inputs.root out=perfNano.root extended=True > step2.log 2>&1 || { tail -30 step2.log; echo "FAIL step2 $OUTNAME"; exit 2; }
cp perfNano.root $OUT && echo "DONE $OUTNAME"
cd /; rm -rf $WD

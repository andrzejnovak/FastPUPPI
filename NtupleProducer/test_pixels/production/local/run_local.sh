#!/bin/bash
# run_local.sh <sample> <idx> <lfn> <maxEvents>   (input step + ntuple step, outputs to /ceph)
SAMPLE=$1; IDX=$2; LFN=$3; NEV=$4
OUT=/scratch/submit/cms/novaka/l1pixels/local_v2
[ -f $OUT/perfNano_${SAMPLE}_${IDX}.root ] && exit 0
export X509_USER_PROXY=$HOME/x509up_u248613
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/ngv2/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh`
T=$CMSSW_BASE/src/FastPUPPI/NtupleProducer/test_pixels
WD=$(mktemp -d /tmp/l1pix_${SAMPLE}_${IDX}.XXXX); cd $WD
nice cmsRun $T/step1_cfg.py inputFiles=root://cms-xrd-global.cern.ch/$LFN out=inputs.root maxEvents=$NEV > step1.log 2>&1 || { cp step1.log /work/submit/novaka/l1pixels/local/logs/${SAMPLE}_${IDX}_step1.log; echo "FAIL step1 $SAMPLE $IDX"; exit 1; }
nice cmsRun $T/step2_cfg.py inputFiles=file:inputs.root out=perfNano.root > step2.log 2>&1 || { cp step2.log /work/submit/novaka/l1pixels/local/logs/${SAMPLE}_${IDX}_step2.log; echo "FAIL step2 $SAMPLE $IDX"; exit 2; }
cp inputs.root $OUT/inputs_${SAMPLE}_${IDX}.root; cp perfNano.root $OUT/perfNano_${SAMPLE}_${IDX}.root && echo "DONE $SAMPLE $IDX"
cd /; rm -rf $WD

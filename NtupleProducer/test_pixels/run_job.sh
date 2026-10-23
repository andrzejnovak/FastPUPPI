#!/bin/bash
# One production job: input step (with pixel tables) + ntuple step on one RAW file.
#   run_job.sh <sample> <idx> <lfn> <redirector> <maxEvents>
set -e
SAMPLE=$1; IDX=$2; LFN=$3; REDIR=$4; NEV=$5
AREA=/work/submit/novaka/l1pixels/CMSSW_17_0_0_pre2
OUT=/ceph/submit/data/user/n/novaka/l1pixels/v1/$SAMPLE
T=$AREA/src/FastPUPPI/NtupleProducer/test_pixels
mkdir -p $OUT
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd $AREA/src && eval `scram runtime -sh` && cd -
WD=$(mktemp -d ${_CONDOR_SCRATCH_DIR:-/tmp}/l1pix.XXXXXX); cd $WD
cmsRun $T/step1_cfg.py inputFiles=${REDIR}/${LFN} out=inputs.root maxEvents=$NEV > step1.log 2>&1 || { tail -50 step1.log; exit 1; }
cmsRun $T/step2_cfg.py inputFiles=file:inputs.root out=perfNano.root > step2.log 2>&1 || { tail -50 step2.log; exit 2; }
cp perfNano.root $OUT/perfNano_${IDX}.root
cp inputs.root $OUT/inputs_${IDX}.root
grep -E "TrigReport Events total" step1.log step2.log || true
cd /; rm -rf $WD

#!/bin/bash
# OSPool job: unpack the CMSSW area, run the input step (with pixel tables) and the ntuple step.
#   run_job_osg.sh <sample> <idx> <lfn> <redirector> <maxEvents>
SAMPLE=$1; IDX=$2; LFN=$3; REDIR=$4; NEV=$5
SB=$PWD
echo "host $(hostname) site ${GLIDEIN_Site:-?} cpus $(nproc)"
export SCRAM_ARCH=el9_amd64_gcc13
source /cvmfs/cms.cern.ch/cmsset_default.sh || exit 10
tar -xzf cmssw.tgz || exit 11
cd CMSSW_17_0_0_pre2/src && scram b ProjectRename >/dev/null 2>&1; eval `scram runtime -sh` || exit 12
cd $SB
T=$CMSSW_BASE/src/FastPUPPI/NtupleProducer/test_pixels
OUT=perfNano_${SAMPLE}_${IDX}.root
for k in 1 2 3; do
  cmsRun $T/step1_cfg.py inputFiles=${REDIR}/${LFN} out=inputs.root maxEvents=$NEV > step1.log 2>&1 && break
  echo "step1 attempt $k failed"; tail -30 step1.log; sleep 60
done
[ -f inputs.root ] || exit 1
cmsRun $T/step2_cfg.py inputFiles=file:inputs.root out=$OUT > step2.log 2>&1 || { tail -50 step2.log; exit 2; }
grep -h "event loop CPU/event" step1.log step2.log
rm -rf inputs.root CMSSW_17_0_0_pre2 cmssw.tgz

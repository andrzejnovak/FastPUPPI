#!/bin/bash
# run_privgen_4b.sh <sample> <idx> <ngenerated>: as run_privgen.sh for a generator-filtered sample (QCD4b): also writes the
# number of generated events, the cross-section before the filter and per-event weight / pT-hat (genw_<sample>_<idx>.txt).
# Writes /ceph/.../l1pixels/privgen/perfNano_<sample>_<idx>.root and a timing line to logs/.
S=$1; IDX=$2; NEV=$3
P=/work/submit/novaka/l1pixels/privgen
OUT=/scratch/submit/cms/novaka/l1pixels/privgen
mkdir -p $OUT
[ -f $OUT/perfNano_${S}_${IDX}.root ] && exit 0
export X509_USER_PROXY=$HOME/x509up_u248613
source /cvmfs/cms.cern.ch/cmsset_default.sh
WD=$(mktemp -d /tmp/privgen_${S}_${IDX}.XXXX); cd $WD
seed="from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper
RandomNumberServiceHelper(process.RandomNumberGeneratorService).populate()"
cp $P/cfg/gs_${S}_cfg.py gs.py; printf '%s\nprocess.options.wantSummary = True\nprocess.maxEvents.input = %d\nprocess.source.firstLuminosityBlock = cms.untracked.uint32(%d)\n' "$seed" $NEV $((IDX+1)) >> gs.py
cp $P/cfg/${DIGI_CFG:-digi_local_cfg.py} digi.py; printf '%s\n' "$seed" >> digi.py
fail() { cp *.log $P/logs/ 2>/dev/null; echo "FAIL $1 $S $IDX"; cd /; rm -rf $WD; exit 1; }
t0=$(date +%s)
(export SCRAM_ARCH=el9_amd64_gcc12; cd $P/CMSSW_14_0_9/src && eval `scram runtime -sh` && cd $WD && cmsRun gs.py > gs_${S}_${IDX}.log 2>&1) || fail gs
t1=$(date +%s)
NGEN=$(grep -m1 "TrigReport Events total" gs_${S}_${IDX}.log | awk "{print \$5}")
XS=$(grep -m1 "Before Filter: total cross section" gs_${S}_${IDX}.log | awk "{print \$7, \$9}")
(export SCRAM_ARCH=el9_amd64_gcc12; cd $P/CMSSW_14_0_9/src && eval `scram runtime -sh` && cd $WD && python3 $P/dump_genweight.py gs.root genw.txt) || fail genweight
[ -s genw.txt ] || { echo "no events passed the filter"; echo "$S $IDX ngen=$NGEN xs=$XS npass=0" >> $P/logs/genfilter_${S}.txt; cd /; rm -rf $WD; exit 0; }
# pileup is mixed from remote MinBias GEN-SIM files: an unreadable file kills the job, so retry (new random pileup each time)
ok=0
for k in 1 2 3; do
  (export SCRAM_ARCH=el9_amd64_gcc12; cd $P/CMSSW_14_0_9/src && eval `scram runtime -sh` && cd $WD && cmsRun digi.py > digi_${S}_${IDX}.log 2>&1) && { ok=1; break; }
  echo "digi attempt $k failed: $(grep -m1 -A1 'Exception Message' digi_${S}_${IDX}.log | tail -1 | cut -c1-150)"; rm -f digi.root
done
[ $ok = 1 ] || fail digi
t2=$(date +%s)
T=/work/submit/novaka/l1pixels/ngv2/CMSSW_17_0_0_pre2/src
(cd $T && eval `scram runtime -sh` && cd $WD && cmsRun $T/FastPUPPI/NtupleProducer/test_pixels/step1_cfg.py inputFiles=file:digi.root out=inputs.root clusters=True > step1_${S}_${IDX}.log 2>&1 \
  && cmsRun $T/FastPUPPI/NtupleProducer/test_pixels/step2_cfg.py inputFiles=file:inputs.root out=perfNano.root extended=True > step2_${S}_${IDX}.log 2>&1) || fail ntuple
t3=$(date +%s)
cp perfNano.root $OUT/perfNano_${S}_${IDX}.root; cp genw.txt $OUT/genw_${S}_${IDX}.txt
echo "$S $IDX ngen=$NGEN xs=$XS npass=$(wc -l < genw.txt)" >> $P/logs/genfilter_${S}.txt
echo "$S $IDX nev=$NEV gs=$((t1-t0))s digi=$((t2-t1))s ntuple=$((t3-t2))s" | tee -a $P/logs/timing.txt
cd /; rm -rf $WD

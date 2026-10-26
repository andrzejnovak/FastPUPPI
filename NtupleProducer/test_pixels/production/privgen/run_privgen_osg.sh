#!/bin/bash
# OSPool job: GEN-SIM -> DIGI/L1/HLT (PU 200, official Spring24 recipe, CMSSW_14_0_9) -> our step1/step2 (CMSSW_17_0_0_pre2).
#   run_privgen_osg.sh <sample> <idx> <nevents> [threads] [streams]
S=$1; IDX=$2; NEV=$3; NT=${4:-1}; NS=${5:-$NT}  # optional: threads, streams for GEN-SIM and DIGI
SB=$PWD
echo "host $(hostname) site ${GLIDEIN_Site:-?} cpus $(nproc)"
source /cvmfs/cms.cern.ch/cmsset_default.sh || exit 10
[ -f /cvmfs/cms.cern.ch/SITECONF/local/JobConfig/site-local-config.xml ] || export SITECONFIG_PATH=/cvmfs/cms.cern.ch/SITECONF/T3_US_OSG
# grid credentials inside the container (CA certificates, VOMS) from cvmfs, or xrootd cannot use the proxy
for d in /etc/grid-security/certificates /cvmfs/grid.cern.ch/etc/grid-security/certificates /cvmfs/oasis.opensciencegrid.org/mis/certificates; do
  [ -d $d ] && { export X509_CERT_DIR=$d; break; }
done
[ -d /cvmfs/grid.cern.ch/etc/grid-security/vomsdir ] && export X509_VOMS_DIR=/cvmfs/grid.cern.ch/etc/grid-security/vomsdir
[ -n "$X509_USER_PROXY" ] || export X509_USER_PROXY=$(ls $SB/x509up* 2>/dev/null | head -1)
echo "X509_CERT_DIR=$X509_CERT_DIR X509_USER_PROXY=$X509_USER_PROXY"
tar -xzf cmssw1409.tgz && tar -xzf cmssw.tgz || exit 11
seed="from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper
RandomNumberServiceHelper(process.RandomNumberGeneratorService).populate()"
cp cfg/gs_${S}_cfg.py gs.py; printf '%s\nprocess.maxEvents.input = %d\nprocess.source.firstLuminosityBlock = cms.untracked.uint32(%d)\n' "$seed" $NEV $((IDX+1)) >> gs.py
cp cfg/digi_cfg.py digi.py; printf '%s\n' "$seed" >> digi.py
mt="process.options.numberOfThreads = $NT
process.options.numberOfStreams = $NS"
printf '%s\n' "$mt" >> gs.py; printf '%s\n' "$mt" >> digi.py
t0=$(date +%s)
(export SCRAM_ARCH=el9_amd64_gcc12; cd CMSSW_14_0_9/src && scram b ProjectRename >/dev/null 2>&1; eval `scram runtime -sh` && cd $SB && cmsRun gs.py > gs.log 2>&1) || { tail -40 gs.log; exit 1; }
t1=$(date +%s)
# remote pileup: an unreadable file kills the job, so retry with new random pileup
ok=0
for k in 1 2 3; do
  (export SCRAM_ARCH=el9_amd64_gcc12; cd CMSSW_14_0_9/src && eval `scram runtime -sh` && cd $SB && cmsRun digi.py > digi.log 2>&1) && { ok=1; break; }
  echo "digi attempt $k failed: $(grep -m1 -A1 'Exception Message' digi.log | tail -1 | cut -c1-150)"; rm -f digi.root
done
[ $ok = 1 ] || { tail -40 digi.log; exit 2; }
t2=$(date +%s)
rm -f gs.root
(export SCRAM_ARCH=el9_amd64_gcc13; cd CMSSW_17_0_0_pre2/src && scram b ProjectRename >/dev/null 2>&1; eval `scram runtime -sh` && cd $SB \
  && T=$CMSSW_BASE/src/FastPUPPI/NtupleProducer/test_pixels \
  && cmsRun $T/step1_cfg.py inputFiles=file:digi.root out=inputs.root clusters=True > step1.log 2>&1 \
  && cmsRun $T/step2_cfg.py inputFiles=file:inputs.root out=perfNano_${S}_${IDX}.root extended=True > step2.log 2>&1) || { tail -30 step1.log step2.log; exit 3; }
t3=$(date +%s)
echo "TIMING $S $IDX nev=$NEV threads=$NT streams=$NS gs=$((t1-t0))s digi=$((t2-t1))s ntuple=$((t3-t2))s"
rm -rf digi.root inputs.root CMSSW_14_0_9 CMSSW_17_0_0_pre2 cmssw1409.tgz cmssw.tgz cfg

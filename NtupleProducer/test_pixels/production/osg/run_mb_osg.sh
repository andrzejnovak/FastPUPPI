#!/bin/bash
# OSPool job: targeted minimum-bias events (one line of a jobs file: "lfn|run:lumi:event,...;lfn|..."), input step
# with all clusters + extended ntuple step (incl. R = 0.8 jets).
#   run_mb_osg.sh <jobsfile> <idx> <outname>
JOBS=$1; IDX=$2; OUTNAME=$3
SB=$PWD
echo "host $(hostname) site ${GLIDEIN_Site:-?} cpus $(nproc)"
export SCRAM_ARCH=el9_amd64_gcc13
source /cvmfs/cms.cern.ch/cmsset_default.sh || exit 10
# non-CMS OSG sites have no local CMS site config: use the generic opportunistic one
[ -f /cvmfs/cms.cern.ch/SITECONF/local/JobConfig/site-local-config.xml ] || export SITECONFIG_PATH=/cvmfs/cms.cern.ch/SITECONF/T3_US_OSG
# grid credentials inside the container: CA certificates and VOMS info from cvmfs (otherwise xrootd cannot use the
# proxy (GSI), falls back to tokens and the CMS servers refuse: "Auth failed")
for d in /etc/grid-security/certificates /cvmfs/grid.cern.ch/etc/grid-security/certificates /cvmfs/oasis.opensciencegrid.org/mis/certificates; do
  [ -d $d ] && { export X509_CERT_DIR=$d; break; }
done
[ -d /cvmfs/grid.cern.ch/etc/grid-security/vomsdir ] && export X509_VOMS_DIR=/cvmfs/grid.cern.ch/etc/grid-security/vomsdir
[ -n "$X509_USER_PROXY" ] || export X509_USER_PROXY=$(ls $SB/x509up* 2>/dev/null | head -1)
echo "X509_CERT_DIR=$X509_CERT_DIR X509_USER_PROXY=$X509_USER_PROXY"; voms-proxy-info -timeleft 2>&1 | tail -1
LINE=$(sed -n "$((IDX+1))p" $JOBS)
LFNS=$(echo "$LINE" | tr ';' '\n' | cut -d'|' -f1)
EVENTS=$(echo "$LINE" | tr ';' '\n' | cut -d'|' -f2 | paste -sd,)
tar -xzf cmssw.tgz || exit 11
cd CMSSW_17_0_0_pre2/src && scram b ProjectRename >/dev/null 2>&1; eval `scram runtime -sh` || exit 12
cd $SB
T=$CMSSW_BASE/src/FastPUPPI/NtupleProducer/test_pixels
# the global redirector hands out IPv6 addresses some OSG nodes cannot reach: fall back to other redirectors
for R in root://cms-xrd-global.cern.ch/ root://cmsxrootd.fnal.gov/ root://xrootd-cms.infn.it/; do
  FILES=$(echo "$LFNS" | sed "s#^#${R}#" | paste -sd,)
  cmsRun $T/step1_cfg.py inputFiles=$FILES events=$EVENTS clusters=True out=inputs.root > step1.log 2>&1 && break
  echo "step1 via $R failed"; grep -A2 "Exception Message" step1.log | head -3; rm -f inputs.root; sleep 30
done
[ -f inputs.root ] || exit 1
cmsRun $T/step2_cfg.py inputFiles=file:inputs.root out=$OUTNAME extended=True > step2.log 2>&1 || { tail -50 step2.log; exit 2; }
grep -c "Begin processing" step1.log | sed 's/^/events processed: /'
rm -rf inputs.root CMSSW_17_0_0_pre2 cmssw.tgz

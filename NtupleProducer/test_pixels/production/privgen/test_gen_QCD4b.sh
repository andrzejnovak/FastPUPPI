#!/bin/bash
#SBATCH --job-name=gen4b_test
#SBATCH --partition=submit
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=04:00:00
#SBATCH --output=/scratch/submit/cms/novaka/l1pixels/privgen_4btest/gen_%j.out
# GEN-only test of the 4b-enriched QCD fragment: filter efficiency, time per generated event, cross-section
P=/work/submit/novaka/l1pixels/privgen; O=/scratch/submit/cms/novaka/l1pixels/privgen_4btest
export SCRAM_ARCH=el9_amd64_gcc12; source /cvmfs/cms.cern.ch/cmsset_default.sh
cd $P/CMSSW_14_0_9/src && eval `scram runtime -sh`
WD=$(mktemp -d /tmp/gen4b.XXXX); cd $WD; cp $P/cfg/gen_QCD4b_cfg.py gen.py
printf 'process.maxEvents.input = 20000\nprocess.options.wantSummary = True\nfrom IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper\nRandomNumberServiceHelper(process.RandomNumberGeneratorService).populate()\n' >> gen.py
t0=$(date +%s); cmsRun gen.py > gen.log 2>&1; echo "exit $? time $(( $(date +%s) - t0 ))s"
grep -E "TrigReport Events total|TrigReport.*fourBFilter|cross section|sigma" gen.log | head -20
cp gen.root $O/gen_test.root; cp gen.log $O/
cd /; rm -rf $WD

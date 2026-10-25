#!/bin/bash
#SBATCH --job-name=itbits --partition=submit --time=02:00:00 --mem=6G --cpus-per-task=1
#SBATCH --output=/work/submit/novaka/l1pixels/itlinks/slurm_%a.log --array=0-1
FILES=(/store/mc/Phase2Spring24DIGIRECOMiniAOD/GluGluToHHTo4B_node_SM_TuneCP5_14TeV-amcatnlo-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/PU200_AllTP_140X_mcRun4_realistic_v4-v1/130000/8d9861a3-3afd-4c7c-91d8-0e47b14fba8a.root
       /store/mc/Phase2Spring24DIGIRECOMiniAOD/GluGluToHHTo4B_node_SM_TuneCP5_14TeV-amcatnlo-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/PU200_AllTP_140X_mcRun4_realistic_v4-v1/130000/92338855-82c8-40e0-84d5-4101030dc922.root)
export X509_USER_PROXY=$HOME/x509up_u248613
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/ngv2/CMSSW_17_0_0_pre2/src && eval `scram runtime -sh`
D=/work/submit/novaka/l1pixels/itlinks; WD=$(mktemp -d /tmp/itbits_$SLURM_ARRAY_TASK_ID.XXXX); cd $WD
cmsRun $D/bitstream_cfg.py inputFiles=root://cms-xrd-global.cern.ch/${FILES[$SLURM_ARRAY_TASK_ID]} maxEvents=10 outputFile=bits.root > cmsrun.log 2>&1 || { tail -40 cmsrun.log; exit 1; }
python3 $D/dump_bits.py $(ls bits*.root | head -1) $D/bits_$SLURM_ARRAY_TASK_ID.npz
cd /; rm -rf $WD

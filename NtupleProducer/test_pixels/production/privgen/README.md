# Private Phase-2 samples (official Spring24 recipe)

Samples that do not exist centrally: ggH + jet (top-mass dependent, p&#770;T > 150 GeV) with H → bb / cc, and ZH with
Z → νν, H → bb / cc. Pythia8 CP5 at 14 TeV (`fragments/`), then the Phase2Spring24 steps from McM
(`TSG-Phase2Spring24wmLHEGS-00026`, `TSG-Phase2Spring24DIGIRECOMiniAOD-00076`), then our `step1_cfg.py` /
`step2_cfg.py`. LO Pythia only: fine for trigger efficiencies, not for cross-section shapes.

## Setup (once)
```
export SCRAM_ARCH=el9_amd64_gcc12; source /cvmfs/cms.cern.ch/cmsset_default.sh
scram p CMSSW CMSSW_14_0_9 && cd CMSSW_14_0_9/src
mkdir -p Configuration/GenProduction/python && cp <repo>/production/privgen/fragments/*.py Configuration/GenProduction/python/
scram b -j4 && cmsenv && mkdir -p ../../cfg && cd ../../cfg
for s in ggHbb_pt150 ggHcc_pt150 ZHnunu_bb ZHnunu_cc; do
  cmsDriver.py Configuration/GenProduction/python/${s}_fragment.py --eventcontent FEVTDEBUG --datatier GEN-SIM \
    --conditions 140X_mcRun4_realistic_v4 --beamspot HLLHC14TeV --step GEN,SIM --geometry Extended2026D110 \
    --era Phase2C17I13M9 --nThreads 1 --python_filename gs_${s}_cfg.py --fileout file:gs.root --number 10 --no_exec --mc
done
cmsDriver.py step2 --eventcontent FEVTDEBUGHLT --pileup AVE_200_BX_25ns \
  --pileup_input "dbs:/MinBias_TuneCP5_14TeV-pythia8/Phase2Spring24GS-140X_mcRun4_realistic_v4-v1/GEN-SIM" \
  --customise SLHCUpgradeSimulations/Configuration/aging.customise_aging_1000 \
  --customise_commands "process.FEVTDEBUGHLToutput.outputCommands.append('keep *_l1tSC8PFL1PuppiCorrectedEmulator_*_HLT')" \
  --datatier GEN-SIM-DIGI-RAW --conditions 140X_mcRun4_realistic_v4 \
  --step DIGI:pdigi_valid,L1TrackTrigger,L1,DIGI2RAW,HLT:@relval2026 --geometry Extended2026D110 \
  --era Phase2C17I13M9 --nThreads 1 --python_filename digi_cfg.py --filein file:gs.root --fileout file:digi.root \
  --number -1 --no_exec --mc
sed -i "s|'/store/mc/|'root://cms-xrd-global.cern.ch//store/mc/|g" digi_cfg.py   # remote pileup via xrootd
```
`digi_local_cfg.py`: the same with `process.mix.input.fileNames` set to the 20 files of `pileup_lfns.txt` copied to
CMS scratch (`slurm_pucopy.sh`); used on Slurm. OSG jobs use the remote list.

## Running
- Slurm: `JOBS=jobs_pass1.txt sbatch --array=0-199%60 slurm_privgen.sh` (`run_privgen.sh`, local pileup pool).
- OSG: `condor_submit privgen_osg.sub` (`run_privgen_osg.sh`; pack `CMSSW_14_0_9` + `cfg/` as `cmssw1409.tgz` and the
  CMSSW_17_0_0_pre2 area as `cmssw.tgz`). Excludes FANDM-ITS (cvmfs) and SU-ITS (memory/disk limits); 16 GB, 25 GB disk.
- Cost: ~46 s/event GEN-SIM, ~90 s/event DIGI/L1/HLT with PU 200, ~5 s/event ntuples (single thread, as McM).
  Multi-threading barely helps the DIGI step (pileup mixing), so single-core jobs give the most throughput.
- Output: `/scratch/submit/cms/novaka/l1pixels/privgen/perfNano_<sample>_<idx>.root`.

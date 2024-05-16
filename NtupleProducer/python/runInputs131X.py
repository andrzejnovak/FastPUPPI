import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras

process = cms.Process("IN", eras.Phase2C17I13M9)
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.Geometry.GeometryExtended2026D95Reco_cff')
process.load('Configuration.Geometry.GeometryExtended2026D95_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '131X_mcRun4_realistic_v5', '')

process.load('SimCalorimetry.HcalTrigPrimProducers.hcaltpdigi_cff')
process.load('CalibCalorimetry.CaloTPG.CaloTPGTranscoder_cfi')
process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('L1Trigger.TrackTrigger.TrackTrigger_cff')
process.load("L1Trigger.TrackFindingTracklet.L1HybridEmulationTracks_cff") 
process.load("L1Trigger.TrackTrigger.ProducerSetup_cff") 
process.load("L1Trigger.TrackerDTC.ProducerED_cff") 
process.load("RecoVertex.BeamSpotProducer.BeamSpot_cfi")
process.load('L1Trigger.L1THGCal.hgcalTriggerPrimitives_cff')

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        # /VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/Phase2Spring23DIGIRECOMiniAOD-PU200_Trk1GeV_131X_mcRun4_realistic_v5-v1/GEN-SIM-DIGI-RAW-MINIAOD
        # /VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/Phase2Spring23DIGIRECOMiniAOD-noPU_131X_mcRun4_realistic_v5-v1/GEN-SIM-DIGI-RAW-MINIAOD
        
        # 'file:/data/cerminar/Phase2Spring23DIGIRECOMiniAOD/DoubleElectron_FlatPt-1To100-gun/GEN-SIM-DIGI-RAW-MINIAOD/PU200_Trk1GeV_131X_mcRun4_realistic_v5-v1/c699a773-9875-40c9-83b7-5a3c27f90bfd.root',
        # '/store/mc/Phase2Spring23DIGIRECOMiniAOD/DYToLL_M-10To50_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/PU200_Trk1GeV_131X_mcRun4_realistic_v5-v1/30000/0289a719-64c3-4b16-871f-da7db9a8ac88.root',      
        # '/store/mc/Phase2Spring23DIGIRECOMiniAOD/MinBias_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/PU200_Trk1GeV_131X_mcRun4_realistic_v5-v1/30002/3b44d52d-1807-4a4f-9b9b-19466303a741.root',
        # "root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/3981b923-4bdd-4e9a-8069-8775095c6bce.root"
        "root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/544c613d-b019-48b2-943b-f651f254cda3.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/6b4f063a-383f-40cd-84d7-8b67defbfa7f.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/4cca461d-d362-4f71-9cbb-27390b7e6e2a.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/0a978566-187d-4c55-b40d-71ac753d7ef7.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/31b4f21d-9039-4b6b-9406-5c38e3c58b75.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/52b4ce62-1a1c-4bcd-a791-5df26d891e43.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/006f6626-cf25-4030-9835-cd507d7fcbec.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/851ca4ca-f2f1-4cf5-b98e-1cf44aaf0f8c.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/c22ac0c6-45df-4cce-b4fe-fbd51a6ac4b9.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/c8e88656-036e-4e86-b7a2-55214d9efb07.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/bb72c23b-88b8-4864-b959-f82d69c9b0b3.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/86429c60-a028-46ec-8806-d08479c7cef3.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/128af533-7d7a-49c7-a058-c6329bb519e0.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/63897b25-9763-4655-8d16-af3fbeee065c.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/54254adb-100e-42c1-98da-18eaf2096833.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/08c295ed-4e66-4fc8-83dd-f0e3c3adeeb2.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/9a48dd17-85e7-4fbd-a60b-8f2b7e3822e6.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/ab9d174b-e5e8-488b-9327-61280832eb48.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/5b520972-0d3c-4de0-b23f-4581feaa95f6.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/a7e1e839-c0bf-43e5-b69f-13956101ccd2.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/cd509ee1-7007-4dac-94b1-642d7ca21bc9.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/502d6a96-5fa6-4e8f-b62d-eb26937ef256.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/835bfac3-04a2-453d-b171-3f6dacb658f2.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/6f7b7d56-78e5-48c0-ad9e-45b50fe6a12a.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/65ab57e9-728b-4af8-8c51-7ceaf35ba708.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/c3388ebd-28b1-4401-a63f-bfdb8d3abfb5.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/4c1cde07-58a5-40f0-b326-5ec08aba3bee.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/39b7413b-0498-47c6-8727-e9eb204ba304.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/704b0f79-d163-40b6-b7a1-e40387704288.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/3ed1426d-048c-4ce4-a2e5-ab6e9a6890b0.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/7f049c56-347b-40d9-948c-654658da6f7d.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/3981b923-4bdd-4e9a-8069-8775095c6bce.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/8045570a-f7c5-406c-aa26-6ed5a8b325ec.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/f0a73aad-1125-462f-bd81-1432a7d6ca9a.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/a9864bbe-06a4-41b1-b0f0-3f51acabf904.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/1a205f1a-b669-48f6-a5b5-cbc26ac5ced2.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/18e4040e-4e3a-4c73-8706-de7dddc8dc66.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/f02970fe-b767-4cdc-90d5-581c99684346.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/da0ad0af-2b4b-443c-9287-db772454dfc3.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/ac57751b-556d-4ef0-99e0-4ff4f02b5ba9.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/cb9dcd3c-4009-44b4-a500-66049688e91b.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/0698d0b9-3317-4eac-bd0e-67b34ce854ff.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/e7ee1d4d-6398-4320-a247-b7b1036a8c3c.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/719c2883-39c2-4bce-9eb6-d5a37935bef8.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/b7112cdc-f6be-4c2a-a49c-f342a03b3f04.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/50e6cefd-ba96-4acd-9124-846ee602c534.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/310000/0cc0c52f-c4e1-4ede-bca0-3528268bbe4e.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/310000/d40bcc1c-e78f-4d2b-a944-391e9aa890f7.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/40000/95dcc526-dfc5-4e8d-879b-0d57e68bcb63.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/40000/76c641e5-56c1-4d8b-85a4-f94d627d81c0.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/310000/19a4105f-b54b-4964-92db-d28ed6968dfb.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/310000/b6bc4132-60cf-41a6-bc80-2e8dab3542cc.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/30000/0022c9de-8357-4c3f-b1e0-b4cce910a1f2.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/30000/0b502bad-ec5b-4d4f-af58-146b9b320c51.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/30000/7a41d4f6-c430-4c0e-b6af-d481144d388e.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/30000/7d7fec59-0c6b-4050-a9c8-bbdfc4577ab5.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/30000/1151fe52-ff4a-48fe-bfc2-8d761f44ef16.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/30000/a91135b1-e27c-4bc2-b29b-b4b2a5395ec9.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/30000/81fde792-17f7-43b5-b545-3d7e46714a37.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/30000/43434113-6217-4997-b04a-36104947d0d2.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/f3c01b6b-d6cc-4290-8202-fce1e906de2e.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/65136eb4-2f80-4960-9f1e-8d2a515fdb8c.root",
"root://xrootd-cms.infn.it//store/mc/Phase2Spring23DIGIRECOMiniAOD/VBFHToTauTau_M-125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/noPU_131X_mcRun4_realistic_v5-v1/2530000/2297b73b-7cab-4269-83a8-4d94b9e9900c.root",
),

    inputCommands = cms.untracked.vstring(
        'keep *',
        'drop l1tPFJets_*_*_*',
        'drop l1tPFTaus_*_*_*',
        'drop l1tTrackerMuons_*_*_*',
        'drop *_hlt*_*_HLT',
        'drop triggerTriggerFilterObjectWithRefs_*_*_HLT'
    ),
)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100000))
process.options = cms.untracked.PSet( 
        wantSummary = cms.untracked.bool(True),
        numberOfThreads = cms.untracked.uint32(4),
        #numberOfStreams = cms.untracked.uint32(4),
)

process.PFInputsTask = cms.Task(
    process.L1TLayer1TaskInputsTask,
    process.L1THGCalTriggerPrimitivesTask,
   #process.TTClustersFromPhase2TrackerDigis,
   #process.TTStubsFromPhase2TrackerDigis,
   #process.TrackerDTCProducer,
   #process.offlineBeamSpot,
   #process.l1tTTTracksFromTrackletEmulation,
   #process.l1tTTTracksFromExtendedTrackletEmulation,
   #process.TTTrackAssociatorFromPixelDigis,
   #process.TTTrackAssociatorFromPixelDigisExtended,
   #process.SimL1EmulatorTask
   #process.l1tTkStubsGmt,
   process.l1tTkMuonsGmt,
   process.l1tSAMuonsGmt
)
process.p = cms.Path(
        process.l1tLayer1 +
        process.l1tLayer2Deregionizer +
        process.l1tLayer2EG
)
process.p.associate(process.PFInputsTask)

process.out = cms.OutputModule("PoolOutputModule",
        fileName = cms.untracked.string("inputs131X.root"),
        outputCommands = cms.untracked.vstring("drop *",
            # --- GEN
            "keep *_genParticles_*_*",
            "keep *_ak4GenJetsNoNu_*_*",
            "keep *_genMetTrue_*_*",
            # --- Track TPs
            "keep *_l1tTTTracksFromTrackletEmulation_*_*",
            "keep *_l1tTTTracksFromExtendedTrackletEmulation_*_*",
            "keep *_TTTrackAssociatorFromPixelDigis_*_*",
            "keep *_TTTrackAssociatorFromPixelDigisExtended_*_*",
            # --- Calo TPs
            "keep *_simHcalTriggerPrimitiveDigis_*_*",
            "keep *_simCaloStage2Layer1Digis_*_*",
            "keep *_simCaloStage2Digis_*_*",
            # --- Muon TPs
            "keep *_simMuonRPCDigis_*_*",
            "keep *_simMuonGEMPadDigis_*_*",
            "keep *_simMuonGEMPadDigiClusters_*_*",
            "keep *_simDtTriggerPrimitiveDigis_*_*",
            "keep *_simCscTriggerPrimitiveDigis_*_*",
            "keep *_simTwinMuxDigis_*_*",
            "keep *_simBmtfDigis_*_*",
            "keep *_simKBmtfStubs_*_*",
            "keep *_simKBmtfDigis_*_*",
            "keep *_simEmtfDigis_*_*",
            "keep *_simOmtfDigis_*_*",
            "keep *_simGmtCaloSumDigis_*_*",
            "keep *_simGmtStage2Digis_*_*",
            "keep *_simEmtfShowers_*_*",
            "keep *_simGmtShowerDigis_*_*",
            "keep *_simCscTriggerPrimitiveDigisRun3_*_*",
            "keep *_simMuonME0PadDigis_*_*",
            "keep *_me0TriggerDigis_*_*",
            "keep *_simMuonME0PseudoReDigisCoarse_*_*",
            "keep *_me0RecHitsCoarse_*_*",
            "keep *_me0TriggerPseudoDigis_*_*",
            "keep *_me0RecHits_*_*",
            "keep *_me0Segments_*_*",
            "keep *_me0TriggerConvertedPseudoDigis_*_*",
            "keep *_simCscTriggerPrimitiveDigisPhase2_*_*",
            "keep *_simGtExtFakeStage2Digis_*_*",
            "keep *_simGtStage2Digis_*_*",
            "keep *_CalibratedDigis_*_*",
            "keep *_dtTriggerPhase2PrimitiveDigis_*_*",
            # --- HGCal TPs
            "keep l1tHGCalTriggerCellBXVector_l1tHGCalVFEProducer_*_*",
            #"keep l1tHGCalTriggerCellBXVector_l1tHGCalConcentratorProducer_*_*",
            "keep l1tHGCalMulticlusterBXVector_l1tHGCalBackEndLayer2Producer_*_*",
            "keep l1tHGCalTowerBXVector_l1tHGCalTowerProducer_*_*",
            # --- GCT reconstruction
            "keep *_l1tEGammaClusterEmuProducer_*_*",
            "keep *_l1tTowerCalibration_*_*",
            "keep *_l1tCaloJet_*_*",
            "keep *_l1tCaloJetHTT_*_*",
            # --- GTT reconstruction
            "keep *_l1tVertexFinder_*_*",
            "keep *_l1tVertexFinderEmulator_*_*",
            "keep *_l1tTrackJets_*_*",
            "keep *_l1tTrackJetsExtended_*_*",
            "keep *_l1tTrackFastJets_*_*",
            "keep *_l1tTrackerEtMiss_*_*",
            "keep *_l1tTrackerHTMiss_*_*",
            "keep *_l1tTrackJetsEmulation_*_*",
            "keep *_l1tTrackJetsExtendedEmulation_*_*",
            "keep *_l1tTrackerEmuEtMiss_*_*",
            "keep *_l1tTrackerEmuHTMiss_*_*",
            "keep *_l1tTrackerEmuHTMissExtended_*_*",
            # --- GMT reconstruction
            "keep *_l1tTkStubsGmt_*_*",
            "keep *_l1tTkMuonsGmt_*_*",
            "keep *_l1tSAMuonsGmt_*_*",
        ),
        compressionAlgorithm = cms.untracked.string('LZMA'),
        compressionLevel = cms.untracked.int32(4),
        dropMetaData = cms.untracked.string('ALL'),
        fastCloning = cms.untracked.bool(False),
        overrideInputFileSplitLevels = cms.untracked.bool(True),
        eventAutoFlushCompressedSize = cms.untracked.int32(15728640),
        SelectEvents = cms.untracked.PSet(SelectEvents = cms.vstring("p")),
)
process.e = cms.EndPath(process.out)

process.schedule = cms.Schedule([process.p,process.e])

process.out.outputCommands += [ "drop *_l1tHGCalVFEProducer_*_*", ]

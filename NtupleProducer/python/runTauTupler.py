import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras

process = cms.Process("RESP", eras.Phase2C9)

process.load('Configuration.StandardSequences.Services_cff')
process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1))
process.MessageLogger.cerr.FwkReport.reportEvery = 1

process.source = cms.Source("PoolSource",
                           fileNames = cms.untracked.vstring(
                               #'/store/cmst3/group/l1tr/cerminar/14_0_X/fpinputs_131X/v2/SingleNeutrino_PU200/inputs131X_1-23.root'
                               '/store/cmst3/group/l1tr/cerminar/14_0_X/fpinputs_131X/v2/DYToLL_M-50_PU200/inputs131X_1.root',
                               '/store/cmst3/group/l1tr/cerminar/14_0_X/fpinputs_131X/v2/DYToLL_M-50_PU200/inputs131X_3.root',
                               '/store/cmst3/group/l1tr/cerminar/14_0_X/fpinputs_131X/v2/DYToLL_M-50_PU200/inputs131X_5.root',
                               '/store/cmst3/group/l1tr/cerminar/14_0_X/fpinputs_131X/v2/DYToLL_M-50_PU200/inputs131X_7.root',
                               '/store/cmst3/group/l1tr/cerminar/14_0_X/fpinputs_131X/v2/DYToLL_M-50_PU200/inputs131X_9.root',
                           ),
                            inputCommands = cms.untracked.vstring("keep *", 
                                                                  "drop l1tPFClusters_*_*_*",
                                                                  "drop l1tPFTracks_*_*_*",
                                                                  "drop l1tTkPrimaryVertexs_*_*_*",
                                                                  "drop l1tPFCandidates_*_*_*")
                        )

process.load('Configuration.Geometry.GeometryExtended2026D95Reco_cff')
process.load('Configuration.Geometry.GeometryExtended2026D95_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('SimCalorimetry.HcalTrigPrimProducers.hcaltpdigi_cff') # needed to read HCal TPs
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('SimCalorimetry.EcalEBTrigPrimProducers.ecalEBTriggerPrimitiveDigis_cff')
process.load('L1Trigger.L1CaloTrigger.l1tEGammaCrystalsEmulatorProducer_cfi')
process.load('L1Trigger.TrackTrigger.TrackTrigger_cff')
process.load("L1Trigger.TrackFindingTracklet.L1HybridEmulationTracks_cff")
process.load("L1Trigger.TrackerDTC.ProducerED_cff") 

from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '123X_mcRun4_realistic_v3', '')

process.load('SimCalorimetry.HcalTrigPrimProducers.hcaltpdigi_cff') # needed to read HCal TPs
process.load('SimCalorimetry.HGCalSimProducers.hgcalDigitizer_cfi') # needed for HGCAL_noise_fC
process.load('L1Trigger.L1THGCal.l1tHGCalVFEProducer_cfi')
process.load('L1Trigger.L1THGCal.hgcalVFE_cff')
process.load('L1Trigger.L1THGCal.hgcalTriggerPrimitives_cff')
process.load('L1Trigger.TrackFindingTracklet.L1HybridEmulationTracks_cff')
process.load('L1Trigger.Phase2L1ParticleFlow.l1tPFTracksFromL1Tracks_cfi')
process.load('L1Trigger.Phase2L1ParticleFlow.l1ctLayer1_cff')
#process.load('L1Trigger.Phase2L1ParticleFlow.l1tDeregionizerProducer_cfi')
process.load('L1Trigger.Phase2L1ParticleFlow.L1NNTauProducer_cff')
process.load('L1Trigger.Phase2L1ParticleFlow.l1tPFClustersFromCombinedCalo_cfi')
#process.l1tPFClustersFromL1EGClusters.src = cms.InputTag('L1EGammaClusterEmuProducer')
#process.l1tPFClustersFromCombinedCalo.phase2barrelCaloTowers = cms.VInputTag(cms.InputTag("LEGammaClusterEmuProducer","L1CaloTowerCollection",""))
#process.l1tPFClustersFromCombinedCaloHCal.phase2barrelCaloTowers = cms.VInputTag(cms.InputTag("L1EGammaClusterEmuProducer","L1CaloTowerCollection",""))
#process.l1tPFTracksFromL1Tracks.L1TrackTag = ("l1tGTTInputProducer","Level1TTTracksConverted")#l1tTTTracksFromExtendedTrackletEmulation", "Level1TTTracks
process.l1tNNTauProducerPuppi.seedpt = 10
process.l1tNNTauProducerPF.seedpt = 10
process.l1tNNTauProducerPuppi.tausize = 0.2
process.l1tNNTauProducerPF.tausize = 0.2
process.l1tLayer1Barrel.nVtx  = 1
process.l1tLayer1HGCal.nVtx = 1
process.l1tLayer1HGCalNoTK.nVtx = 1
process.l1tLayer1HF.nVtx = 1
process.l1tLayer1Barrel.puAlgoParameters.nVtx = 1
process.l1tLayer1HGCal.puAlgoParameters.nVtx = 1
process.l1tLayer1HGCalNoTK.puAlgoParameters.nVtx = 1
process.l1tLayer1HF.puAlgoParameters.nVtx = 1

ntuple = cms.EDAnalyzer("TauNTuplizer",
                        src=cms.InputTag("l1tNNTauProducerPF","L1PFTausNN"),
                        genParticles = cms.InputTag("genParticles"),
                        drMax = cms.double(0.2),
                        minRecoPtOverGenPt = cms.double(0.2),
                        onlyMatched = cms.bool(False),
                        variables = cms.PSet(
                            pt = cms.string("pt"),
                            eta = cms.string("eta"),
                            phi = cms.string("phi"),
                            chargedIso = cms.string("chargedIso"),
                            fullIso    = cms.string("fullIso"),
                            decayId    = cms.string("id"),
                            passLoose  = cms.string("passLooseNN"),
                            passTight  = cms.string("passTightNN"),
                            m   = cms.string("mass"),
                            z0  = cms.string("z0"),
                            dxy = cms.string("dxy"),
                        ),
                    )

ntuple_double = cms.EDAnalyzer("TauNTuplizerDouble",
                        src=cms.InputTag("l1tNNTauProducerPF","L1PFTausNN"),
                        genParticles = cms.InputTag("genParticles"),
                        drMax = cms.double(0.2),
                        minRecoPtOverGenPt = cms.double(0.2),
                        onlyMatched = cms.bool(False),
                        variables = cms.PSet(
                            pt = cms.string("pt"),
                            eta = cms.string("eta"),
                            phi = cms.string("phi"),
                            chargedIso = cms.string("chargedIso"),
                            fullIso    = cms.string("fullIso"),
                            decayId    = cms.string("id"),
                            passLoose  = cms.string("passLooseNN"),
                            passTight  = cms.string("passTightNN"),
                            m   = cms.string("mass"),
                            z0  = cms.string("z0"),
                            dxy = cms.string("dxy"),
                        ),
                    )

process.ntuplePFSingle    = ntuple.clone()
process.ntuplePupSingle   = ntuple.clone(src=cms.InputTag("l1tNNTauProducerPuppi","L1PFTausNN"))
process.ntuplePupDiTau    = ntuple_double.clone(src=cms.InputTag   ("l1tNNTauProducerPuppi","L1PFTausNN"))
  
modules = cms.Task(
    process.L1TLayer1TaskInputsTask,
    process.L1TLayer1Task,
    process.l1tLayer2Deregionizer,
    process.l1tNNTauProducerPuppi,
    process.l1tNNTauProducerPF,
)

process.p = cms.Path()

process.p.associate(modules)
process.p2 = cms.Path(process.ntuplePFSingle+process.ntuplePupSingle+process.ntuplePupDiTau)
process.schedule = cms.Schedule(process.p, process.p2)
process.TFileService = cms.Service("TFileService", fileName = cms.string("idTupleNew.root"))


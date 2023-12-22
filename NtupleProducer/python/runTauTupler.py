import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras

#process = cms.Process("ID", eras.Phase2C4_trigger)
process = cms.Process("ID", eras.Phase2C9)

process.load('Configuration.StandardSequences.Services_cff')
process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1))
process.MessageLogger.cerr.FwkReport.reportEvery = 1

process.source = cms.Source("PoolSource",
                           fileNames = cms.untracked.vstring(
#'file:/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/tmp/CMSSW_10_5_0_pre1/src/L1Trigger/Phase2L1Taus/test/tmp2/tau104X.root',
#'file:/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/tmp/CMSSW_10_5_0_pre1/src/L1Trigger/Phase2L1Taus/test/tmp2/tau104X_v2.root'
"file:inputs131X.root"
                                                              ),

#                           fileNames = cms.untracked.vstring('file:/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/tmp/CMSSW_10_5_0_pre1/src/L1Trigger/Phase2L1Taus/test/tau104X.root'),
                            duplicateCheckMode = cms.untracked.string("noDuplicateCheck"),

                            inputCommands = cms.untracked.vstring("keep *",
                                                                  "drop l1tPFClusters_*_*_*",
                                                                  "drop l1tPFTracks_*_*_*",
                                                                  "drop l1tTkPrimaryVertexs_*_*_*",
                                                                  "drop l1tPFCandidates_*_*_*")

)
#process.load('Configuration.Geometry.GeometryExtended2026D49Reco_cff')
#process.load('Configuration.Geometry.GeometryExtended2026D49_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('SimCalorimetry.HcalTrigPrimProducers.hcaltpdigi_cff') # needed to read HCal TPs
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('SimCalorimetry.EcalEBTrigPrimProducers.ecalEBTriggerPrimitiveDigis_cff')
process.load('L1Trigger.L1CaloTrigger.l1tEGammaCrystalsEmulatorProducer_cfi')
process.load('L1Trigger.TrackTrigger.TrackTrigger_cff')
process.load("L1Trigger.TrackFindingTracklet.L1HybridEmulationTracks_cff")
#process.load('L1Trigger.TrackerDTC.ProducerES_cff')
process.load('L1Trigger.TrackerDTC.ProducerED_cff')


process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '131X_mcRun4_realistic_v5', '') 

process.load('L1Trigger.L1THGCal.l1tHGCalTriggerGeometryESProducer_cfi')
process.load('SimCalorimetry.HGCalSimProducers.hgcalDigitizer_cfi')
process.load('L1Trigger.L1THGCal.l1tHGCalVFEProducer_cfi')
process.load('L1Trigger.L1THGCal.hgcalVFE_cff')
process.load('L1Trigger.L1THGCal.hgcalTriggerPrimitives_cff')
process.load('L1Trigger.Phase2L1GMT.gmt_cfi')
#process.l1tSAMuonsGmt = process.l1tStandaloneMuons.clone()
process.load('L1Trigger.L1CaloTrigger.l1tEGammaCrystalsEmulatorProducer_cfi')
process.load('L1Trigger.L1TTrackMatch.l1tGTTInputProducer_cfi')
process.load('L1Trigger.VertexFinder.l1tVertexProducer_cfi')
#process.l1tVertexFinderEmulator = process.l1tVertexProducer.clone()
#process.l1tVertexFinderEmulator.VertexReconstruction.Algorithm = "fastHistoEmulation"
#process.l1tVertexFinderEmulator.l1TracksInputTag = ("l1tGTTInputProducer","Level1TTTracksConverted")
process.load('L1Trigger.TrackFindingTracklet.L1HybridEmulationTracks_cff')
process.load('L1Trigger.Phase2L1ParticleFlow.l1tPFTracksFromL1Tracks_cfi')
process.load('L1Trigger.Phase2L1ParticleFlow.l1ctLayer1_cff')
process.load('L1Trigger.Phase2L1ParticleFlow.L1NNTauProducer_cff')
process.load('L1Trigger.Phase2L1ParticleFlow.l1tPFClustersFromCombinedCalo_cfi')
#process.l1tPFClustersFromL1EGClusters.src = cms.InputTag('L1EGammaClusterEmuProducer')
#process.l1tPFClustersFromCombinedCalo.phase2barrelCaloTowers = cms.VInputTag(cms.InputTag("LEGammaClusterEmuProducer","L1CaloTowerCollection",""))
#process.l1tPFClustersFromCombinedCaloHCal.phase2barrelCaloTowers = cms.VInputTag(cms.InputTag("L1EGammaClusterEmuProducer","L1CaloTowerCollection",""))
#process.l1tPFTracksFromL1Tracks.L1TrackTag = ("l1tGTTInputProducer","Level1TTTracksConverted")#l1tTTTracksFromExtendedTrackletEmulation", "Level1TTTracks
#process.L1NNTauProducerPuppi.L1PFObjects = cms.InputTag("l1ctLayer1:Puppi")



ntuple = cms.EDAnalyzer("TauNTuplizer",
    src = cms.InputTag("L1PFTauProducer","L1PFTaus"),
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
    ),
)

process.ntuplePF   = ntuple.clone()
process.ntupleNN   = ntuple.clone(src=cms.InputTag("L1NNTauProducer","L1PFTausNN") )
#process.ntuplePF2  = ntuple.clone(src=cms.InputTag("L1PFTauProducer2","L1PFTaus") )
#process.ntupleNN2  = ntuple.clone(src=cms.InputTag("L1NNTauProducer2","L1PFTausNN") )
#process.ntupleNN3  = ntuple.clone(src=cms.InputTag("L1NNTauProducer3","L1PFTausNN") )
  
modules = [
#    process.ntuplePF,
#    process.ntupleNN,
#    process.ntuplePF2,
#    process.ntupleNN2,
#    process.ntupleNN3
]

modules = cms.Task(
    ##process.simEcalEBTriggerPrimitiveDigis,
    #process.TTClustersFromPhase2TrackerDigis,
    #process.TTStubsFromPhase2TrackerDigis,
    #process.TrackerDTCProducer,
    #process.l1tTTTracksFromTrackletEmulation,
    #process.l1tPFTracksFromL1Tracks,
    #process.l1tEGammaClusterEmuProducer,
    #process.L1THGCalTriggerPrimitivesTask,
    #process.l1tSAMuonsGmt,
    #process.l1tGTTInputProducer,
    #process.l1tGTTInputProducerExtended,
    #process.l1tVertexFinderEmulator,
    process.L1TLayer1TaskInputsTask,
    process.L1TLayer1Task,
    process.l1tNNTauProducerPuppi,
    process.l1tNNTauProducerPF,
)
process.p = cms.Path()

process.p.associate(modules)

#process.p = cms.Path(sum(modules[1:], modules[0]))
process.TFileService = cms.Service("TFileService", fileName = cms.string("idTupleNew.root"))

process.output = cms.OutputModule("PoolOutputModule",
  fileName = cms.untracked.string("edmOutput.root")
)
process.e = cms.EndPath( process.output )


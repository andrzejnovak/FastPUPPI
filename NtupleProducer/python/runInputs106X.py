import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras

process = cms.Process("IN", eras.Phase2C9_trigger)
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.Geometry.GeometryExtended2026D41Reco_cff')
process.load('Configuration.Geometry.GeometryExtended2026D41_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase2_realistic', '')

process.load('SimCalorimetry.HcalTrigPrimProducers.hcaltpdigi_cff')
process.load('CalibCalorimetry.CaloTPG.CaloTPGTranscoder_cfi')
process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('L1Trigger.TrackTrigger.TrackTrigger_cff')
process.load("L1Trigger.TrackFindingTracklet.Tracklet_cfi") 
process.load("RecoVertex.BeamSpotProducer.BeamSpot_cfi")
process.load('SimCalorimetry.HcalTrigPrimProducers.hcaltpdigi_cff')
process.load('CalibCalorimetry.CaloTPG.CaloTPGTranscoder_cfi')




process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('file:/eos/cms/store/mc/PhaseIITDRSpring19DR/TT_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW/NoPU_106X_upgrade2023_realistic_v3-v2/40000/009982E7-AEA5-0042-B199-D1F75139909F.root'),
    inputCommands = cms.untracked.vstring("keep *", 
        "drop l1tHGCalTowerMapBXVector_hgcalTriggerPrimitiveDigiProducer_towerMap_HLT",
        "drop *_hgcalTriggerPrimitiveDigiProducer_*_*",
        "drop l1tEMTFHit2016Extras_simEmtfDigis_CSC_HLT",
        "drop l1tEMTFHit2016Extras_simEmtfDigis_RPC_HLT",
        "drop l1tEMTFHit2016s_simEmtfDigis__HLT",
        "drop l1tEMTFTrack2016Extras_simEmtfDigis__HLT",
        "drop l1tEMTFTrack2016s_simEmtfDigis__HLT")

)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(25))
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )

process.p = cms.Path(
    process.offlineBeamSpot +
    process.TTTracksFromTrackletEmulation +
    process.SimL1Emulator
)

process.out = cms.OutputModule("PoolOutputModule",
        fileName = cms.untracked.string("inputs106X.root"),
        outputCommands = cms.untracked.vstring("drop *",
            # --- GEN
            "keep *_genParticles_*_*",
            "keep *_ak4GenJetsNoNu_*_*",
            "keep *_genMetTrue_*_*",
            # --- PF IN
            "keep *_TTTracksFromTrackletEmulation_*_*",
            # ecal
            "keep *_l1EGammaCrystalsProducer_L1EGXtalClusterNoCuts_*",
            "keep *_l1EGammaCrystalsProducer_*_*",
            # HGC
            #"keep *_hgcalVFEProducer_*_IN", # uncomment to be able to re-run the concentrator
            "keep *_hgcalConcentratorProducer*_*_IN",
            #"keep *_hgcalBackEndLayer1Producer*_*_IN",
            "keep *_hgcalBackEndLayer2Producer*_*_IN",
            "keep *_hgcalTowerMapProducer_*_IN",
            "keep *_hgcalTowerProducer_*_IN",
            # muons
            "keep *_simGmtStage2Digis__*",
            "keep *_simGtExtFakeStage2Digis_*_*",
            "keep *_me0TriggerPseudoDigis_*_*",
            # hcal (old)
            "keep *_simHcalTriggerPrimitiveDigis__*",
            # new ecal and hcal
            "keep *_L1EGammaClusterEmuProducer_*_*",
            # --- Stage2 ---
            "keep *_simCaloStage2Digis_*_*",
            # --- VERTEXING ---
            "keep *_VertexProducer_*_*",
            "keep *_L1TkPrimaryVertex_*_*",
            # --- OTHERS FOR COMPARISONS
            # Jets & HTMiss
            "keep *_L1CaloJetProducer_*_*",
            "keep *_L1CaloJetHTTProducer_*_*",
            "keep *_L1TkCaloJets_*_*",
            "keep *_L1TkCaloHTMissVtx_*_*",
            "keep *_L1TkPrimaryVertex_*_*",
            "keep *_L1TrackerEtMiss_*_*",
            "keep *_L1TrackerHTMiss_*_*",
            "keep *_L1TrackerJets_*_*",
            "keep *_TwoLayerJets_*_*",
            # E/gamma
            "keep *_l1EGammaEEProducer_*_*",
            "keep *_L1TkElectronsCrystal_*_*",
            "keep *_L1TkElectronsEllipticMatchCrystal_*_*",
            "keep *_L1TkElectronsHGC_*_*",
            "keep *_L1TkElectronsEllipticMatchHGC_*_*",
            "keep *_L1TkElectronsLooseCrystal_*_*",
            "keep *_L1TkElectronsLooseHGC_*_*",
            "keep *_L1TkIsoElectronsCrystal_*_*",
            "keep *_L1TkIsoElectronsHGC_*_*",
            "keep *_L1TkPhotonsCrystal_*_*",
            "keep *_L1TkPhotonsHGC_*_*",
            "keep *_L1WP2Electrons_*_*",
            # Muons
            "keep *_L1TkGlbMuons_*_*",
            "keep *_L1TkMuons_*_*",
            "keep *_L1TkMuonsTP_*_*",
            "keep *_L1TkTauFromCalo_*_*",
            "keep *_l1KBmtfStubMatchedMuons_*_*",
            "keep *_l1TkMuonStubEndCap_*_*",
            "keep *_l1TkMuonStubEndCapS12_*_*",
            # Taus
            "keep *_L1TkCaloTaus_*_*",
            "keep *_L1TkEGTaus_*_*",
            "keep *_L1TkTauFromCalo_*_*",
            "keep *_L1TrackerTaus_*_*",
            # --- PF OUT
            "keep l1tPFClusters_*_*_*",
            "keep l1tPFTracks_*_*_*",
            "keep l1tPFCandidates_*_*_*",
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

def goSlim():
    process.out.outputCommands += [ "drop *_hgcalConcentratorProducer*_*_*", "drop *_hgcalTowerMapProducer_*_*", ]

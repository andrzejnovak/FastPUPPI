# Emulate the Inner Tracker chip output (CROC QCore encoding, CMSSW Phase2ITQCoreProducer) on PU 200 RAW.
#   cmsRun bitstream_cfg.py inputFiles=root://... maxEvents=20 outputFile=bits.root
import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
from Configuration.Eras.Era_Phase2C17I13M9_cff import Phase2C17I13M9
opts = VarParsing("analysis")
opts.parseArguments()
process = cms.Process("ITBITS", Phase2C17I13M9)
process.load("Configuration.Geometry.GeometryExtendedRun4D110Reco_cff")
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 5
process.source = cms.Source("PoolSource", fileNames=cms.untracked.vstring(opts.inputFiles),
                            inputCommands=cms.untracked.vstring("drop *", "keep *_simSiPixelDigis_Pixel_*"),
                            dropDescendantsOfDroppedBranches=cms.untracked.bool(False))
process.maxEvents.input = opts.maxEvents
process.bits = cms.EDProducer("Phase2ITQCoreProducer", src=cms.InputTag("generalTracks"),
                              siPixelDigi=cms.InputTag("simSiPixelDigis", "Pixel"))
process.p = cms.Path(process.bits)
process.out = cms.OutputModule("PoolOutputModule", fileName=cms.untracked.string(opts.outputFile),
                               outputCommands=cms.untracked.vstring("drop *", "keep *_bits_*_*", "keep *_simSiPixelDigis_Pixel_*"))
process.e = cms.EndPath(process.out)

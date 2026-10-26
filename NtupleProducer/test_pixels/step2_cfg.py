# Local test of the ntuple step: standard perfNano + gen-jet flavour + seeded-cone jets (R = 0.4 and 0.8).
#   cmsRun step2_cfg.py inputFiles=file:inputs.root out=perfNano.root
import sys, os
sys.path.insert(0, os.path.join(os.environ["CMSSW_BASE"], "src/FastPUPPI/NtupleProducer/python"))
from FWCore.ParameterSet.VarParsing import VarParsing
opts = VarParsing("analysis")
opts.register("extended", False, VarParsing.multiplicity.singleton, VarParsing.varType.bool,
              "also store L1 tracks (standard and extended) and vertices, Layer-1 PF/PUPPI candidates, gen leptons")
opts.register("out", "out.root", VarParsing.multiplicity.singleton, VarParsing.varType.string, "output file")
opts.parseArguments()
import runPerformanceNTuple as cfg
from runPerformanceNTuple import process
process.source.fileNames = opts.inputFiles
process.maxEvents.input = opts.maxEvents
process.outnano.fileName = opts.out
process.MessageLogger.cerr.FwkReport.reportEvery = 100
cfg.addGenJetFlavourTable()
cfg.addSeededConeJets()
cfg.addNGJetTags()
cfg.addSC8Jets()
if opts.extended:
    import FWCore.ParameterSet.Config as cms
    from FastPUPPI.NtupleProducer.l1TrackTable_cfi import l1TrackTable
    process.l1TrackTable = l1TrackTable.clone()
    process.l1TrackExtTable = l1TrackTable.clone(name="L1TracksExt", storeVertices=False,
                                                 tracks=cms.InputTag("l1tTTTracksFromExtendedTrackletEmulation", "Level1TTTracks"))
    process.extraPFStuff.add(process.l1TrackTable, process.l1TrackExtTable)
    cfg.saveCands()
    cfg.addGenLep([11, 13])

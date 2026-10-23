# Local test of the input step with the pixel-track tables.
#   cmsRun step1_cfg.py inputFiles=... out=... maxEvents=...
import sys, os
sys.path.insert(0, os.path.join(os.environ["CMSSW_BASE"], "src/FastPUPPI/NtupleProducer/python"))
from FWCore.ParameterSet.VarParsing import VarParsing
opts = VarParsing("analysis")
opts.register("keepRaw", False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "also keep pixel EDM collections")
opts.register("pixels", True, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "add pixel-track tables")
opts.register("skipEvents", 0, VarParsing.multiplicity.singleton, VarParsing.varType.int, "events to skip")
opts.register("out", "out.root", VarParsing.multiplicity.singleton, VarParsing.varType.string, "output file")
opts.parseArguments()
import runInputs151X as cfg
from runInputs151X import process
process.source.fileNames = opts.inputFiles
process.source.skipEvents = __import__("FWCore.ParameterSet.Config", fromlist=["cms"]).untracked.uint32(opts.skipEvents)
process.maxEvents.input = opts.maxEvents
process.out.fileName = opts.out
if opts.pixels:
    cfg.addPixelTracks(keepRaw=opts.keepRaw)

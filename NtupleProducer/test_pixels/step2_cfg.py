# Local test of the ntuple step: standard perfNano + gen-jet flavour + seeded-cone jets.
#   cmsRun step2_cfg.py inputFiles=file:inputs.root out=perfNano.root
import sys, os
sys.path.insert(0, os.path.join(os.environ["CMSSW_BASE"], "src/FastPUPPI/NtupleProducer/python"))
from FWCore.ParameterSet.VarParsing import VarParsing
opts = VarParsing("analysis")
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

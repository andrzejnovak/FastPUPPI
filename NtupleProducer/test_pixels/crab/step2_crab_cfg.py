# Ntuple step run inside the CRAB job on the step-1 output.
import FWCore.ParameterSet.Config as cms
import FastPUPPI.NtupleProducer.runPerformanceNTuple as cfg
from FastPUPPI.NtupleProducer.runPerformanceNTuple import process
process.source.fileNames = ["file:inputs.root"]
process.maxEvents.input = -1
process.outnano.fileName = "perfNano.root"
process.MessageLogger.cerr.FwkReport.reportEvery = 100
cfg.addGenJetFlavourTable()
cfg.addSeededConeJets()
cfg.addNGJetTags()

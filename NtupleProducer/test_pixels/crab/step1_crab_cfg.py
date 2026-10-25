# CRAB PSet for the input step with pixel-track tables (CRAB injects the input files).
import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
opts = VarParsing("analysis")
opts.parseArguments()
import FastPUPPI.NtupleProducer.runInputs151X as cfg
from FastPUPPI.NtupleProducer.runInputs151X import process
process.maxEvents.input = opts.maxEvents
process.out.fileName = "inputs.root"
cfg.addPixelTracks()

# Pythia8 CP5, 14 TeV: ggH + jet (top-mass dependent), pT-hat > 150 GeV, H -> bb (private, for L1 trigger studies)
import FWCore.ParameterSet.Config as cms
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *

generator = cms.EDFilter("Pythia8ConcurrentGeneratorFilter",
    comEnergy=cms.double(14000.),
    filterEfficiency=cms.untracked.double(1.0),
    maxEventsToPrint=cms.untracked.int32(0),
    pythiaHepMCVerbosity=cms.untracked.bool(False),
    pythiaPylistVerbosity=cms.untracked.int32(0),
    PythiaParameters=cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        processParameters=cms.vstring(
            "HiggsSM:gg2Hg(l:t) = on",
            "HiggsSM:qg2Hq(l:t) = on",
            "HiggsSM:qqbar2Hg(l:t) = on",
            "PhaseSpace:pTHatMin = 150.",
            "25:m0 = 125.0",
            "25:onMode = off",
            "25:onIfMatch = 5 -5",
        ),
        parameterSets=cms.vstring("pythia8CommonSettings", "pythia8CP5Settings", "processParameters"),
    ),
)

ProductionFilterSequence = cms.Sequence(generator)

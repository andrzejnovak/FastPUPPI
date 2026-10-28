# Pythia8 CP5, 14 TeV: inclusive hard QCD (pT-hat > 30, biased towards high pT-hat as pT-hat^4.5 / 30^4.5, event weights
# compensate), filtered at generator level for >= 4 b quarks (last copy) with pT > 15 GeV, |eta| < 2.6: the genuine-4b
# multijet background of HH->4b at L1-object level (private, for L1 trigger / scouting studies). Weight per event:
# sigma(generated) x w / N_generated (N_generated from the job's TrigReport, not the filtered count).
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
            "HardQCD:all = on",
            "PhaseSpace:pTHatMin = 30.",
            "PhaseSpace:bias2Selection = on",
            "PhaseSpace:bias2SelectionPow = 4.5",
            "PhaseSpace:bias2SelectionRef = 30.",
        ),
        parameterSets=cms.vstring("pythia8CommonSettings", "pythia8CP5Settings", "processParameters"),
    ),
)

genParticlesForFilter = cms.EDProducer("GenParticleProducer",
    saveBarCodes=cms.untracked.bool(True),
    src=cms.InputTag("generator", "unsmeared"),
    abortOnUnknownPDGCode=cms.untracked.bool(False),
)
bQuarksForFilter = cms.EDFilter("GenParticleSelector",
    src=cms.InputTag("genParticlesForFilter"),
    cut=cms.string("abs(pdgId) == 5 && isLastCopy() && pt > 15 && abs(eta) < 2.6"),
    filter=cms.bool(False),
)
fourBFilter = cms.EDFilter("CandViewCountFilter", src=cms.InputTag("bQuarksForFilter"), minNumber=cms.uint32(4))

ProductionFilterSequence = cms.Sequence(generator * genParticlesForFilter * bQuarksForFilter * fourBFilter)

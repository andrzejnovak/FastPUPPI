#!/usr/bin/env python3
"""Offline AK4 PUPPI jets (slimmedJetsPuppi) from MINIAOD, keyed by (lumi, event), for the analysis-level selection.

    python3 dump_offline.py OUT.npz LFN
Per jet: pT, eta, phi, mass, UParT / ParticleNet / DeepJet b scores, hadron flavour, constituent counts and
energy fractions (for a loose jet ID).
"""
import sys

import numpy as np
from DataFormats.FWLite import Events, Handle

out, lfn = sys.argv[1], sys.argv[2]
h = Handle("std::vector<pat::Jet>")
UPART, PNET = "pfUnifiedParticleTransformerAK4DiscriminatorsJetTags:BvsAll", \
    "pfParticleNetFromMiniAODAK4PuppiCentralDiscriminatorsJetTags:BvsAll"
DJ = ["pfDeepFlavourJetTags:probb", "pfDeepFlavourJetTags:probbb", "pfDeepFlavourJetTags:problepb"]
cols = {k: [] for k in ("lumi", "event", "njet", "pt", "eta", "phi", "mass", "upart", "pnet", "deepjet", "flav",
                        "nconst", "chf", "nhf", "nemf")}
for e in Events("root://cms-xrd-global.cern.ch/" + lfn):
    e.getByLabel("slimmedJetsPuppi", h)
    a = e.eventAuxiliary().id()
    js = [j for j in h.product() if j.pt() > 20 and abs(j.eta()) < 2.5]
    cols["lumi"].append(a.luminosityBlock())
    cols["event"].append(a.event())
    cols["njet"].append(len(js))
    for j in js:
        cols["pt"].append(j.pt())
        cols["eta"].append(j.eta())
        cols["phi"].append(j.phi())
        cols["mass"].append(j.mass())
        cols["upart"].append(j.bDiscriminator(UPART))
        cols["pnet"].append(j.bDiscriminator(PNET))
        cols["deepjet"].append(sum(j.bDiscriminator(d) for d in DJ))
        cols["flav"].append(j.hadronFlavour())
        cols["nconst"].append(j.numberOfDaughters())
        cols["chf"].append(j.chargedHadronEnergyFraction())
        cols["nhf"].append(j.neutralHadronEnergyFraction())
        cols["nemf"].append(j.neutralEmEnergyFraction())
np.savez(out, **{k: np.array(v) for k, v in cols.items()})
print(f"{len(cols['lumi'])} events, {len(cols['pt'])} jets -> {out}")

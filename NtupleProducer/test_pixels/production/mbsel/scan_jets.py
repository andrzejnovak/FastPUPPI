#!/usr/bin/env python3
"""Stored L1 jets (14_0 emulator SC4 jets saved in the MinBias RAW, |eta| < 5) for every event of a list of files:
the NJ leading jets (pT, eta, phi) and the central HT, for forward-jet seeds (VBF) that the HT scan cannot select.

    python3 scan_jets.py OUT.npz LFN [LFN ...]
"""
import sys

import numpy as np
from DataFormats.FWLite import Events, Handle

NJ = 8
out, lfns = sys.argv[1], sys.argv[2:]
h = Handle("std::vector<l1t::PFJet>")
ids, jets, bad = [], [], []
for lfn in lfns:
    try:
        for e in Events("root://cms-xrd-global.cern.ch/" + lfn):
            e.getByLabel("l1tSC4PFL1PuppiCorrectedEmulator", h)
            a = e.eventAuxiliary().id()
            js = sorted(((j.pt(), j.eta(), j.phi()) for j in h.product() if j.pt() > 15), reverse=True)[:NJ]
            ht = sum(p for p, eta, _ in js if p > 30 and abs(eta) < 2.4)
            ids.append((a.run(), a.luminosityBlock(), a.event(), ht))
            jets.append(js + [(0.0, 0.0, 0.0)] * (NJ - len(js)))
    except Exception as ex:  # unreadable file: record it, keep going
        bad.append(lfn)
        print("BAD", lfn, ex, flush=True)
r = np.array(ids, dtype=float).reshape(-1, 4)
j = np.array(jets, dtype=np.float32).reshape(-1, NJ, 3)
np.savez(out, run=r[:, 0].astype(np.int64), lumi=r[:, 1].astype(np.int64), event=r[:, 2].astype(np.int64), ht=r[:, 3],
         pt=j[:, :, 0], eta=j[:, :, 1], phi=j[:, :, 2], bad=np.array(bad))
print(f"{len(ids)} events from {len(lfns) - len(bad)} files ({len(bad)} bad) -> {out}")

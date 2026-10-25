#!/usr/bin/env python3
"""Stored L1 HT (14_0 emulator SC4 jets saved in the MinBias RAW, pT > 30, |eta| < 2.4) for every event of a list of files.

    python3 scan_ht.py OUT.npz LFN [LFN ...]
Used to preselect minimum-bias events for the targeted pixel production without re-running the L1 emulation.
"""
import sys

import numpy as np
from DataFormats.FWLite import Events, Handle

out, lfns = sys.argv[1], sys.argv[2:]
h = Handle("std::vector<l1t::PFJet>")
rows, bad = [], []
for lfn in lfns:
    try:
        for e in Events("root://cms-xrd-global.cern.ch/" + lfn):
            e.getByLabel("l1tSC4PFL1PuppiCorrectedEmulator", h)
            a = e.eventAuxiliary().id()
            ht = sum(j.pt() for j in h.product() if j.pt() > 30 and abs(j.eta()) < 2.4)
            rows.append((a.run(), a.luminosityBlock(), a.event(), ht))
    except Exception as ex:  # unreadable file: record it, keep going
        bad.append(lfn)
        print("BAD", lfn, ex, flush=True)
r = np.array(rows, dtype=float).reshape(-1, 4)
np.savez(out, run=r[:, 0].astype(np.int64), lumi=r[:, 1].astype(np.int64), event=r[:, 2].astype(np.int64), ht=r[:, 3],
         bad=np.array(bad))
print(f"{len(rows)} events from {len(lfns) - len(bad)} files ({len(bad)} bad) -> {out}")

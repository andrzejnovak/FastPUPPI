#!/usr/bin/env python3
"""Pick minimum-bias events with L1 HT above a cut from the official-input ntuples (for a targeted pixel production).

    python3 select_events.py OUT.txt HTCUT "perfNano_MinBias_*.root"
HT as in the seed study: L1 SC4NG jets with pT > 30 GeV, |eta| < 2.4. Writes run:lumi:event per line; prints totals.
"""
import glob
import sys

import awkward as ak
import numpy as np
import uproot

out, cut, pat = sys.argv[1], float(sys.argv[2]), sys.argv[3]
n_tot, rows = 0, []
for f in sorted(glob.glob(pat)):
    a = uproot.open(f)["Events"].arrays(["run", "luminosityBlock", "event", "L1NGJets_pt", "L1NGJets_eta"])
    pt, eta = a.L1NGJets_pt, a.L1NGJets_eta
    ht = ak.to_numpy(ak.sum(pt[(pt > 30) & (abs(eta) < 2.4)], axis=1))
    sel = ht > cut
    n_tot += len(ht)
    rows += [f"{r}:{l}:{e}" for r, l, e in zip(ak.to_numpy(a.run)[sel], ak.to_numpy(a.luminosityBlock)[sel], ak.to_numpy(a.event)[sel])]
open(out, "w").write("\n".join(rows) + "\n")
print(f"{len(rows)} of {n_tot} events with HT > {cut:.0f} GeV ({len(rows) / n_tot:.4f}) -> {out}")

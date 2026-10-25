#!/usr/bin/env python3
"""How well do objects available early in the L1 latency point at the final b jets?

    python3 seed_match.py OUT.json "HH4b_glob"

For HH->4b L1 SC4 jets (pT > 30 GeV, |eta| < 2.4) matched to a b gen jet: distance to the nearest L1 track jet
(Global Track Trigger, shortly after the 5 us track arrival) and to the nearest L1 calo jet, and the fraction
within dR < 0.1 / 0.2 / 0.3. Also how many such objects an event has above a few pT thresholds (requests per event).
"""
import glob
import json
import sys

import awkward as ak
import numpy as np
import uproot

out, pat = sys.argv[1:3]
BR = ["L1NGJets_pt", "L1NGJets_eta", "L1NGJets_phi", "GenJets_pt", "GenJets_eta", "GenJets_phi", "GenJets_hadronFlavour",
      "L1TKJets_pt", "L1TKJets_eta", "L1TKJets_phi", "L1CaloJets_pt", "L1CaloJets_eta", "L1CaloJets_phi"]
a = ak.concatenate([uproot.open(f)["Events"].arrays(filter_name=BR) for f in sorted(glob.glob(pat))])


def vec(prefix):
    return ak.zip({"pt": a[f"{prefix}_pt"], "eta": a[f"{prefix}_eta"], "phi": a[f"{prefix}_phi"]})


def mindr(x, y):
    p = ak.cartesian({"x": x, "y": y}, nested=True)
    dr = np.hypot(p.x.eta - p.y.eta, (p.x.phi - p.y.phi + np.pi) % (2 * np.pi) - np.pi)
    return ak.fill_none(ak.min(dr, axis=2), 9.0)


jets, gen = vec("L1NGJets"), vec("GenJets")
jets = jets[(jets.pt > 30) & (abs(jets.eta) < 2.4)]
genb = gen[(a.GenJets_hadronFlavour == 5) & (gen.pt > 15)]
bjets = jets[mindr(jets, genb) < 0.3]
res = {"n_bjets": int(ak.sum(ak.num(bjets)))}
for name in ("L1TKJets", "L1CaloJets"):
    o = vec(name)
    for thr in (5, 10, 20):
        oo = o[o.pt > thr]
        d = ak.to_numpy(ak.flatten(mindr(bjets, oo)))
        res[f"{name}_pt>{thr}"] = {f"frac_dR<{c}": float((d < c).mean()) for c in (0.1, 0.2, 0.3)} | {
            "median_dR": float(np.median(d)), "mean_objects_per_event": float(ak.mean(ak.num(oo[abs(oo.eta) < 2.4])))}
    print(name, json.dumps({k: v for k, v in res.items() if k.startswith(name)}), flush=True)
json.dump(res, open(out, "w"), indent=1)

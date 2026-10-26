#!/usr/bin/env python3
"""ZH(nunu) H -> bb / cc: how much of the signal the planned Phase-2 menu keeps, vs the Z pT (generator MET).

    python3 zh_met.py OUT.json SAMPLE:GLOB [SAMPLE:GLOB ...]
Fiducial: two generator jets of the Higgs flavour (hadronFlavour 5 or 4) with pT > 25, |eta| < 2.5.
Seeds (online thresholds from the CMSSW step1_2024 scalings):
  MET200  L1 PUPPI MET (all candidates) > 97.0      MHT140  SC4 corrected MHT > 128.1
  jets    SinglePuppiJet230, DoublePuppiJet112_112 (|deta| < 1.6), PuppiHT450, PuppiHT400 + QuadJet70_55_40_40
Also the efficiency of looser MET cuts (online), for a "lower MET + flavour-tagged jets" seed.
"""
import glob
import json
import sys

import awkward as ak
import numpy as np
import uproot

from vbf_menu import HT_ALONE, HT_QUAD, QUAD_BARREL, QUAD_ENDCAP, thr

MET200, MHT140 = 97.0, 128.1
MET_SCAN = (37.5, 49.4, 61.3, 73.2, 85.1, 97.0)  # online values of offline-equivalent 100, 120, ..., 200
EDGES = [0, 100, 150, 200, 250, 300, 400, 1000]
BR = ["GenJets_pt", "GenJets_eta", "GenJets_hadronFlavour", "genMet_pt", "L1PuppiMet_pt", "scPuppiCorrMHTMet_pt",
      "scPuppiCorrJets_pt", "scPuppiCorrJets_eta", "L1NGJets_pt", "L1NGJets_eta"]


def seeds(a):
    n = len(a)
    j = ak.zip({k: a[f"scPuppiCorrJets_{k}"] for k in ("pt", "eta")})
    jc = j[abs(j.eta) < 2.4]
    single = ak.to_numpy(ak.any(jc.pt > ak.unflatten(thr(230, ak.to_numpy(ak.flatten(jc.eta))), ak.num(jc)), axis=1))
    pc = ak.combinations(jc, 2)
    ta = ak.unflatten(thr(112, ak.to_numpy(ak.flatten(pc["0"].eta))), ak.num(pc))
    tb = ak.unflatten(thr(112, ak.to_numpy(ak.flatten(pc["1"].eta))), ak.num(pc))
    double = ak.to_numpy(ak.any((pc["0"].pt > ta) & (pc["1"].pt > tb) & (abs(pc["0"].eta - pc["1"].eta) < 1.6), axis=1))
    pt, eta = a.L1NGJets_pt, a.L1NGJets_eta
    acc = abs(eta) < 2.4
    ht = ak.to_numpy(ak.sum(pt[acc & (pt > 30)], axis=1))
    js = ak.argsort(pt[acc], ascending=False)
    jpt, jeta = ak.pad_none(pt[acc][js], 4, clip=True), ak.pad_none(eta[acc][js], 4, clip=True)
    quad = np.ones(n, bool)
    for k in range(4):
        p, e = ak.to_numpy(ak.fill_none(jpt[:, k], 0.0)), ak.to_numpy(ak.fill_none(jeta[:, k], 0.0))
        quad &= p > np.where(abs(e) < 1.5, QUAD_BARREL[k], QUAD_ENDCAP[k])
    met = ak.to_numpy(a.L1PuppiMet_pt)
    return {"MET200": met > MET200, "MHT140": ak.to_numpy(a.scPuppiCorrMHTMet_pt) > MHT140,
            "jets": single | double | (quad & (ht > HT_QUAD)) | (ht > HT_ALONE)}, met


if __name__ == "__main__":
    res = {}
    for spec in sys.argv[2:]:
        name, pat = spec.split(":", 1)
        files = sorted(glob.glob(pat))
        a = ak.concatenate([uproot.open(f)["Events"].arrays(filter_name=BR) for f in files])
        flav = 4 if name.endswith("cc") else 5
        g = (a.GenJets_hadronFlavour == flav) & (a.GenJets_pt > 25) & (abs(a.GenJets_eta) < 2.5)
        fid = ak.to_numpy(ak.sum(g, axis=1)) >= 2
        s, met = seeds(a)
        anyseed = np.logical_or.reduce(list(s.values()))
        gmet = ak.to_numpy(a.genMet_pt)
        rows = []
        for lo, hi in zip(EDGES[:-1], EDGES[1:]):
            sel = fid & (gmet >= lo) & (gmet < hi)
            n = int(sel.sum())
            r = {"genmet": [lo, hi], "n": n}
            if n:
                r.update({k: float(v[sel].mean()) for k, v in s.items()})
                r["menu"] = float(anyseed[sel].mean())
                r.update({f"met_gt_{x:g}": float((met[sel] > x).mean()) for x in MET_SCAN})
            rows.append(r)
        hi = fid & (gmet > 150)
        res[name] = {"files": len(files), "events": len(a), "fiducial": int(fid.sum()), "by_genmet": rows,
                     "genmet_gt150": {"n": int(hi.sum()), "menu": float(anyseed[hi].mean()),
                                      **{k: float(v[hi].mean()) for k, v in s.items()}}}
        print(name, len(files), "files", len(a), "events,", int(fid.sum()), "fiducial", flush=True)
        print("  genMET > 150:", res[name]["genmet_gt150"])
        for r in rows:
            print("  ", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    json.dump(res, open(sys.argv[1], "w"), indent=1)

#!/usr/bin/env python3
"""VBF H->cc / H->bb: which fraction of signal in a generator-level VBF acceptance the planned Phase-2 menu keeps.

    python3 vbf_menu.py OUT.json SAMPLE:GLOB [SAMPLE:GLOB ...]
Acceptance (generator jets): two jets of the Higgs flavour (hadronFlavour 4 or 5) with pT > 30, |eta| < 2.4, and two
other jets with pT > 30, |eta| < 4.7, m_jj > 500 GeV, |deta| > 3 (the highest-m_jj such pair).
Menu (online thresholds from the CMSSW step1_2024 scalings, per |eta| region barrel/endcap/HGCAL-forward/HF):
  VBF       DoublePuppiJet160_35_mass620: SC4 jets |eta| < 5, one above 160 and one above 35 (offline-equivalent),
            m_jj > 620 (any such pair)
  SingleJet SinglePuppiJet230; DoubleJet DoublePuppiJet112_112 with |deta| < 1.6 (|eta| < 2.4)
  HT        PuppiHT450 and PuppiHT400 + QuadJet70_55_40_40 (as direct_rate.py, on the NG jets)
"""
import glob
import json
import sys

import awkward as ak
import numpy as np
import uproot

ETA_EDGES = np.array([0, 1.5, 2.4, 3.0, 99])
THR = {160: (105.5, 94.3, 92.1, 124.7), 35: (25.0, 25.0, 25.0, 30.8), 230: (157.0, 138.3, 149.5, 177.4),
       112: (70.2, 64.1, 52.8, 88.6)}
QUAD_BARREL, QUAD_ENDCAP, HT_QUAD, HT_ALONE = (41.1, 29.4, 25.0, 25.0), (32.7, 25.0, 25.0, 25.0), 316.3, 361.0
BR = ["GenJets_pt", "GenJets_eta", "GenJets_phi", "GenJets_mass", "GenJets_hadronFlavour", "scPuppiCorrJets_pt",
      "scPuppiCorrJets_eta", "scPuppiCorrJets_phi", "scPuppiCorrJets_mass", "L1NGJets_pt", "L1NGJets_eta"]


def thr(pt_off, eta):
    return np.asarray(THR[pt_off])[np.clip(np.digitize(np.abs(eta), ETA_EDGES) - 1, 0, 3)]


def mjj(pt1, eta1, phi1, m1, pt2, eta2, phi2, m2):
    v1 = ak.zip({"pt": pt1, "eta": eta1, "phi": phi1, "mass": m1}, with_name="Momentum4D")
    v2 = ak.zip({"pt": pt2, "eta": eta2, "phi": phi2, "mass": m2}, with_name="Momentum4D")
    return (v1 + v2).mass


def menu_flags(a):
    """Per-event decisions of the planned hadronic seeds (VBF, SingleJet, DoubleJet, HT) on an events array."""
    n = len(a)
    j = ak.zip({k: a[f"scPuppiCorrJets_{k}"] for k in ("pt", "eta", "phi", "mass")})
    jp = ak.cartesian([j, j], nested=False)
    l1, l2 = jp["0"], jp["1"]
    distinct = ~((l1.pt == l2.pt) & (l1.eta == l2.eta) & (l1.phi == l2.phi))
    mm = mjj(l1.pt, l1.eta, l1.phi, l1.mass, l2.pt, l2.eta, l2.phi, l2.mass)
    t160 = ak.unflatten(thr(160, ak.to_numpy(ak.flatten(l1.eta))), ak.num(l1))
    t35 = ak.unflatten(thr(35, ak.to_numpy(ak.flatten(l2.eta))), ak.num(l2))
    vbf = ak.to_numpy(ak.any(distinct & (l1.pt > t160) & (l2.pt > t35) & (mm > 620), axis=1))
    jc = j[abs(j.eta) < 2.4]
    t230 = ak.unflatten(thr(230, ak.to_numpy(ak.flatten(jc.eta))), ak.num(jc))
    single = ak.to_numpy(ak.any(jc.pt > t230, axis=1))
    pc = ak.combinations(jc, 2)
    t112a = ak.unflatten(thr(112, ak.to_numpy(ak.flatten(pc["0"].eta))), ak.num(pc))
    t112b = ak.unflatten(thr(112, ak.to_numpy(ak.flatten(pc["1"].eta))), ak.num(pc))
    double = ak.to_numpy(ak.any((pc["0"].pt > t112a) & (pc["1"].pt > t112b) & (abs(pc["0"].eta - pc["1"].eta) < 1.6), axis=1))
    # HT seeds as direct_rate.py (NG jets, |eta| < 2.4)
    pt, eta = a.L1NGJets_pt, a.L1NGJets_eta
    acc24 = abs(eta) < 2.4
    ht = ak.to_numpy(ak.sum(pt[acc24 & (pt > 30)], axis=1))
    js = ak.argsort(pt[acc24], ascending=False)
    jpt, jeta = ak.pad_none(pt[acc24][js], 4, clip=True), ak.pad_none(eta[acc24][js], 4, clip=True)
    quad = np.ones(n, bool)
    for k in range(4):
        p, e = ak.to_numpy(ak.fill_none(jpt[:, k], 0.0)), ak.to_numpy(ak.fill_none(jeta[:, k], 0.0))
        quad &= p > np.where(abs(e) < 1.5, QUAD_BARREL[k], QUAD_ENDCAP[k])
    htseed = (quad & (ht > HT_QUAD)) | (ht > HT_ALONE)
    return {"VBF": vbf, "SingleJet": single, "DoubleJet": double, "HT": htseed}


def evaluate(files, flav):
    import vector
    vector.register_awkward()
    a = ak.concatenate([uproot.open(f)["Events"].arrays(filter_name=BR) for f in files])
    n = len(a)
    # acceptance
    g = ak.zip({k: a[f"GenJets_{k}"] for k in ("pt", "eta", "phi", "mass", "hadronFlavour")})
    hq = g[(g.hadronFlavour == flav) & (g.pt > 30) & (abs(g.eta) < 2.4)]
    oth = g[(g.hadronFlavour != flav) & (g.pt > 30) & (abs(g.eta) < 4.7)]
    pr = ak.combinations(oth, 2)
    m = mjj(pr["0"].pt, pr["0"].eta, pr["0"].phi, pr["0"].mass, pr["1"].pt, pr["1"].eta, pr["1"].phi, pr["1"].mass)
    vbf_ok = (m > 500) & (abs(pr["0"].eta - pr["1"].eta) > 3)
    acc = ak.to_numpy((ak.num(hq) >= 2) & ak.any(vbf_ok, axis=1))
    seeds = menu_flags(a)
    vbf, single, double, htseed = (seeds[k] for k in ("VBF", "SingleJet", "DoubleJet", "HT"))
    anyseed = vbf | single | double | htseed
    na = acc.sum()
    out = {"events": int(n), "accepted": int(na), "acceptance": float(na / n),
           "menu_eff_on_accepted": float((anyseed & acc).sum() / na),
           "seed_eff_on_accepted": {k: float((v & acc).sum() / na) for k, v in seeds.items()},
           "only_this_seed": {k: float((v & acc & ~np.logical_or.reduce([w for kk, w in seeds.items() if kk != k])).sum() / na)
                              for k, v in seeds.items()},
           "menu_eff_all_events": float(anyseed.mean())}
    return out


if __name__ == "__main__":
    res = {}
    for spec in sys.argv[2:]:
        name, pat = spec.split(":", 1)
        files = sorted(glob.glob(pat))
        res[name] = evaluate(files, 4 if "CC" in name else 5)
        res[name]["files"] = len(files)
        print(name, json.dumps(res[name]), flush=True)
    json.dump(res, open(sys.argv[1], "w"), indent=1)

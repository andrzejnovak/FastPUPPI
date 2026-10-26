#!/usr/bin/env python3
"""First look at boosted H -> cc / bb in L1 R = 0.8 jets (private ggH + jet samples) against minimum bias.

    python3 fatjet_first.py OUT.json SIG_NAME:SIG_GLOB [...] MB:MB_GLOB
Higgs proxy (no generator Higgs stored yet): vector sum of the generator jets of the Higgs flavour (pT > 20) within
dR < 0.8 of the leading one. Signal L1 jet: the highest-pT SC8 jet within dR < 0.8 of the proxy. Menu: as
vbf_menu.py (VBF, SingleJet230, DoubleJet112, HT seeds). Minimum bias: rate of "leading SC8 jet pT > X" (and with
two-prong score > 0.5), from the re-simulated events (preselected, so only meaningful where the preselection is
complete) weighted to all 1,999,360 events.
"""
import glob
import json
import sys

import awkward as ak
import numpy as np
import uproot
import vector

vector.register_awkward()
sys.path.insert(0, ".")
from vbf_menu import THR, thr  # noqa: E402

MB_TOTAL, BX_KHZ = 1999360, 2760 * 11.245
BR = ["GenJets_*", "sc8PuppiCorrJets_*", "L1SC8ProngJets_*", "scPuppiCorrJets_*", "L1NGJets_pt", "L1NGJets_eta"]


def load(pat):
    return ak.concatenate([uproot.open(f)["Events"].arrays(filter_name=BR) for f in sorted(glob.glob(pat))])


def dr(e1, p1, e2, p2):
    return np.hypot(e1 - e2, (p1 - p2 + np.pi) % (2 * np.pi) - np.pi)


def signal(a, flav):
    g = ak.zip({"pt": a.GenJets_pt, "eta": a.GenJets_eta, "phi": a.GenJets_phi, "mass": a.GenJets_mass,
                "fl": a.GenJets_hadronFlavour}, with_name="Momentum4D")
    q = g[(g.fl == flav) & (g.pt > 20)]
    q = q[ak.argsort(q.pt, ascending=False)]
    lead = ak.firsts(q)
    near = q[dr(q.eta, q.phi, lead.eta, lead.phi) < 0.8]
    h = ak.zip({"pt": ak.sum(near.px, axis=1), "eta": 0 * ak.num(near)}, with_name=None)
    hx, hy, hz = ak.sum(near.px, axis=1), ak.sum(near.py, axis=1), ak.sum(near.pz, axis=1)
    hpt = np.hypot(ak.to_numpy(ak.fill_none(hx, 0)), ak.to_numpy(ak.fill_none(hy, 0)))
    heta = np.arcsinh(ak.to_numpy(ak.fill_none(hz, 0)) / np.maximum(hpt, 1e-6))
    hphi = np.arctan2(ak.to_numpy(ak.fill_none(hy, 0)), ak.to_numpy(ak.fill_none(hx, 0)))
    nq = ak.to_numpy(ak.num(near))
    # matched L1 SC8 jet (corrected) and two-prong score (same cones, uncorrected emulator jets)
    j8 = ak.zip({k: a[f"sc8PuppiCorrJets_{k}"] for k in ("pt", "eta", "phi", "mass")})
    m = dr(j8.eta, j8.phi, heta, hphi) < 0.8
    j8m = ak.firsts(j8[m][ak.argsort(j8[m].pt, ascending=False)])
    p8 = ak.zip({k: a[f"L1SC8ProngJets_{k}"] for k in ("pt", "eta", "phi", "mass", "score_nprong")})
    mp = dr(p8.eta, p8.phi, heta, hphi) < 0.8
    p8m = ak.firsts(p8[mp][ak.argsort(p8[mp].pt, ascending=False)])
    return {"hpt": hpt, "heta": heta, "nq": nq, "l1pt": ak.to_numpy(ak.fill_none(j8m.pt, 0.0)),
            "l1mass": ak.to_numpy(ak.fill_none(j8m.mass, 0.0)), "prong": ak.to_numpy(ak.fill_none(p8m.score_nprong, -1.0))}


def menu(a):
    j = ak.zip({k: a[f"scPuppiCorrJets_{k}"] for k in ("pt", "eta", "phi", "mass")})
    jc = j[abs(j.eta) < 2.4]
    t230 = ak.unflatten(thr(230, ak.to_numpy(ak.flatten(jc.eta))), ak.num(jc))
    single = ak.to_numpy(ak.any(jc.pt > t230, axis=1))
    pt, eta = a.L1NGJets_pt, a.L1NGJets_eta
    ht = ak.to_numpy(ak.sum(pt[(abs(eta) < 2.4) & (pt > 30)], axis=1))
    return {"single": single, "ht450": ht > 361.0}


res = {}
sigs, mb = sys.argv[2:-1], sys.argv[-1].split(":", 1)[1]
for spec in sigs:
    name, pat = spec.split(":", 1)
    a = load(pat)
    s = signal(a, 4 if "cc" in name else 5)
    mn = menu(a)
    fid = (s["hpt"] > 0) & (abs(s["heta"]) < 2.4) & (s["nq"] >= 2)
    edges = [150, 200, 250, 300, 350, 400, 500, 700]
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = fid & (s["hpt"] >= lo) & (s["hpt"] < hi)
        n = int(sel.sum())
        rows.append({"hpt": [lo, hi], "n": n, "menu_single_or_ht": float((mn["single"] | mn["ht450"])[sel].mean()) if n else None,
                     "l1_sc8_matched": float((s["l1pt"][sel] > 0).mean()) if n else None,
                     "l1_sc8_pt_median": float(np.median(s["l1pt"][sel])) if n else None,
                     "l1_sc8_mass_median": float(np.median(s["l1mass"][sel])) if n else None,
                     "prong_gt05": float((s["prong"][sel] > 0.5).mean()) if n else None})
    res[name] = {"events": len(a), "fiducial_merged": int(fid.sum()), "by_hpt": rows}
    print(name, len(a), "events,", int(fid.sum()), "with a merged H candidate (>=2 jets of the flavour within dR 0.8)")
    for r in rows:
        print("  ", r)
# minimum bias: leading SC8 jet rate
a = load(mb)
j8 = a.sc8PuppiCorrJets_pt[abs(a.sc8PuppiCorrJets_eta) < 2.4]
lead = ak.to_numpy(ak.fill_none(ak.max(j8, axis=1), 0.0))
p8 = a[["L1SC8ProngJets_pt", "L1SC8ProngJets_eta", "L1SC8ProngJets_score_nprong"]]
c = abs(p8.L1SC8ProngJets_eta) < 2.4
pl = ak.to_numpy(ak.fill_none(ak.max(ak.where(p8.L1SC8ProngJets_score_nprong[c] > 0.5, p8.L1SC8ProngJets_pt[c], 0.0), axis=1), 0.0))
w = BX_KHZ / MB_TOTAL
res["minbias"] = {"events": len(a), "rate_khz_lead_sc8_gt": {x: float((lead > x).sum() * w) for x in (100, 125, 150, 175, 200, 250)},
                  "rate_khz_lead_prong05_sc8_gt": {x: float((pl > x).sum() * w) for x in (100, 125, 150, 175, 200, 250)}}
print("minimum bias", res["minbias"])
json.dump(res, open(sys.argv[1], "w"), indent=1)

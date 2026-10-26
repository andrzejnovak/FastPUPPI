#!/usr/bin/env python3
"""HH->4b offline selections from today's proxy to softer "future" ones, to see how much L1 headroom becomes usable.

    python3 offline_scenarios.py OUT.npz OUT.json "HH4B_GLOB" "QCD_GLOB"
Same jets, UParT working points (10% / 1% light mistag on QCD jets, pT > 30), b-response correction, pairing and
mass window as offline_sel.py (`today` reproduces its resolved_4b | 3b_mass). Scenarios:
  today        jets pT > 30; 4 highest-b jets: 4 M, or 3 M + 1 L; window 30 GeV
  soft_jets    the same with jets pT > 20
  soft_loose   jets pT > 20; >= 3 M (4th any), or 4 L; window 30 GeV
  soft_wide    as soft_loose, window 40 GeV
Background is not modelled: looser selections also take more QCD (QCD_GLOB only sets the working points).
"""
import glob
import json
import os
import sys

import numpy as np

out, out_json, hh_glob, qcd_glob = sys.argv[1:5]
SCEN = {"today": (30, "tight", 30), "soft_jets": (20, "tight", 30), "soft_loose": (20, "loose", 30), "soft_wide": (20, "loose", 40)}


def load(pat):
    parts = [dict(np.load(f)) for f in sorted(glob.glob(pat))]
    ev = {k: np.concatenate([p[k] for p in parts]) for k in ("lumi", "event", "njet")}
    jets = {k: np.concatenate([p[k] for p in parts]) for k in parts[0] if k not in ev}
    return ev, jets


def good(j, ptmin):
    return (j["pt"] > ptmin) & (abs(j["eta"]) < 2.5) & (j["nconst"] > 1) & (j["nhf"] < 0.9) & (j["nemf"] < 0.9)


_, qj = load(qcd_glob)
light = good(qj, 30) & (qj["flav"] == 0)
wp = {name: float(np.quantile(qj["upart"][light], 1 - mis)) for name, mis in (("L", 0.1), ("M", 0.01))}
ev, jj = load(hh_glob)
pairings = [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]
resp = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "b_response.json")))
resp_pt = np.array([np.sqrt(lo * min(hi, 400.0)) for lo, hi, _, _ in resp])
resp_val = np.array([r for _, _, r, _ in resp])
b_corr = lambda pt: 1 / np.interp(np.log(pt), np.log(resp_pt), resp_val)


def p4(pt, eta, phi, m):
    px, py, pz = pt * np.cos(phi), pt * np.sin(phi), pt * np.sinh(eta)
    return np.array([np.sqrt(px**2 + py**2 + pz**2 + m**2), px, py, pz])


def mass(a, b):
    s = a + b
    return np.sqrt(max(s[0] ** 2 - s[1] ** 2 - s[2] ** 2 - s[3] ** 2, 0.0))


offs = np.concatenate([[0], np.cumsum(ev["njet"])])
flags = {k: np.zeros(len(ev["lumi"]), bool) for k in SCEN}
for i in range(len(ev["lumi"])):
    s = slice(offs[i], offs[i + 1])
    j = {k: v[s] for k, v in jj.items()}
    for ptmin in sorted({v[0] for v in SCEN.values()}):
        g = good(j, ptmin)
        if g.sum() < 4:
            continue
        b = j["upart"][g]
        top = np.argsort(-b)[:4]
        sel = {k: j[k][g][top] for k in ("pt", "eta", "phi", "mass")}
        c = b_corr(sel["pt"])
        v = [p4(sel["pt"][k] * c[k], sel["eta"][k], sel["phi"][k], sel["mass"][k] * c[k]) for k in range(4)]
        best = min(pairings, key=lambda pr: abs(mass(v[pr[0][0]], v[pr[0][1]]) - mass(v[pr[1][0]], v[pr[1][1]])))
        h = sorted([best[0], best[1]], key=lambda pr: -(v[pr[0]] + v[pr[1]])[1:3].dot((v[pr[0]] + v[pr[1]])[1:3]))
        dist = np.hypot(mass(v[h[0][0]], v[h[0][1]]) - 125, mass(v[h[1][0]], v[h[1][1]]) - 120)
        nm, nl = (b[top] > wp["M"]).sum(), (b[top] > wp["L"]).sum()
        for name, (pmin, tags, win) in SCEN.items():
            if pmin != ptmin:
                continue
            tag_ok = ((nm == 4) | ((nm == 3) & (nl == 4))) if tags == "tight" else ((nm >= 3) | (nl == 4))
            flags[name][i] = tag_ok & (dist < win)
frac = {k: float(v.mean()) for k, v in flags.items()}
print("selected fraction of HH4b events:", frac)
np.savez(out, lumi=ev["lumi"], event=ev["event"], **flags)
json.dump({"wp_upart": wp, "selected_fraction": frac, "scenarios": SCEN}, open(out_json, "w"), indent=1)

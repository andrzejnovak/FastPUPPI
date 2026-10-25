#!/usr/bin/env python3
"""Analysis-level HH->4b selection on offline PUPPI jets (dump_offline.py), for the L1 efficiency study.

    python3 offline_sel.py OUT.npz OUT.json "HH4B_GLOB" "QCD_GLOB"
Jets: pT > 30, |eta| < 2.5, loose ID (>1 constituent, neutral hadron and neutral EM fractions < 0.9).
b tagging: UParT B-vs-all; working points at 10% / 1% / 0.1% light-jet mistag (L, M, T), set on QCD jets
(hadron flavour 0, pT > 30).
Selections (per event, flags saved with lumi, event):
  resolved_4b : >= 4 jets; the 4 with the highest b score all pass M; their momenta corrected for the b-jet response
                (stand-in for b-jet energy regression: median offline / generator pT of true b jets vs pT, measured in
                these HH4b events, b_response.json); pairing into two Higgs candidates with the smallest |m1 - m2|;
                signal region sqrt((m1 - 125)^2 + (m2 - 120)^2) < 30 GeV (leading-pT pair first).
  resolved_4b_noreg : the same without the b-response correction (Higgs candidates peak near 100-110 GeV).
  4b_nomass   : same without the mass window.
  3b_mass     : 3 of the 4 pass M, the 4th passes L, with the (corrected) mass window.
  4j          : >= 4 jets only (loosest).
"""
import glob
import json
import os
import sys

import numpy as np

out, out_json, hh_glob, qcd_glob = sys.argv[1:5]


def load(pat):
    parts = [dict(np.load(f)) for f in sorted(glob.glob(pat))]
    ev = {k: np.concatenate([p[k] for p in parts]) for k in ("lumi", "event", "njet")}
    jets = {k: np.concatenate([p[k] for p in parts]) for k in parts[0] if k not in ev}
    return ev, jets


def good(j):
    return (j["pt"] > 30) & (abs(j["eta"]) < 2.5) & (j["nconst"] > 1) & (j["nhf"] < 0.9) & (j["nemf"] < 0.9)


_, qj = load(qcd_glob)
light = good(qj) & (qj["flav"] == 0)
wp = {name: float(np.quantile(qj["upart"][light], 1 - mis)) for name, mis in (("L", 0.1), ("M", 0.01), ("T", 0.001))}
ev, jj = load(hh_glob)
bjet = good(jj) & (jj["flav"] == 5)
eff_b = {name: float((jj["upart"][bjet] > c).mean()) for name, c in wp.items()}
print("UParT working points (light mistag 10/1/0.1%):", wp, "b efficiency in HH4b:", eff_b)

pairings = [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]
resp = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "b_response.json")))
resp_pt = np.array([np.sqrt(lo * min(hi, 400.0)) for lo, hi, _, _ in resp])
resp_val = np.array([r for _, _, r, _ in resp])


def b_corr(pt):
    """1 / (b-jet response) at this offline pT, interpolated in log pT."""
    return 1 / np.interp(np.log(pt), np.log(resp_pt), resp_val)


def p4(pt, eta, phi, m):
    px, py, pz = pt * np.cos(phi), pt * np.sin(phi), pt * np.sinh(eta)
    return np.array([np.sqrt(px**2 + py**2 + pz**2 + m**2), px, py, pz])


def mass(a, b):
    s = a + b
    return np.sqrt(max(s[0] ** 2 - s[1] ** 2 - s[2] ** 2 - s[3] ** 2, 0.0))


offs = np.concatenate([[0], np.cumsum(ev["njet"])])
flags = {k: np.zeros(len(ev["lumi"]), bool) for k in ("resolved_4b", "resolved_4b_noreg", "4b_nomass", "3b_mass", "4j")}
mh1, mh2 = np.zeros(len(ev["lumi"])), np.zeros(len(ev["lumi"]))
for i in range(len(ev["lumi"])):
    s = slice(offs[i], offs[i + 1])
    g = good({k: v[s] for k, v in jj.items()})
    if g.sum() < 4:
        continue
    flags["4j"][i] = True
    b = jj["upart"][s][g]
    top = np.argsort(-b)[:4]
    sel = {k: jj[k][s][g][top] for k in ("pt", "eta", "phi", "mass")}
    windows = {}
    for corr in (False, True):
        c = b_corr(sel["pt"]) if corr else np.ones(4)
        v = [p4(sel["pt"][k] * c[k], sel["eta"][k], sel["phi"][k], sel["mass"][k] * c[k]) for k in range(4)]
        best = min(pairings, key=lambda pr: abs(mass(v[pr[0][0]], v[pr[0][1]]) - mass(v[pr[1][0]], v[pr[1][1]])))
        h = sorted([best[0], best[1]], key=lambda pr: -(v[pr[0]] + v[pr[1]])[1:3].dot((v[pr[0]] + v[pr[1]])[1:3]))
        m1, m2 = mass(v[h[0][0]], v[h[0][1]]), mass(v[h[1][0]], v[h[1][1]])
        windows[corr] = np.hypot(m1 - 125, m2 - 120) < 30
        if corr:
            mh1[i], mh2[i] = m1, m2
    window = windows[True]
    nm = (b[top] > wp["M"]).sum()
    flags["4b_nomass"][i] = nm == 4
    flags["resolved_4b"][i] = (nm == 4) & window
    flags["resolved_4b_noreg"][i] = (nm == 4) & windows[False]
    flags["3b_mass"][i] = (nm == 3) & (b[top].min() > wp["L"]) & window
frac = {k: float(v.mean()) for k, v in flags.items()}
print("selected fraction of HH4b events:", frac)
np.savez(out, lumi=ev["lumi"], event=ev["event"], mh1=mh1, mh2=mh2, **flags)
json.dump({"wp_upart": wp, "eff_b": eff_b, "selected_fraction": frac, "n_events": int(len(ev["lumi"]))},
          open(out_json, "w"), indent=1)

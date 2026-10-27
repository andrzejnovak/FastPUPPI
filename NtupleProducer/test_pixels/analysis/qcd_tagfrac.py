#!/usr/bin/env python3
"""Offline 4b / 3b tag fractions of QCD multijet events, for the triggered-stream background of scouting.py.

    python3 qcd_tagfrac.py OUT.json
QCDFlat offline jets (MINIAOD slimmedJetsPuppi, UParT; offline/dump_offline.py), events with >= 4 jets pT > 25,
|eta| < 2.5 and HT 150-800 (unweighted: the fraction varies slowly with HT). The 4 leading jets: measured P(3 tags)
at the UParT medium working point, and truth-tagged P(4) / P(3) with the per-jet probabilities scouting.py uses
(b 0.84, c 0.12, light 0.01); the measured per-jet efficiencies and P(3) check them (no 4-tag event is observed).
"""
import glob
import json
import sys

import numpy as np

WP = json.load(open("offline_sel2.json"))["wp_upart"]["M"]
P = {5: 0.84, 4: 0.12, 0: 0.01}
rows = []
for f in sorted(glob.glob("/scratch/submit/cms/novaka/l1pixels/offline/QCDFlat_*.npz")):
    d = np.load(f)
    off = np.concatenate([[0], np.cumsum(d["njet"])])
    for i in range(len(d["njet"])):
        s = slice(off[i], off[i + 1])
        pt, eta, u, fl = d["pt"][s], d["eta"][s], d["upart"][s], d["flav"][s]
        m = (pt > 25) & (abs(eta) < 2.5)
        ht = pt[(pt > 30) & (abs(eta) < 2.5)].sum()
        if m.sum() < 4 or not 150 < ht < 800:
            continue
        o = np.argsort(-pt[m])[:4]
        fl4, t = fl[m][o], u[m][o] > WP
        p = np.array([P[int(x)] if x in (4, 5) else P[0] for x in fl4])
        p3 = sum(np.prod(np.where(np.arange(4) == k, 1 - p, p)) for k in range(4))
        cnt = []
        for c in (fl4 == 5, fl4 == 4, (fl4 != 4) & (fl4 != 5)):
            cnt += [(t & c).sum(), c.sum()]
        rows.append([p.prod(), p3, t.sum() == 3, t.sum() == 4] + cnt)
r = np.array(rows, float)
out = {"n_events": len(r), "truth_P4": r[:, 0].mean(), "truth_P3": r[:, 1].mean(), "measured_P3": r[:, 2].mean(),
       "measured_P3_n": int(r[:, 2].sum()), "measured_P4_n": int(r[:, 3].sum()),
       "per_jet_eff": {"b": r[:, 4].sum() / r[:, 5].sum(), "c": r[:, 6].sum() / r[:, 7].sum(), "light": r[:, 8].sum() / r[:, 9].sum()}}
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out, indent=1))

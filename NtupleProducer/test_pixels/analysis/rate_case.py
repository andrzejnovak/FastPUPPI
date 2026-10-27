#!/usr/bin/env python3
"""The rate case: an HH->4b seed with an L1 b tag against the menu's untagged HT seeds, at equal rate or equal
efficiency (page tab "Rate").

    pixi run python rate_case.py OUT.json
Inputs: seed_plane.npz (HT and 4-leading-jet score sums for HH->4b and minimum bias, as seed_plane.py),
curves_flags.npz (menu flag, offline 4b + 3b selection), perfect_ceiling.json (flavour-aware perfect seed).
Standalone seeds (no menu): HT only; HT + NN sum; HT + pixel sum. Cuts chosen on even events (HH and minimum bias),
quoted on odd ones; minimum-bias weight BX_KHZ / MB_TOTAL (HT >= 150, where the re-simulated sample is complete).
"""
import json
import os
import sys

import numpy as np

os.environ.setdefault("MB_TOTAL", "1999360")
os.environ.setdefault("HT_MIN", "150")
import direct_rate as D  # noqa: E402

RATES = (2.0, 3.0, 5.0, 7.5, 10.0, 14.0, 20.0, 30.0, 40.0)
sp = dict(np.load("seed_plane.npz"))
fl = dict(np.load("curves_flags.npz"))
pos = {(l, e): i for i, (l, e) in enumerate(zip(fl["lumi"], fl["event"]))}
ix = np.array([pos[(l, e)] for l, e in zip(sp["hh_lumi"], sp["hh_event"])])
off = fl["offline_4b3b"][ix].astype(bool)
ev_h, ev_m = sp["hh_event"] % 2 == 0, sp["mb_event"] % 2 == 0
w_fold = len(sp["mb_ht"]) / D.MB_TOTAL * D.BX_KHZ / ev_m.sum()
allh = np.ones(len(sp["hh_ht"]), bool)
eff = lambda p, den: float((p & den & ~ev_h).sum() / (den & ~ev_h).sum())
res = {"menu": {"rate_khz": float(sp["mb_menu"][~ev_m].sum() * w_fold), "eff_all": eff(sp["hh_menu"].astype(bool), allh),
                "eff_offline": eff(sp["hh_menu"].astype(bool), off)}, "standalone": {}}
print("menu HT seeds:", res["menu"], flush=True)
tags = {"HT only": (np.zeros(len(sp["hh_ht"])), np.zeros(len(sp["mb_ht"]))), "NN": (sp["hh_nn"], sp["mb_nn"]),
        "pixel": (sp["hh_l1"], sp["mb_l1"])}
def best_ht(r):
    """HT-only seed: the lowest HT cut (10 GeV steps) whose rate on even minimum bias stays within r."""
    for h in np.arange(150, 1500, 10):
        if (sp["mb_ht"][ev_m] > h).sum() * w_fold <= r:
            return h
    return 1500.0


for name, (s_h, s_m) in tags.items():
    rows = []
    for r in RATES:
        if name == "HT only":
            h, s = best_ht(r), -1.0
        else:
            _, h, s = D.best(s_h[ev_h], sp["hh_ht"][ev_h], allh[ev_h], s_m[ev_m], sp["mb_ht"][ev_m], np.full(ev_m.sum(), w_fold), r)
        p_h, p_m = (sp["hh_ht"] > h) & (s_h > s), (sp["mb_ht"] > h) & (s_m > s)
        rows.append({"target_khz": r, "ht_cut": float(h), "score_cut": float(s), "rate_khz": float(p_m[~ev_m].sum() * w_fold),
                     "eff_all": eff(p_h, allh), "eff_offline": eff(p_h, off)})
        print(f"{name:8s} {r:5.1f} kHz: HT > {h:.0f}, sum > {s:.2f}  rate {rows[-1]['rate_khz']:.1f}  "
              f"eff all {rows[-1]['eff_all']:.3f} offline {rows[-1]['eff_offline']:.3f}", flush=True)
    res["standalone"][name] = rows
# rate needed to match the menu's efficiency, and efficiency at the menu's rate (log-linear interpolation)
for name, rows in list(res["standalone"].items()):
    rate, e = np.array([r["rate_khz"] for r in rows]), np.array([r["eff_all"] for r in rows])
    o = np.argsort(rate)
    res["standalone"][name + "_at_menu_rate"] = float(np.interp(np.log(res["menu"]["rate_khz"]), np.log(rate[o]), e[o]))
    o = np.argsort(e)
    res["standalone"][name + "_rate_for_menu_eff"] = float(np.exp(np.interp(res["menu"]["eff_all"], e[o], np.log(rate[o]))))
    print(f"{name}: at the menu rate {res['standalone'][name + '_at_menu_rate']:.3f}; rate for the menu efficiency "
          f"{res['standalone'][name + '_rate_for_menu_eff']:.1f} kHz", flush=True)
pc = json.load(open("perfect_ceiling.json"))
res["standalone"]["perfect"] = [{"target_khz": r["target_khz"], "ht_cut": r["ht_cut"], "n_b_min": r["n_b_min"], "rate_khz": r["rate_khz"],
                                 "eff_all": r["eff"]["all"], "eff_offline": r["eff"]["offline_4b3b"]} for r in pc["standalone"]]
json.dump(res, open(sys.argv[1], "w"), indent=1)
print("wrote", sys.argv[1])

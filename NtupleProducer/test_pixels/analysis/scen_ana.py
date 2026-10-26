#!/usr/bin/env python3
"""L1 efficiency and delivered kappa_lambda information for each offline scenario (offline_scenarios.npz).

    python3 scen_ana.py OUT.json
Odd HH->4b events, seeds at +2.5 kHz on top of the menu (curves_flags.npz, ht_control_flags.npz). kappa_lambda
information per event: (d ln s_i / d kl)^2 at kl = 1 of its generator m_HH bin, as make_page_plots.py section 9.
"""
import glob
import json
import re
import sys

import numpy as np

fl = dict(np.load("curves_flags.npz")); odd = fl["odd"]
g = {k: np.concatenate([np.load(f)[k] for f in sorted(glob.glob("/scratch/submit/cms/novaka/l1pixels/genmhh/mhh_*.npz"))]) for k in ("lumi", "event", "mhh")}
pos = {(l, e): i for i, (l, e) in enumerate(zip(g["lumi"], g["event"]))}
mhh = np.array([g["mhh"][pos[(l, e)]] for l, e in zip(fl["lumi"], fl["event"])])
nano = {}
for f in sorted(glob.glob("klreweight/nano_mhh_kl*.npz")):
    m = np.load(f)["mhh"]; nano[float(re.search(r"kl(\d+p\d+)", f).group(1).replace("p", "."))] = m[m > 0]
bins = np.concatenate([np.arange(240, 600, 20), np.arange(600, 800, 50), [800, 1000, 1300, 5000]])
dens = {kl: np.histogram(m, bins)[0] / len(m) for kl, m in nano.items()}
ib = np.clip(np.digitize(mhh, bins) - 1, 0, len(bins) - 2)
XS = lambda k: (70.38 - 51.85 * k + 11.42 * k ** 2) / (70.38 - 51.85 + 11.42)
ks = np.array([0.0, 1.0, 2.45]); S3 = np.array([XS(k) * dens[k] for k in ks])
cf = np.array([np.polyfit(ks, S3[:, i], 2) for i in range(S3.shape[1])])
w = ((2 * cf[:, 0] + cf[:, 1]) / np.maximum(S3[1], 1e-12))[ib] ** 2
ctl = dict(np.load("ht_control_flags.npz")); cp = {(l, e): i for i, (l, e) in enumerate(zip(ctl["lumi"], ctl["event"]))}
T = {"Run-3-style": fl["menu"], "lower HT": ctl["HTlow|menu|2.5"][[cp[(l, e)] for l, e in zip(fl["lumi"], fl["event"])]],
     "NN": fl["NN|menu|2.5"], "pixel": fl["L1 pixel|menu|2.5"], "HLT pixel": fl["HLT pixel|menu|2.5"], "perfect": fl["perfect|menu|2.5"]}
sc = np.load("offline_scenarios.npz"); sp = {(l, e): i for i, (l, e) in enumerate(zip(sc["lumi"], sc["event"]))}
si = np.array([sp[(l, e)] for l, e in zip(fl["lumi"], fl["event"])])
check = (sc["today"][si] == fl["offline_4b3b"]).mean()
res = {"agreement_today_vs_offline_4b3b": float(check), "scenarios": {}}
ref = (w * (odd & sc["today"][si] & T["NN"])).sum()
for name in ("today", "soft_jets", "soft_loose", "soft_wide"):
    sel = odd & sc[name][si]
    r = {"selected_frac": float(sc[name][si][odd].mean()), "n_odd": int(sel.sum()), "n_odd_lt400": int((sel & (mhh < 400)).sum()),
         "eff": {}, "eff_lt400": {}, "eff_klw": {}, "info_rel_today_NN": {}}
    for k, v in T.items():
        r["eff"][k] = float(v[sel].mean())
        r["eff_lt400"][k] = float(v[sel & (mhh < 400)].mean())
        r["eff_klw"][k] = float((w * v)[sel].sum() / w[sel].sum())
        r["info_rel_today_NN"][k] = float((w * (sel & v)).sum() / ref)
    r["info_offline_only_rel"] = float((w * sel).sum() / ref)  # with a perfect trigger
    res["scenarios"][name] = r
    print(f"{name:10s} sel {100*r['selected_frac']:4.1f}% (odd n={r['n_odd']}, <400: {r['n_odd_lt400']})  "
          + "  ".join(f"{k} {100*r['eff_klw'][k]:4.1f}" for k in T) + "  | kl info vs today+NN: "
          + "  ".join(f"{k} {r['info_rel_today_NN'][k]:.2f}" for k in ("Run-3-style", "NN", "pixel", "perfect"))
          + f"  (no trigger loss {r['info_offline_only_rel']:.2f})")
print("today flags agree with offline_4b3b:", check)
json.dump(res, open(sys.argv[1], "w"), indent=1)

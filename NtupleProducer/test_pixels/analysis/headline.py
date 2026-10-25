#!/usr/bin/env python3
"""Headline: what a better L1 b-tag is worth for HH->4b, as equivalent HL-LHC luminosity at fixed L1 rate.

    python3 headline.py seed_flags_14kHz.npz "klreweight/nano_mhh_kl*.npz" OUT.json

For each kappa_lambda (Phase-2 SM sample reweighted in gen m_HH), the seed efficiency in the generator fiducial proxy for
HT only, today's L1 NN, a realistic pixel tagger (proxy: eps_b 0.5 at 3% fakes, matching the minimum-bias measurement),
and the ideal tagger (eps_b 0.7 at 1%). Equivalent luminosity relative to today's NN:
  conservative  L_eq = eff / eff_NN        (background in the offline 4b region gains like the signal: Z^2 ~ L * eff)
  optimistic    L_eq = (eff / eff_NN)^2    (background unchanged)
Uncertainties: binomial / effective-count on the efficiencies only (not the rate or the reweighting).
"""
import glob
import json
import re
import sys

import numpy as np

d = np.load(sys.argv[1])
out = sys.argv[3]
bins = np.concatenate([np.arange(240, 600, 20), np.arange(600, 800, 50), [800, 1000, 1300, 5000]])
nano = {}
for f in sorted(glob.glob(sys.argv[2])):
    kl = float(re.search(r"kl(\d+p\d+)", f).group(1).replace("p", "."))
    m = np.load(f)["mhh"]
    nano[kl] = np.histogram(m[m > 0], bins)[0] / (m > 0).sum()
m, acc = d["mhh"], d["acc"]
ib = np.clip(np.digitize(m, bins) - 1, 0, len(bins) - 2)
seeds = {"HT only": d["ht_only"], "L1 NN (today)": d["nn"], "pixel tagger (realistic proxy)": d["param_eb0.5_em0.03"],
         "ideal tagger (eps_b 0.7, 1%)": d["param_eb0.7_em0.01"]}
res = {}
for kl in sorted(nano):
    r = np.where(nano[1.0] > 0, nano[kl] / np.maximum(nano[1.0], 1e-12), 0.0)
    w = np.where(m > 0, r[ib], 0.0) if kl != 1.0 else (m > 0).astype(float)
    w = w * acc
    neff = w.sum() ** 2 / (w ** 2).sum()
    row = {}
    for name, p in seeds.items():
        e = float((w * p).sum() / w.sum())
        row[name] = {"eff": e, "err": float(np.sqrt(e * (1 - e) / neff))}
    base = row["L1 NN (today)"]["eff"]
    for name in row:
        row[name]["Leq_conservative"] = row[name]["eff"] / base
        row[name]["Leq_optimistic"] = (row[name]["eff"] / base) ** 2
    res[kl] = row
    print(f"kl={kl:4.2f}  " + "  ".join(f"{n}: {v['eff']:.3f}±{v['err']:.3f} (x{v['Leq_conservative']:.2f}/x{v['Leq_optimistic']:.2f})"
                                       for n, v in row.items()), flush=True)
json.dump(res, open(out, "w"), indent=1)

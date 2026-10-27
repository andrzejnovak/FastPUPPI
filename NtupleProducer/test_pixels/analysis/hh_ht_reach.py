#!/usr/bin/env python3
"""How much HH->4b signal sits below the L1 HT reach of the scouting study (HT > 150), per kappa_lambda.

    python3 hh_ht_reach.py OUT.json HH4B_GLOB GENMHH_GLOB KL_GLOB
Events with >= 4 L1 jets (pT > 20, |eta| < 2.4) in the Higgs-candidate window of scouting.py, weighted to
kappa_lambda = 1, 2.45, 5 (shape x sigma); fraction and yield (3000/fb, before tags) per L1 HT bin.
"""
import glob
import json
import re
import sys

import numpy as np

import scouting as S

out, hh_pat, gen_glob, kl_glob = sys.argv[1:5]
hh = S.read(hh_pat)
S.kinematics(hh)
g = {k: np.concatenate([np.load(f)[k] for f in sorted(glob.glob(gen_glob))]) for k in ("lumi", "event", "mhh")}
gpos = {(l, e): i for i, (l, e) in enumerate(zip(g["lumi"], g["event"]))}
mhh = np.array([g["mhh"][gpos[(l, e)]] for l, e in zip(hh["lumi"], hh["event"])])
nano = {float(re.search(r"kl(\d+p\d+)", f).group(1).replace("p", ".")): np.load(f)["mhh"] for f in sorted(glob.glob(kl_glob))}
gb = np.concatenate([np.arange(240, 600, 20), np.arange(600, 800, 50), [800, 1000, 1300, 5000]])
dens = {kl: np.histogram(m[m > 0], gb)[0] / (m > 0).sum() for kl, m in nano.items()}
ib = np.clip(np.digitize(mhh, gb) - 1, 0, len(gb) - 2)
c = json.load(open("scouting.json"))["setup"]["window"]
win = hh["n4"] & (np.hypot((hh["m1"] - c[0]) / c[1], (hh["m2"] - c[2]) / c[3]) < 1.6)
edges = [0, 100, 125, 150, 170, 200, 250, 300, 400, 1e9]
res = {"ht_edges": edges}
for kl in (1.0, 2.45, 5.0):
    w = S.SIG_SM / len(mhh) * S.XS(kl) * np.where(dens[1.0] > 0, dens[kl] / np.maximum(dens[1.0], 1e-12), 0.0)[ib]
    h = np.histogram(hh["ht"][win], edges, weights=w[win])[0]
    res[str(kl)] = {"yield_per_ht_bin": h.tolist(), "frac_below_150": float(h[:3].sum() / h.sum()),
                    "frac_below_170": float(h[:4].sum() / h.sum()), "window_yield": float(h.sum())}
    print(f"kl={kl:4.2f}: window yield {h.sum():8.0f}  below HT 150: {h[:3].sum() / h.sum():.3f}  below 170: {h[:4].sum() / h.sum():.3f}  "
          f"per bin {np.round(h / h.sum(), 3).tolist()}", flush=True)
json.dump(res, open(out, "w"), indent=1)

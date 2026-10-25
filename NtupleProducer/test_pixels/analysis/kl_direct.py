#!/usr/bin/env python3
"""kappa_lambda split of the direct rate test: fiducial HH->4b efficiency of each seed, reweighted with gen m_HH.

    python3 kl_direct.py direct_rate_flags.npz "GENMHH_GLOB" "klreweight/nano_mhh_kl*.npz" OUT.json
Odd events only (thresholds were chosen on even ones). Denominator: generator fiducial events (4 b jets with
pT > 30, |eta| < 2.4), or with SEL="sel.npz:flag" the events passing an offline selection (offline_sel.py). Weights as in kl_reweight.py. The error on the pixel - NN
difference is paired: only events where the two seeds disagree contribute.
"""
import glob
import json
import os
import re
import sys

import numpy as np

fl, gen_glob, kl_glob, out = sys.argv[1:5]
d = dict(np.load(fl))
g = {k: np.concatenate([np.load(f)[k] for f in sorted(glob.glob(gen_glob))]) for k in ("lumi", "event", "mhh")}
pos = {(l, e): i for i, (l, e) in enumerate(zip(g["lumi"], g["event"]))}
mhh = np.array([g["mhh"][pos[(l, e)]] for l, e in zip(d["lumi"], d["event"])])

nano = {}
for f in sorted(glob.glob(kl_glob)):
    m = np.load(f)["mhh"]
    nano[float(re.search(r"kl(\d+p\d+)", f).group(1).replace("p", "."))] = m[m > 0]
bins = np.concatenate([np.arange(240, 600, 20), np.arange(600, 800, 50), [800, 1000, 1300, 5000]])
dens = {kl: np.histogram(m, bins)[0] / len(m) for kl, m in nano.items()}
ib = np.clip(np.digitize(mhh, bins) - 1, 0, len(bins) - 2)

sel = d["odd"] & d["fid"]
if os.environ.get("SEL"):
    path, flag = os.environ["SEL"].split(":")
    o = np.load(path)
    opos = {(l, e): i for i, (l, e) in enumerate(zip(o["lumi"], o["event"]))}
    oi = np.array([opos.get((l, e), -1) for l, e in zip(d["lumi"], d["event"])])
    print(f"offline selection {flag}: {(oi >= 0).mean():.3f} of events found, {o[flag][oi[oi >= 0]].mean():.3f} pass")
    sel = d["odd"] & (oi >= 0) & np.where(oi >= 0, o[flag][np.maximum(oi, 0)], False)
res = {}
pairs = [(f"{t}_menu_{r}", f"NN_menu_{r}") for r in ("2.5", "5", "10") for t in ("pixel", "pixel>2")]
pairs += [(f"{t}_alone_{r}", f"NN_alone_{r}") for r in ("5", "10", "14", "20") for t in ("pixel", "pixel>2")]
for kl in sorted(nano):
    w = np.ones(len(mhh)) if kl == 1.0 else np.where(dens[1.0] > 0, dens[kl] / np.maximum(dens[1.0], 1e-12), 0.0)[ib]
    w = w * sel
    eff = lambda k: float((w * d[k]).sum() / w.sum())
    row = {"menu": eff("menu")}
    for a, b in pairs:
        ea, eb = eff(a), eff(b)
        disc = w * (d[a] != d[b])
        err = float(np.sqrt((w * disc).sum()) / w.sum())  # paired (McNemar-like) error on ea - eb
        row[a] = {"eff": ea, "eff_NN": eb, "diff": ea - eb, "diff_err": err, "lumi_ratio": [ea / eb, (ea / eb) ** 2]}
    res[kl] = row
    print(f"kl={kl:4.2f}  menu alone {row['menu']:.3f}")
    for a, _ in pairs:
        r = row[a]
        print(f"   {a:18s} {r['eff']:.3f} vs NN {r['eff_NN']:.3f}  diff {r['diff']:+.3f} +- {r['diff_err']:.3f}  "
              f"equiv lumi x{r['lumi_ratio'][0]:.2f}-{r['lumi_ratio'][1]:.2f}")
json.dump(res, open(out, "w"), indent=1)

#!/usr/bin/env python3
"""Planned-menu seed rates from the stored 14_0 L1 SC4 jets of ALL minimum-bias events (mbjscan, leading 8 jets with
pT > 15, |eta| < 5), with the same step1_2024 online thresholds as vbf_menu.py. Compares with our 17_0 re-emulation
(vbf_ctag.py "base") and the L1 TDR table.

    python3 rate_check.py OUT.json
"""
import glob
import json
import sys

import numpy as np

ETA_EDGES = np.array([0, 1.5, 2.4, 3.0, 99])
THR = {160: (105.5, 94.3, 92.1, 124.7), 35: (25.0, 25.0, 25.0, 30.8), 230: (157.0, 138.3, 149.5, 177.4),
       112: (70.2, 64.1, 52.8, 88.6)}
QUAD_BARREL, QUAD_ENDCAP, HT_QUAD, HT_ALONE = (41.1, 29.4, 25.0, 25.0), (32.7, 25.0, 25.0, 25.0), 316.3, 361.0
BX_KHZ = 2760 * 11.245


def thr(pt_off, eta):
    return np.asarray(THR[pt_off])[np.clip(np.digitize(np.abs(eta), ETA_EDGES) - 1, 0, 3)]


def flags(pt, eta, phi, ht):
    pt = np.where(np.isfinite(pt), pt, 0.0)
    n = len(pt)
    cen = np.abs(eta) < 2.4
    single = np.any(cen & (pt > thr(230, eta)), axis=1)
    p112 = cen & (pt > thr(112, eta))
    double = np.zeros(n, bool)
    vbf = np.zeros(n, bool)
    nj = pt.shape[1]
    for i in range(nj):
        for j in range(nj):
            if i == j:
                continue
            if i < j:
                double |= p112[:, i] & p112[:, j] & (np.abs(eta[:, i] - eta[:, j]) < 1.6)
            ok = (pt[:, i] > thr(160, eta[:, i])) & (pt[:, j] > thr(35, eta[:, j])) & (pt[:, j] > 0)
            m2 = 2 * pt[:, i] * pt[:, j] * (np.cosh(eta[:, i] - eta[:, j]) - np.cos(phi[:, i] - phi[:, j]))
            vbf |= ok & (m2 > 620.0 ** 2)
    # quad jet on the central jets ordered by pT (stored jets are pT ordered)
    cpt = np.where(cen, pt, 0.0)
    order = np.argsort(-cpt, axis=1)
    cs = np.take_along_axis(cpt, order, 1)
    ce = np.take_along_axis(eta, order, 1)
    quad = np.ones(n, bool)
    for k in range(4):
        quad &= cs[:, k] > np.where(np.abs(ce[:, k]) < 1.5, QUAD_BARREL[k], QUAD_ENDCAP[k])
    htseed = (quad & (ht > HT_QUAD)) | (ht > HT_ALONE)
    return {"VBF": vbf, "SingleJet": single, "DoubleJet": double, "HT": htseed, "HT450": ht > HT_ALONE,
            "HT400_Quad": quad & (ht > HT_QUAD)}


parts = [np.load(f) for f in sorted(glob.glob("/scratch/submit/cms/novaka/l1pixels/mbjscan/scan_*.npz"))]
pt, eta, phi, ht = (np.concatenate([p[k] for p in parts]).astype(np.float64) for k in ("pt", "eta", "phi", "ht"))
n = len(pt)
f = flags(pt, eta, phi, ht)
f["any"] = f["VBF"] | f["SingleJet"] | f["DoubleJet"] | f["HT"]
out = {"n_events": n, "rate_khz": {k: float(v.mean() * BX_KHZ) for k, v in f.items()},
       "n_pass": {k: int(v.sum()) for k, v in f.items()}}
# DoubleJet threshold scan: rate vs offline-equivalent threshold, scaling the 112 thresholds linearly
scan = {}
for t in (100, 112, 125, 140, 150):
    s = np.asarray(THR[112]) * 0  # placeholder for clarity
    THR[t] = tuple(np.asarray((70.2, 64.1, 52.8, 88.6)) * t / 112.0)
    cen = np.abs(eta) < 2.4
    p = cen & (pt > thr(t, eta))
    d = np.zeros(n, bool)
    for i in range(8):
        for j in range(i + 1, 8):
            d |= p[:, i] & p[:, j] & (np.abs(eta[:, i] - eta[:, j]) < 1.6)
    scan[t] = float(d.mean() * BX_KHZ)
out["doublejet_scan_khz"] = scan
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out, indent=1))

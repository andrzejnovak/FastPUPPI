#!/usr/bin/env python3
"""Learn the Inner Tracker module planes and chip layout from hits on HLT pixel tracks (detId + global position).

    python3 chip_geom.py OUT.npz OUT_val.json "train_glob" "validation_glob" [MAXFILES]
Pass 1: per detId, hit centroid and covariance -> plane normal (smallest PCA axis).
Pass 2: per detId, min / max of the hits along the two in-plane axes (chipgeo.inplane_axes) and the plane residual;
the module centre is the midpoint of the extents, the long axis the longer extent; >25 mm -> 2 chips on that axis.
Per chip: acceptance of the cluster tables (fraction of the chip area at |eta| < 2.5 seen from the origin).
Validation (other files): assign each hit to a module from its position alone and compare with its detId.
"""
import glob
import json
import sys

import awkward as ak
import numpy as np
import uproot

import chipgeo as CG

out, out_val, train_glob, val_glob = sys.argv[1:5]
maxfiles = int(sys.argv[5]) if len(sys.argv) > 5 else 40
train = sorted(glob.glob(train_glob))[:maxfiles]
val = sorted(glob.glob(val_glob))[:2]
BR = ["PixelHits_detId", "PixelHits_x", "PixelHits_y", "PixelHits_z", "PixelHits_subdet", "PixelHits_layer"]


def chunks(files):
    for f in files:
        for a in uproot.iterate(f + ":Events", filter_name=BR, step_size=300):
            det = ak.to_numpy(ak.flatten(a.PixelHits_detId)).astype(np.int64)
            p = np.stack([ak.to_numpy(ak.flatten(a[f"PixelHits_{c}"])).astype(float) for c in "xyz"], 1)
            ok = (det > 0) & (abs(p[:, 0]) < 900)
            yield det[ok], p[ok], ak.to_numpy(ak.flatten(a.PixelHits_subdet))[ok], ak.to_numpy(ak.flatten(a.PixelHits_layer))[ok]


# pass 1: module list, centroid, covariance
ids = np.zeros(0, np.int64)
acc = {}
for det, p, sub, lay in chunks(train):
    u, inv = np.unique(det, return_inverse=True)
    s = np.zeros((len(u), 10))
    np.add.at(s, inv, np.column_stack([np.ones(len(p)), p, p[:, [0]] * p, p[:, [1]] * p[:, 1:], p[:, [2]] ** 2]))
    for i, d in enumerate(u):
        acc[d] = acc.get(d, 0) + s[i]
ids = np.array(sorted(acc))
S = np.array([acc[d] for d in ids])
nh = S[:, 0]
c = S[:, 1:4] / nh[:, None]
xx, xy, xz, yy, yz, zz = (S[:, i] / nh for i in range(4, 10))
cov = np.stack([np.stack([xx, xy, xz], 1), np.stack([xy, yy, yz], 1), np.stack([xz, yz, zz], 1)], 1) - c[:, :, None] * c[:, None, :]
w_, v_ = np.linalg.eigh(cov)
normal = v_[:, :, 0]
sub, lay = CG.decode(ids)
barrel = sub == 1
a1, a2 = CG.inplane_axes(c, normal, barrel)
print(f"pass 1: {len(ids)} modules, {nh.sum():.3g} hits")

# pass 2: extents along a1, a2 and plane residuals
lo = np.full((len(ids), 2), np.inf)
hi = np.full((len(ids), 2), -np.inf)
wsq = np.zeros(len(ids))
for det, p, _, _ in chunks(train):
    m = np.searchsorted(ids, det)
    d = p - c[m]
    q = np.stack([(d * a1[m]).sum(1), (d * a2[m]).sum(1)], 1)
    np.minimum.at(lo, m, q)
    np.maximum.at(hi, m, q)
    np.add.at(wsq, m, (d * normal[m]).sum(1) ** 2)
ext = hi - lo
mid = (hi + lo) / 2
cen = c + mid[:, [0]] * a1 + mid[:, [1]] * a2
long_is_1 = ext[:, 0] >= ext[:, 1]
e_long = np.where(long_is_1[:, None], a1, a2)
e_short = np.where(long_is_1[:, None], a2, a1)
L_long = np.where(long_is_1, ext[:, 0], ext[:, 1])
L_short = np.where(long_is_1, ext[:, 1], ext[:, 0])
n_long = np.where(L_long > CG.TWO_CHIP, 2, 1)
n_short = np.where(L_short > CG.TWO_CHIP, 2, 1)
lid = CG.lid_of(sub, lay, cen[:, 2])
geo = dict(detid=ids, subdet=sub, layer=lay, lid=lid, nhits=nh, c=cen, n=normal, e_long=e_long, e_short=e_short,
           L_long=L_long, L_short=L_short, n_long=n_long, n_short=n_short, w_rms=np.sqrt(wsq / nh))

# chip acceptance of the cluster tables: fraction of each chip's area at |eta| < 2.5
g = np.linspace(0.05, 0.95, 10)
accept = np.zeros((len(ids), 4))
tmp = CG.Geometry.__new__(CG.Geometry)
tmp.__dict__.update(geo)
rect = tmp.chip_rects(np.arange(len(ids)))
for ci in range(4):
    alo, ahi, blo, bhi = (rect[:, ci, j] for j in range(4))
    A = alo[:, None, None] + (ahi - alo)[:, None, None] * g[None, :, None]
    B = blo[:, None, None] + (bhi - blo)[:, None, None] * g[None, None, :]
    P = cen[:, None, None, :] + A[..., None] * e_long[:, None, None, :] + B[..., None] * e_short[:, None, None, :]
    eta = np.arcsinh(P[..., 2] / np.hypot(P[..., 0], P[..., 1]))
    exists = ahi > alo
    accept[:, ci] = np.where(exists, (abs(eta) < 2.5).mean((1, 2)), 0)
geo["accept"] = accept
np.savez(out, **geo)

# validation: per-layer summary and hit -> module assignment on independent files
G = CG.Geometry(out)
summ = {}
for l in np.unique(lid):
    s = lid == l
    summ[int(l)] = {"modules": int(s.sum()), "chips": int((n_long[s] * n_short[s]).sum()),
                    "layout(long x short chips)": {f"{a}x{b}": int(((n_long[s] == a) & (n_short[s] == b)).sum())
                                                   for a in (1, 2) for b in (1, 2) if ((n_long[s] == a) & (n_short[s] == b)).any()},
                    "L_long_mm_median": float(np.median(L_long[s]) * 10), "L_short_mm_median": float(np.median(L_short[s]) * 10),
                    "w_rms_um_median": float(np.median(geo["w_rms"][s]) * 1e4),
                    "nhits_median": float(np.median(nh[s])), "chip_accept_mean": float(accept[s].sum() / (n_long[s] * n_short[s]).sum())}
nv = nok = nin = 0
for det, p, hs, hl in chunks(val):
    m, ch, ok, *_ = G.assign(p, CG.lid_of(hs, hl, p[:, 2]))
    known = np.isin(det, G.detid)
    nv += known.sum()
    nok += (G.detid[np.maximum(m, 0)][known] == det[known]).sum()
    nin += ok[known].sum()
val_res = {"train_files": len(train), "train_hits": float(nh.sum()), "modules": len(ids),
           "val_hits": int(nv), "val_assigned_to_own_detId": nok / max(nv, 1), "val_inside_flag": nin / max(nv, 1),
           "by_layer": summ}
json.dump(val_res, open(out_val, "w"), indent=1)
print(json.dumps(val_res, indent=1))

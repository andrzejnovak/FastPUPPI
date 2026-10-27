#!/usr/bin/env python3
"""Side check: does the v2 summary (charm_feats2.py, calibrated 3D IP) also change the per-jet b tag?

    python3 btag_v2check.py OUT.json lists_l1ext_HH4b.npz lists_l1ext_QCDFlat.npz
As train_sets.py "NN + jet summary (BDT)": b jets from HH->4b vs QCD light (reweighted to the b-jet pT, |eta|),
even/odd folds; b-eff at 1% / 10% light mistag for the NN, the old summary, v2 summary, v2 summary + charm word.
"""
import json
import os
import sys

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_curve

from charm_feats2 import charm2, summary2
from train_sets import jet_features, kin_weights, load, summary_features

out, f_b, f_l = sys.argv[1:4]
b, l = load(f_b), load(f_l)
b = {k: v[b["flav"] == 5] for k, v in b.items() if k != "hit"}
l = {k: v[l["flav"] == 0] for k, v in l.items() if k != "hit"}
w = np.concatenate([np.ones(len(b["pt"])), kin_weights(b, l)])
y = np.concatenate([np.ones(len(b["pt"])), np.zeros(len(l["pt"]))])
d = {k: np.concatenate([b[k], l[k]]) for k in b}
d["evt"] = np.concatenate([b["evt"], l["evt"] + 10_000_000])
fold = d["evt"] % 2
jf = jet_features(d)
sets = {"old summary": np.column_stack([jf, summary_features(d["trk"], d["ntrk"])]),
        "v2 summary": np.column_stack([jf, summary2(d["trk"], d["ntrk"], d["eta"])]),
        "v2 summary + charm": np.column_stack([jf, summary2(d["trk"], d["ntrk"], d["eta"]),
                                               charm2(d["trk"], d["ntrk"], d["eta"], d["pt"])])}
res = {}
s = d["scores"]
preds = {"L1 NN": s[:, 0] / np.clip(s[:, 0] + s[:, 2] + s[:, 3], 1e-6, None)}
for name, X in sets.items():
    p = np.zeros(len(y))
    for f in (0, 1):
        tr, te = fold == f, fold != f
        ww = w[tr].copy()
        ww[y[tr] == 0] *= y[tr].sum() / ww[y[tr] == 0].sum()
        clf = HistGradientBoostingClassifier(max_iter=300, max_leaf_nodes=31, random_state=1)
        p[te] = clf.fit(X[tr], y[tr], sample_weight=ww).predict_proba(X[te])[:, 1]
    preds[name] = p
for name, p in preds.items():
    fpr, tpr, _ = roc_curve(y, p, sample_weight=w)
    res[name] = {"b_at_0.01": float(np.interp(0.01, fpr, tpr)), "b_at_0.1": float(np.interp(0.1, fpr, tpr))}
    print(f"{name:22s} b-eff @1% {res[name]['b_at_0.01']:.3f}  @10% {res[name]['b_at_0.1']:.3f}", flush=True)
res["n_b"], res["n_light"] = int(y.sum()), int((y == 0).sum())
json.dump(res, open(out + ".tmp", "w"), indent=1)
os.replace(out + ".tmp", out)

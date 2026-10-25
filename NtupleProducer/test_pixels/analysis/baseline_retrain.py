#!/usr/bin/env python3
"""Is the pixel gain just retraining? Same BDT on the 8 NN scores + jet pT, eta, with and without the pixel summary.

    python3 baseline_retrain.py lists_hh4b.npz lists_qcd.npz
Two folds by event parity, as train_sets.py; b-jet efficiency at 1% and 10% light mistag (light reweighted to b kinematics).
"""
import sys

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, roc_curve

from train_sets import jet_features, kin_weights, load, summary_features

b, l = load(sys.argv[1]), load(sys.argv[2])
b = {k: v[b["flav"] == 5] for k, v in b.items()}
l = {k: v[l["flav"] == 0] for k, v in l.items()}
d = {k: np.concatenate([b[k], l[k]]) for k in b}
y = np.concatenate([np.ones(len(b["pt"])), np.zeros(len(l["pt"]))])
w = np.concatenate([np.ones(len(b["pt"])), kin_weights(b, l)])
fold = (np.concatenate([b["evt"], l["evt"] + 10_000_000]) % 2).astype(int)
jf = jet_features(d)
s = d["scores"]
inputs = {"NN ratio b/(b+uds+g), no training": None,
          "BDT on 8 NN scores + pT, eta (no pixels)": jf,
          "BDT on 8 NN scores + pT, eta + pixel summary": np.column_stack([jf, summary_features(d["trk"], d["ntrk"])])}
for name, X in inputs.items():
    pred = np.zeros(len(y))
    for f in (0, 1):
        tr, te = fold == f, fold != f
        if X is None:
            pred[te] = s[te, 0] / np.clip(s[te, 0] + s[te, 2] + s[te, 3], 1e-6, None)
            continue
        ww = w[tr].copy()
        ww[y[tr] == 0] *= y[tr].sum() / ww[y[tr] == 0].sum()
        clf = HistGradientBoostingClassifier(max_iter=300, max_leaf_nodes=31, random_state=1).fit(X[tr], y[tr], sample_weight=ww)
        pred[te] = clf.predict_proba(X[te])[:, 1]
    fpr, tpr, _ = roc_curve(y, pred, sample_weight=w)
    print(f"{name:48s} AUC {roc_auc_score(y, pred, sample_weight=w):.3f}  b@1% {np.interp(0.01, fpr, tpr):.3f}  b@10% {np.interp(0.10, fpr, tpr):.3f}", flush=True)

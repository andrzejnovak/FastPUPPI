#!/usr/bin/env python3
"""Per-jet c-tagging with and without pixel inputs, on QCD jets only (c, light and b from the same sample).

    python3 ctag_compare.py OUT.json NAME:QCD.npz [NAME:QCD.npz ...]
CvsL: c efficiency at 1% / 10% light mistag; CvsB: c efficiency at 10% / 30% b mistag. L1 NN = today's discriminants
c / (c + uds + g) and c / (c + b); NN only = BDT on the 8 NN scores + pT, eta (closure); NAME = BDT on those plus the
8-number pixel summary from that list. Same BDT and even/odd folds as tag_compare.py; the background is reweighted to
the c-jet pT, eta spectrum.
"""
import json
import sys

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_curve

from train_sets import jet_features, kin_weights, load, summary_features

MIS = np.logspace(-3.5, 0, 60)
WP = {"CvsL": (0.01, 0.1), "CvsB": (0.1, 0.3)}
res = {"CvsL": {}, "CvsB": {}}


def store(task, tag, y, pred, w):
    fpr, tpr, _ = roc_curve(y, pred, sample_weight=w)
    lo, hi = WP[task]
    r = {f"c_at_{lo:g}": float(np.interp(lo, fpr, tpr)), f"c_at_{hi:g}": float(np.interp(hi, fpr, tpr)),
         "roc_mistag": MIS.tolist(), "roc_ceff": np.interp(MIS, fpr, tpr).tolist(),
         "n_c": int(y.sum()), "n_bkg": int((y == 0).sum())}
    res[task][tag] = r
    print(f"{task} {tag:14s} c-eff @{lo:g} {r[f'c_at_{lo:g}']:.3f}  @{hi:g} {r[f'c_at_{hi:g}']:.3f}", flush=True)


def bdt(X, y, w, fold):
    pred = np.zeros(len(y))
    for f in (0, 1):
        tr, te = fold == f, fold != f
        ww = w[tr].copy()
        ww[y[tr] == 0] *= y[tr].sum() / ww[y[tr] == 0].sum()
        clf = HistGradientBoostingClassifier(max_iter=300, max_leaf_nodes=31, random_state=1)
        pred[te] = clf.fit(X[tr], y[tr], sample_weight=ww).predict_proba(X[te])[:, 1]
    return pred


for spec in sys.argv[2:]:
    name, path = spec.split(":")
    q = load(path)
    for task, bflav in (("CvsL", 0), ("CvsB", 5)):
        c = {k: v[q["flav"] == 4] for k, v in q.items()}
        o = {k: v[q["flav"] == bflav] for k, v in q.items()}
        d = {k: np.concatenate([c[k], o[k]]) for k in c}
        y = np.concatenate([np.ones(len(c["pt"])), np.zeros(len(o["pt"]))])
        w = np.concatenate([np.ones(len(c["pt"])), kin_weights(c, o)])
        fold = d["event"] % 2
        sc = d["scores"]
        if "L1 NN" not in res[task]:
            den = sc[:, 1] + (sc[:, 2] + sc[:, 3] if task == "CvsL" else sc[:, 0])
            store(task, "L1 NN", y, sc[:, 1] / np.maximum(den, 1e-6), w)
        if "NN only" not in res[task]:
            store(task, "NN only", y, bdt(jet_features(d), y, w, fold), w)
        X = np.column_stack([jet_features(d), summary_features(d["trk"], d["ntrk"])])
        store(task, name, y, bdt(X, y, w, fold), w)
json.dump(res, open(sys.argv[1], "w"), indent=1)

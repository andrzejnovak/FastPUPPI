#!/usr/bin/env python3
"""Per-jet b-tagging with different pixel inputs: b efficiency at 1% / 10% light mistag (QCD light jets), two folds
split by event parity, same BDT as direct_rate.py.

    python3 tag_compare.py OUT.json NAME:HH.npz:QCD.npz [NAME:HH.npz:QCD.npz ...]   (env OFFLINE="HH_GLOB:QCD_GLOB")
L1 NN = today's discriminant b / (b + uds + g) (baseline); NN only = BDT on the 8 NN scores + pT, eta (closure:
should equal the baseline); NAME = BDT on those plus the 8-number pixel summary from that list. With OFFLINE, also
the offline UParT B-vs-all on offline jets (pT > 30, |eta| < 2.5, b vs light from hadron flavour): a reference on
different jets, not an L1 comparison. ROC curves are saved (b efficiency at log-spaced light mistag).
"""
import glob
import json
import os
import sys

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_curve

from train_sets import jet_features, kin_weights, load, summary_features

MIS = np.logspace(-3.5, 0, 60)
res = {}


def store(tag, y, pred, w, ntrk=None):
    fpr, tpr, _ = roc_curve(y, pred, sample_weight=w)
    res[tag] = {"b_at_1pct": float(np.interp(0.01, fpr, tpr)), "b_at_10pct": float(np.interp(0.1, fpr, tpr)),
                "roc_mistag": MIS.tolist(), "roc_beff": np.interp(MIS, fpr, tpr).tolist(), "n_b": int(y.sum()),
                "n_light": int((y == 0).sum())}
    if ntrk is not None:
        res[tag]["mean_tracks_bjet"] = float(ntrk[y == 1].mean())
    print(f"{tag:14s} b-eff @1% {res[tag]['b_at_1pct']:.3f}  @10% {res[tag]['b_at_10pct']:.3f}", flush=True)


for spec in sys.argv[2:]:
    name, fh, fq = spec.split(":")
    b, l = load(fh), load(fq)
    b = {k: v[b["flav"] == 5] for k, v in b.items()}
    l = {k: v[l["flav"] == 0] for k, v in l.items()}
    d = {k: np.concatenate([b[k], l[k]]) for k in b}
    y = np.concatenate([np.ones(len(b["pt"])), np.zeros(len(l["pt"]))])
    w = np.concatenate([np.ones(len(b["pt"])), kin_weights(b, l)])
    fold = d["event"] % 2
    if "L1 NN" not in res:
        sc = d["scores"]
        store("L1 NN", y, sc[:, 0] / np.maximum(sc[:, 0] + sc[:, 2] + sc[:, 3], 1e-6), w)
    for tag, X in (("NN only", jet_features(d)), (name, np.column_stack([jet_features(d), summary_features(d["trk"], d["ntrk"])]))):
        if tag in res:
            continue
        pred = np.zeros(len(y))
        for f in (0, 1):
            tr, te = fold == f, fold != f
            ww = w[tr].copy()
            ww[y[tr] == 0] *= y[tr].sum() / ww[y[tr] == 0].sum()
            clf = HistGradientBoostingClassifier(max_iter=300, max_leaf_nodes=31, random_state=1).fit(X[tr], y[tr], sample_weight=ww)
            pred[te] = clf.predict_proba(X[te])[:, 1]
        store(tag, y, pred, w, d["ntrk"])
if os.environ.get("OFFLINE"):
    hp, qp = os.environ["OFFLINE"].split(":")
    cat = lambda pat: {k: np.concatenate([np.load(f)[k] for f in sorted(glob.glob(pat))]) for k in ("pt", "eta", "upart", "flav")}
    h, q = cat(hp), cat(qp)
    mb = (h["flav"] == 5) & (h["pt"] > 30) & (abs(h["eta"]) < 2.5)
    ml = (q["flav"] == 0) & (q["pt"] > 30) & (abs(q["eta"]) < 2.5)
    yo = np.concatenate([np.ones(mb.sum()), np.zeros(ml.sum())])
    store("offline UParT", yo, np.concatenate([h["upart"][mb], q["upart"][ml]]), np.ones(len(yo)))
json.dump(res, open(sys.argv[1], "w"), indent=1)

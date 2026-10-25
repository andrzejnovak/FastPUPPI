#!/usr/bin/env python3
"""What if only tracks that L1 already finds (Outer Tracker, pT > 2 GeV) get pixel information?

    python3 pt2_test.py lists_hh4b.npz lists_qcd.npz [lists_minbias.npz]
Proxy: keep only the jet's pixel tracks with pT above a threshold, recompute the 8-number summary, retrain the BDT.
b-jet efficiency at 1%/10% light mistag (two folds), and fake rate on minimum-bias HT>150 jets at eps_b = 50/60/70%.
"""
import sys

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, roc_curve

from train_sets import jet_features, kin_weights, load, summary_features


def keep_pt(dd, ptmin):
    trk = dd["trk"].copy()
    valid = np.arange(trk.shape[1])[None, :] < dd["ntrk"][:, None]
    ok = valid & (np.exp(trk[:, :, 0]) > ptmin)
    order = np.argsort(~ok, axis=1, kind="stable")  # kept tracks first, keep significance order
    trk = np.take_along_axis(trk, order[..., None], 1)
    return trk, ok.sum(1)


def main():
    b, l = load(sys.argv[1]), load(sys.argv[2])
    b = {k: v[b["flav"] == 5] for k, v in b.items()}
    l = {k: v[l["flav"] == 0] for k, v in l.items()}
    d = {k: np.concatenate([b[k], l[k]]) for k in b}
    y = np.concatenate([np.ones(len(b["pt"])), np.zeros(len(l["pt"]))])
    w = np.concatenate([np.ones(len(b["pt"])), kin_weights(b, l)])
    evt = np.concatenate([b["evt"], l["evt"] + 10_000_000])
    fold = (evt % 2).astype(int)
    jf = jet_features(d)
    mb = load(sys.argv[3]) if len(sys.argv) > 3 else None
    if mb is not None:
        ht = {}
        for e, p in zip(mb["evt"], mb["pt"]):
            ht[e] = ht.get(e, 0.0) + p
        hard = np.array([ht[e] for e in mb["evt"]]) > 150
    for ptmin in (0.0, 2.0, 3.0):
        trk, n = keep_pt(d, ptmin)
        X = np.column_stack([jf, summary_features(trk, n)])
        pred = np.zeros(len(y))
        for f in (0, 1):
            tr, te = fold == f, fold != f
            ww = w[tr].copy()
            ww[y[tr] == 0] *= y[tr].sum() / ww[y[tr] == 0].sum()
            clf = HistGradientBoostingClassifier(max_iter=300, max_leaf_nodes=31, random_state=1).fit(X[tr], y[tr], sample_weight=ww)
            pred[te] = clf.predict_proba(X[te])[:, 1]
            if f == 0 and mb is not None:
                tmb, nmb = keep_pt(mb, ptmin)
                s_mb = clf.predict_proba(np.column_stack([jet_features(mb), summary_features(tmb, nmb)]))[:, 1]
                s_b = pred[te & (y == 1)]
                fr = [float((s_mb[hard] > np.quantile(s_b, 1 - e)).mean()) for e in (0.5, 0.6, 0.7)]
        fpr, tpr, _ = roc_curve(y, pred, sample_weight=w)
        msg = f"tracks pT>{ptmin:.0f}: mean tracks/b-jet {n[y == 1].mean():.1f}  AUC {roc_auc_score(y, pred, sample_weight=w):.3f}  b@1% {np.interp(0.01, fpr, tpr):.3f}  b@10% {np.interp(0.10, fpr, tpr):.3f}"
        if mb is not None:
            msg += f"  MB HT>150 fakes @eb50/60/70: {fr[0]:.3f} {fr[1]:.3f} {fr[2]:.3f}"
        print(msg, flush=True)


if __name__ == "__main__":
    main()

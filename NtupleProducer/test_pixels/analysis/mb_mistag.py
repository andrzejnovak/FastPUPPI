#!/usr/bin/env python3
"""Fake rate of pixel-augmented taggers on minimum-bias jets, the jets that set the L1 rate.

    python3 mb_mistag.py OUT.json lists_hh4b.npz lists_qcd.npz lists_minbias.npz

Taggers are trained on even events (HH->4b b vs QCD light, as in train_sets.py). Working points are set on odd-event
HH->4b b jets (eps_b = 0.5, 0.6, 0.7) and applied to QCD light jets (odd events) and to minimum-bias jets: all of them,
and those in events with HT > 150 GeV (HT from L1 jets pT > 30 GeV, |eta| < 2.4, as in the seed study).
"""
import json
import os
import sys

import numpy as np

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
import tensorflow as tf  # noqa: E402
from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: E402

from train_sets import deepsets, jet_features, kin_weights, load, standardize, summary_features  # noqa: E402

EFFS = (0.5, 0.6, 0.7)


def main():
    out, f_b, f_l, f_mb = sys.argv[1:5]
    b, l, mb = load(f_b), load(f_l), load(f_mb)
    b = {k: v[b["flav"] == 5] for k, v in b.items()}
    l = {k: v[l["flav"] == 0] for k, v in l.items()}
    d = {k: np.concatenate([b[k], l[k]]) for k in b}
    y = np.concatenate([np.ones(len(b["pt"])), np.zeros(len(l["pt"]))])
    w = np.concatenate([np.ones(len(b["pt"])), kin_weights(b, l)])
    evt = np.concatenate([b["evt"], l["evt"] + 10_000_000])
    tr = evt % 2 == 0
    te_b, te_l = (~tr) & (y == 1), (~tr) & (y == 0)
    ww = w[tr].copy()
    ww[y[tr] == 0] *= y[tr].sum() / ww[y[tr] == 0].sum()

    ht = {}
    for e, p in zip(mb["evt"], mb["pt"]):
        ht[e] = ht.get(e, 0.0) + p
    mb_ht = np.array([ht[e] for e in mb["evt"]])
    hard = mb_ht > 150
    print(f"train jets {tr.sum()}, MB jets {len(mb['pt'])} (in HT>150 events: {hard.sum()}), "
          f"MB flavour fractions {dict(zip(*np.unique(mb['flav'], return_counts=True)))}", flush=True)

    scores = {}
    nn = lambda s: s[:, 0] / np.clip(s[:, 0] + s[:, 2] + s[:, 3], 1e-6, None)
    scores["L1 NN only"] = (nn(d["scores"]), nn(mb["scores"]))

    jf, jf_mb = jet_features(d), jet_features(mb)
    X, X_mb = np.column_stack([jf, summary_features(d["trk"], d["ntrk"])]), np.column_stack([jf_mb, summary_features(mb["trk"], mb["ntrk"])])
    clf = HistGradientBoostingClassifier(max_iter=300, max_leaf_nodes=31, random_state=1).fit(X[tr], y[tr], sample_weight=ww)
    scores["NN + 8-number summary (BDT)"] = (clf.predict_proba(X)[:, 1], clf.predict_proba(X_mb)[:, 1])

    k = 16
    M = (np.arange(k)[None, :] < d["ntrk"][:, None]).astype(np.float32)
    M_mb = (np.arange(k)[None, :] < mb["ntrk"][:, None]).astype(np.float32)
    (Ttr, Tall, Tmb), _ = standardize(d["trk"][tr, :k], d["trk"][:, :k], mb["trk"][:, :k]), None
    (Jtr, Jall, Jmb), _ = standardize(jf[tr], jf, jf_mb), None
    Ttr, Tall, Tmb = Ttr * M[tr][..., None], Tall * M[..., None], Tmb * M_mb[..., None]
    model = deepsets(k, Ttr.shape[-1], d["hit"].shape[-1], jf.shape[-1], use_trk=True, use_hit=False, use_jet=True)
    perm = np.random.default_rng(0).permutation(int(tr.sum()))
    model.fit({"trk": Ttr[perm], "mask": M[tr][perm], "jet": Jtr[perm]}, y[tr][perm], sample_weight=ww[perm], epochs=200,
              batch_size=256, validation_split=0.2, verbose=0,
              callbacks=[tf.keras.callbacks.EarlyStopping(patience=8, restore_best_weights=True)])
    pred = lambda T, Mx, J: model.predict({"trk": T, "mask": Mx, "jet": J}, batch_size=4096, verbose=0)[:, 0]
    scores["NN + 16 pixel tracks (set network)"] = (pred(Tall, M, Jall), pred(Tmb, M_mb, Jmb))

    res = {"n_mb_jets": int(len(mb["pt"])), "n_mb_jets_ht150": int(hard.sum()),
           "mb_flavour": {int(f): int(c) for f, c in zip(*np.unique(mb["flav"], return_counts=True))}, "taggers": {}}
    for name, (s, s_mb) in scores.items():
        rows = []
        for eb in EFFS:
            thr = np.quantile(s[te_b], 1 - eb)
            rows.append({"eps_b": eb,
                         "mistag_qcd_light": float(np.average(s[te_l] > thr, weights=w[te_l])),
                         "mistag_mb_all": float((s_mb > thr).mean()),
                         "mistag_mb_ht150": float((s_mb[hard] > thr).mean()) if hard.any() else None,
                         "mistag_mb_ht150_by_flav": {int(f): float((s_mb[hard & (mb["flav"] == f)] > thr).mean())
                                                     for f in np.unique(mb["flav"][hard])}})
        res["taggers"][name] = rows
        for r in rows:
            print(f"{name:38s} eps_b {r['eps_b']:.1f}: QCD light {r['mistag_qcd_light']:.3f}  MB all {r['mistag_mb_all']:.3f}  "
                  f"MB HT>150 {r['mistag_mb_ht150']:.3f}", flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Can a network recover track information from pixel hits, and how does that scale with training data?

    python3 regress_hits.py OUTDIR lists_hh4b.npz lists_qcd.npz

Labels come from the HLT pixel-track fit, so every jet of every flavour is usable (no b/light labels needed).
  A. per track, hits grouped by track: 4 hits -> signed IP and IP significance (the fit, learned)
  B. per jet, hits pooled without track grouping and shuffled: up to 64 hits -> the 8-number jet summary
     (hits still come only from vertex-compatible pixel tracks: optimistic versus all clusters in the cone)
Then B's predicted summary replaces the true one in the NN + summary b-tagger, to see how much tagging survives.
Trained on even events, tested on odd. Writes regress.json.
"""
import json
import os
import sys

import numpy as np

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
import tensorflow as tf  # noqa: E402
from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: E402

from train_sets import jet_features, kin_weights, load, summary_features  # noqa: E402

FRACS = (0.03, 0.1, 0.3, 1.0)


def r2(pred, true):
    return 1 - ((pred - true) ** 2).sum(0) / ((true - true.mean(0)) ** 2).sum(0)


def standardize(train, *others):
    mu = train.reshape(-1, train.shape[-1]).mean(0)
    sd = train.reshape(-1, train.shape[-1]).std(0) + 1e-6
    return [(a - mu) / sd for a in (train,) + others], (mu, sd)


def fit(model, X, y, seed):
    perm = np.random.default_rng(seed).permutation(len(y))
    X = {k: v[perm] for k, v in X.items()} if isinstance(X, dict) else X[perm]
    cb = [tf.keras.callbacks.EarlyStopping(patience=6, restore_best_weights=True)]
    model.fit(X, y[perm], epochs=150, batch_size=512, validation_split=0.15, callbacks=cb, verbose=0)


def track_mlp(n_in, n_out):
    inp = tf.keras.Input((n_in,))
    x = inp
    for w in (128, 128, 64):
        x = tf.keras.layers.Dense(w, activation="relu")(x)
    m = tf.keras.Model(inp, tf.keras.layers.Dense(n_out)(x))
    m.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="mse")
    return m


def hit_deepsets(n_hit, n_hf, n_out):
    inp_h = tf.keras.Input((n_hit, n_hf), name="hit")
    inp_m = tf.keras.Input((n_hit,), name="mask")
    x = inp_h
    for w in (64, 64, 64):
        x = tf.keras.layers.Dense(w, activation="relu")(x)
    m = tf.keras.layers.Reshape((n_hit, 1))(inp_m)
    xs = tf.keras.layers.Multiply()([x, m])
    mean = tf.keras.layers.Lambda(lambda a: tf.reduce_sum(a[0], 1) / tf.maximum(tf.reduce_sum(a[1], 1), 1.0))([xs, m])
    mx = tf.keras.layers.Lambda(lambda a: tf.reduce_max(a[0] + (a[1] - 1.0) * 1e3, 1))([x, m])
    mx = tf.keras.layers.Lambda(lambda a: tf.where(tf.reduce_sum(a[1], 1) > 0, a[0], 0.0))([mx, m])
    z = tf.keras.layers.Concatenate()([mean, mx])
    for w in (128, 64):
        z = tf.keras.layers.Dense(w, activation="relu")(z)
    model = tf.keras.Model([inp_h, inp_m], tf.keras.layers.Dense(n_out)(z))
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="mse")
    return model


def main():
    out, f_b, f_l = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    b, l = load(f_b), load(f_l)
    d = {k: np.concatenate([b[k], l[k]]) for k in b}
    d["evt"] = np.concatenate([b["evt"], l["evt"] + 10_000_000])
    even = d["evt"] % 2 == 0
    ntrk = d["ntrk"]
    res = {"n_jets": int(len(ntrk)), "n_tracks": int(ntrk.sum())}
    print(f"jets {len(ntrk)}, tracks {ntrk.sum()}", flush=True)

    # ---- A. per track: 4 hits -> (signed IP, IP significance)
    valid = np.arange(16)[None, :] < ntrk[:, None]
    X_t = d["hit"][valid].reshape(-1, 4 * d["hit"].shape[-1])
    y_t = d["trk"][valid][:, [4, 5]]
    y_t[:, 1] = np.clip(y_t[:, 1], -20, 20)
    ev_t = np.repeat(even, ntrk)
    (Xtr, Xte), _ = standardize(X_t[ev_t], X_t[~ev_t])
    (ytr, yte), (mu, sd) = standardize(y_t[ev_t], y_t[~ev_t])
    res["A"] = []
    for frac in FRACS:
        n = int(frac * len(ytr))
        m = track_mlp(Xtr.shape[1], 2)
        fit(m, Xtr[:n], ytr[:n], 1)
        p = m.predict(Xte, batch_size=8192, verbose=0) * sd + mu
        t = yte * sd + mu
        rr = r2(p, t)
        big_true, big_pred = t[:, 1] > 3, p[:, 1] > 3
        row = {"frac": frac, "n_train_tracks": n, "r2_ip": float(rr[0]), "r2_ipsig": float(rr[1]),
               "sig3_recall": float((big_true & big_pred).sum() / max(big_true.sum(), 1)),
               "sig3_purity": float((big_true & big_pred).sum() / max(big_pred.sum(), 1))}
        res["A"].append(row)
        print("A", json.dumps(row), flush=True)

    # ---- B. per jet: pooled, shuffled hits (no track grouping) -> 8-number summary
    nh = d["hit"].shape[-1]
    H = d["hit"].reshape(len(ntrk), 64, nh)
    M = np.repeat(valid, 4, axis=1).astype(np.float32)
    rng = np.random.default_rng(7)
    perm = np.argsort(rng.random((len(ntrk), 64)) + (1 - M) * 10, axis=1)  # shuffle real hits, padding last
    H = np.take_along_axis(H, perm[..., None], 1)
    M = np.take_along_axis(M, perm, 1)
    S = summary_features(d["trk"], ntrk)
    S[:, :3] = np.clip(S[:, :3], -20, 20)
    (Htr, Hte), _ = standardize(H[even], H[~even])
    Htr, Hte = Htr * M[even][..., None], Hte * M[~even][..., None]
    (Str, Ste), (smu, ssd) = standardize(S[even], S[~even])
    res["B"] = []
    pred_full = None
    for frac in FRACS[1:]:
        n = int(frac * len(Str))
        m = hit_deepsets(64, nh, S.shape[1])
        fit(m, {"hit": Htr[:n], "mask": M[even][:n]}, Str[:n], 2)
        p = m.predict({"hit": Hte, "mask": M[~even]}, batch_size=4096, verbose=0) * ssd + smu
        rr = r2(p, Ste * ssd + smu)
        row = {"frac": frac, "n_train_jets": n, "r2_per_feature": [float(x) for x in rr]}
        res["B"].append(row)
        print("B", json.dumps(row), flush=True)
        pred_full = p

    # ---- does tagging survive? NN + true summary vs NN + summary predicted from pooled hits (b vs light, odd events)
    te = ~even
    y = np.where(d["flav"] == 5, 1, np.where(d["flav"] == 0, 0, -1))
    jf = jet_features(d)
    bl = (y >= 0)
    w = np.ones(len(y))
    lmask = bl & (y == 0)
    w[lmask] = kin_weights({k: v[y == 1] for k, v in d.items()}, {k: v[lmask] for k, v in d.items()})
    Sp = np.zeros_like(S)
    Sp[te] = pred_full
    from sklearn.metrics import roc_auc_score, roc_curve
    tag = {}
    for name, feats in (("NN + true summary", S), ("NN + summary from pooled hits", Sp)):
        X = np.column_stack([jf, feats])
        idx = np.where(te & bl)[0]
        half = (d["evt"][idx] // 2) % 2 == 0  # split the odd events again: train / evaluate
        tr_i, ev_i = idx[half], idx[~half]
        ww = w[tr_i].copy()
        ww[y[tr_i] == 0] *= (y[tr_i] == 1).sum() / ww[y[tr_i] == 0].sum()
        clf = HistGradientBoostingClassifier(max_iter=300, max_leaf_nodes=31, random_state=1).fit(X[tr_i], y[tr_i], sample_weight=ww)
        s = clf.predict_proba(X[ev_i])[:, 1]
        fpr, tpr, _ = roc_curve(y[ev_i], s, sample_weight=w[ev_i])
        tag[name] = {"auc": float(roc_auc_score(y[ev_i], s, sample_weight=w[ev_i])),
                     "beff_1pct": float(np.interp(0.01, fpr, tpr)), "beff_10pct": float(np.interp(0.10, fpr, tpr))}
        print("tag", name, json.dumps(tag[name]), flush=True)
    res["tagging"] = tag
    json.dump(res, open(os.path.join(out, "regress.json"), "w"), indent=1)


if __name__ == "__main__":
    main()

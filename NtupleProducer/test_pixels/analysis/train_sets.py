#!/usr/bin/env python3
"""How much does each extra block of pixel information buy, per bit sent?

    python3 train_sets.py OUTDIR lists_hh4b.npz lists_qcd.npz

b jets from HH->4b, light jets from QCD (reweighted to the b-jet pT/|eta| spectrum). Each
configuration is trained twice (even->odd and odd->even events) so every jet gets an
out-of-sample score. Writes budget.json and budget.png (b-eff at fixed light mistag vs bits/jet).
"""
import json
import os
import sys

import numpy as np

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
try:
    import tensorflow as tf  # noqa: E402  (only the deep-set training needs it)
except ImportError:
    tf = None
from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: E402
from sklearn.metrics import roc_auc_score, roc_curve  # noqa: E402

# ---- assumed word sizes (bits) -------------------------------------------------------------
BITS_TRACK = 64  # pT, eta, phi, z0, d0, d0 uncertainty, quality
BITS_HIT = 40  # layer/disk, phi, z (or r), cluster sizeX/sizeY, charge
BITS_SUMMARY = 64  # 8 per-jet summary features x 8 bits
BITS_PUPPI_JET = 16 * 64  # what the current NN tagger already receives per jet (reference)

PT_BINS = np.array([30, 40, 50, 60, 75, 90, 110, 135, 165, 200, 300])
ETA_BINS = np.array([0, 0.8, 1.5, 2.4])


def load(path):
    d = dict(np.load(path, allow_pickle=True))
    m = (d["pt"] < 300) & (abs(d["eta"]) < 2.4)
    return {k: v[m] for k, v in d.items() if k not in ("sample", "trk_feats", "hit_feats")}


def kin_weights(ref, d):
    h_ref, _, _ = np.histogram2d(ref["pt"], abs(ref["eta"]), bins=[PT_BINS, ETA_BINS])
    h_d, _, _ = np.histogram2d(d["pt"], abs(d["eta"]), bins=[PT_BINS, ETA_BINS])
    ratio = np.divide(h_ref / h_ref.sum(), h_d / h_d.sum(), out=np.zeros_like(h_ref), where=h_d > 0)
    ip = np.clip(np.digitize(d["pt"], PT_BINS) - 1, 0, len(PT_BINS) - 2)
    ie = np.clip(np.digitize(abs(d["eta"]), ETA_BINS) - 1, 0, len(ETA_BINS) - 2)
    return ratio[ip, ie]


def pixel_summary(d, l1=False):
    """8-number pixel summary of a list dict. With PIXSUM=v2, lists of L1 tracks with pixel hits (l1=True) use the
    recalibrated 3D impact-parameter summary of charm_feats2.py (same 8 numbers and bits; its resolution table is
    calibrated for the L1-track refit, so HLT pixel and Outer-Tracker-only lists keep the stored significance).
    PIXSUM=q8: the original summary quantised to 8 bits per feature (64 bits per jet)."""
    mode = os.environ.get("PIXSUM", "v1") if l1 else "v1"
    if mode == "v2":
        from charm_feats2 import summary2
        return summary2(d["trk"], d["ntrk"], d["eta"])
    if mode == "v2xy":  # recalibrated transverse significance only (no longitudinal term)
        from charm_feats2 import track_views
        t = track_views(d["trk"], d["ntrk"], d["eta"])
        sxy = np.where(t["valid"], np.clip(t["sxy"], -50, 50), -50.0)
        top = np.sort(sxy, axis=1)[:, ::-1][:, :3]
        sipm = np.where(t["valid"], t["sip"], -1.0)
        return np.column_stack([top, d["ntrk"], (sxy > 3).sum(1), (sxy > 5).sum(1), np.where(sxy > 0, sxy, 0).sum(1),
                                sipm.max(1)]).astype(np.float32)
    if mode == "q8":  # the 64-bit word: 8 features x 8 bits, as the firmware would send it (quantize_summary)
        return quantize_summary(summary_features(d["trk"], d["ntrk"]))
    return summary_features(d["trk"], d["ntrk"])


def summary_features(trk, ntrk):
    sig = np.where(np.arange(trk.shape[1])[None, :] < ntrk[:, None], trk[:, :, 5], -50.0)
    top = np.sort(sig, axis=1)[:, ::-1][:, :3]
    sip = np.where(np.arange(trk.shape[1])[None, :] < ntrk[:, None], trk[:, :, 4], -1.0)
    return np.column_stack([top, ntrk, (sig > 3).sum(1), (sig > 5).sum(1), np.where(sig > 0, sig, 0).sum(1), sip.max(1)])


def quantize_summary(summ):
    """8-bit fixed point per feature, as L1 firmware would carry it (truncate, saturate)."""
    q = summ.copy()
    q[:, :3] = np.clip(np.floor(q[:, :3] * 8) / 8, -16, 15.875)  # IP significance: ap_fixed<8,5>
    q[:, 3:6] = np.clip(q[:, 3:6], 0, 255)  # track counts: 8-bit integers
    q[:, 6] = np.clip(np.floor(q[:, 6] * 2) / 2, 0, 127.5)  # sum of positive significances: ap_ufixed<8,7>
    q[:, 7] = np.clip(np.floor(q[:, 7] / 0.02) * 0.02, -2.56, 2.54)  # largest signed IP [mm, as stored by make_lists], 20 um steps
    return q


def jet_features(d):
    return np.column_stack([d["scores"], np.log(d["pt"]), d["eta"]]).astype(np.float32)


def deepsets(n_trk, n_tf, n_hf, n_jf, use_trk, use_hit, use_jet, wide=False):
    wh, wt, wz = (64, 128, 64) if wide else (16, 32, 32)
    inp_t = tf.keras.Input((n_trk, n_tf), name="trk")
    inp_h = tf.keras.Input((n_trk, 4, n_hf), name="hit")
    inp_m = tf.keras.Input((n_trk,), name="mask")
    inp_j = tf.keras.Input((n_jf,), name="jet")
    parts = []
    if use_hit:
        h = tf.keras.layers.Dense(wh, activation="relu")(inp_h)
        h = tf.keras.layers.Dense(wh, activation="relu")(h)
        h = tf.keras.layers.Reshape((n_trk, 4 * wh))(h)  # keep layer order: hits are ordered inside out
        parts.append(h)
    if use_trk:
        parts.append(inp_t)
    x = parts[0] if len(parts) == 1 else tf.keras.layers.Concatenate()(parts)
    x = tf.keras.layers.Dense(wt, activation="relu")(x)
    x = tf.keras.layers.Dense(wt, activation="relu")(x)
    m = tf.keras.layers.Reshape((n_trk, 1))(inp_m)
    xs = tf.keras.layers.Multiply()([x, m])
    mean = tf.keras.layers.Lambda(lambda a: tf.reduce_sum(a[0], 1) / tf.maximum(tf.reduce_sum(a[1], 1), 1.0))([xs, m])
    mx = tf.keras.layers.Lambda(lambda a: tf.reduce_max(a[0] + (a[1] - 1.0) * 1e3, 1))([x, m])
    mx = tf.keras.layers.Lambda(lambda a: tf.where(tf.reduce_sum(a[1], 1) > 0, a[0], 0.0))([mx, m])
    z = [mean, mx] + ([inp_j] if use_jet else [])
    z = tf.keras.layers.Concatenate()(z)
    z = tf.keras.layers.Dense(wz, activation="relu")(z)
    z = tf.keras.layers.Dense(wz // 2, activation="relu")(z)
    out = tf.keras.layers.Dense(1, activation="sigmoid")(z)
    used = ([inp_t] if use_trk else []) + ([inp_h] if use_hit else []) + [inp_m] + ([inp_j] if use_jet else [])
    model = tf.keras.Model(used, out)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="binary_crossentropy")
    return model


def standardize(train, *others):
    mu = train.reshape(-1, train.shape[-1]).mean(0)
    sd = train.reshape(-1, train.shape[-1]).std(0) + 1e-6
    return [(a - mu) / sd for a in (train,) + others]


def main():
    out, f_b, f_l = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    b, l = load(f_b), load(f_l)
    b = {k: v[b["flav"] == 5] for k, v in b.items()}
    l = {k: v[l["flav"] == 0] for k, v in l.items()}
    w = np.concatenate([np.ones(len(b["pt"])), kin_weights(b, l)])
    y = np.concatenate([np.ones(len(b["pt"])), np.zeros(len(l["pt"]))])
    d = {k: np.concatenate([b[k], l[k]]) for k in b}
    d["evt"] = np.concatenate([b["evt"], l["evt"] + 10_000_000])
    fold = (d["evt"] % 2).astype(int)
    jf = jet_features(d)
    summ = summary_features(d["trk"], d["ntrk"])
    jf_q = jf.copy()
    jf_q[:, :8] = np.clip(np.floor(jf_q[:, :8] * 256) / 256, 0, 255 / 256)  # NN scores at L1 precision: ap_ufixed<8,0>
    summ_q = quantize_summary(summ)
    print(f"b jets {int(y.sum())}, light jets {int((1 - y).sum())}, median pixel tracks/jet {np.median(d['ntrk']):.0f}")

    def train_w(m):
        ww = w[m].copy()
        ww[y[m] == 0] *= y[m].sum() / ww[y[m] == 0].sum()
        return ww

    configs = [("NN tagger only", "ng", 0, 0)]
    configs += [("NN + jet summary (BDT)", "summary", 0, BITS_SUMMARY)]
    for k in (1, 2, 4, 8, 16):
        configs.append((f"NN + {k} tracks", "trk", k, k * BITS_TRACK))
    for k in (2, 4, 8, 16):
        configs.append((f"NN + {k} tracks + hits", "trkhit", k, k * (BITS_TRACK + 4 * BITS_HIT)))
    for k in (4, 8, 16):
        configs.append((f"NN + hits of {k} tracks (no fit)", "hit", k, k * 4 * BITS_HIT))
    configs.append(("16 tracks + hits, no NN", "trkhit_nonn", 16, 16 * (BITS_TRACK + 4 * BITS_HIT)))
    configs.append(("NN + jet summary, 8-bit (BDT)", "summary_q", 0, BITS_SUMMARY))
    configs.append(("NN + hits of 16 tracks (no fit), wide", "hitL", 16, 16 * 4 * BITS_HIT))
    only = os.environ.get("CONFIGS")  # names of the configurations to run, e.g. for a quick focused job
    if only:
        configs = [c for c in configs if c[0] in only]  # names contain commas, so match as substrings

    def run(kind, k, frac=1.0):
        """Out-of-sample predictions for one configuration, training on a fraction of each training half."""
        pred = np.zeros(len(y))
        for f in (0, 1):
            tr, te = fold == f, fold != f
            if frac < 1.0:
                keep = np.random.default_rng(100 + f).random(len(y)) < frac
                tr = tr & keep
            if kind == "ng":
                s = d["scores"]
                pred[te] = s[te, 0] / np.clip(s[te, 0] + s[te, 2] + s[te, 3], 1e-6, None)
                continue
            if kind in ("summary", "summary_q"):
                X = np.column_stack([jf, summ]) if kind == "summary" else np.column_stack([jf_q, summ_q])
                clf = HistGradientBoostingClassifier(max_iter=300, max_leaf_nodes=31, random_state=1)
                clf.fit(X[tr], y[tr], sample_weight=train_w(tr))
                pred[te] = clf.predict_proba(X[te])[:, 1]
                continue
            T, H = d["trk"][:, :k], d["hit"][:, :k]
            M = (np.arange(k)[None, :] < d["ntrk"][:, None]).astype(np.float32)
            Ttr, Tte = standardize(T[tr], T[te])
            Htr, Hte = standardize(H[tr], H[te])
            Jtr, Jte = standardize(jf[tr], jf[te])
            Ttr, Tte, Htr, Hte = Ttr * M[tr][..., None], Tte * M[te][..., None], Htr * M[tr][..., None, None], Hte * M[te][..., None, None]
            ut, uh, uj = kind in ("trk", "trkhit", "trkhit_nonn"), kind in ("trkhit", "hit", "hitL", "trkhit_nonn"), kind != "trkhit_nonn"
            model = deepsets(k, T.shape[-1], H.shape[-1], jf.shape[-1], use_trk=ut, use_hit=uh, use_jet=uj, wide=kind == "hitL")

            def feed(Tx, Hx, Mx, Jx):
                return {n: a for n, a, u in [("trk", Tx, ut), ("hit", Hx, uh), ("mask", Mx, True), ("jet", Jx, uj)] if u}
            cb = [tf.keras.callbacks.EarlyStopping(patience=int(os.environ.get("PATIENCE", 8)), restore_best_weights=True)]
            # shuffle: Keras' validation_split takes the last rows, and the arrays are ordered b then light
            perm = np.random.default_rng(f).permutation(int(tr.sum()))
            Xtr = {n: a[perm] for n, a in feed(Ttr, Htr, M[tr], Jtr).items()}
            model.fit(Xtr, y[tr][perm], sample_weight=train_w(tr)[perm], epochs=int(os.environ.get("EPOCHS", 200)), batch_size=256,
                      validation_split=0.2, callbacks=cb, verbose=0)
            pred[te] = model.predict(feed(Tte, Hte, M[te], Jte), batch_size=4096, verbose=0)[:, 0]
        return pred

    def score(pred):
        fpr, tpr, _ = roc_curve(y, pred, sample_weight=w)
        return {"auc": float(roc_auc_score(y, pred, sample_weight=w)),
                "beff_1pct": float(np.interp(0.01, fpr, tpr)), "beff_10pct": float(np.interp(0.10, fpr, tpr))}

    results = []
    for name, kind, k, bits in configs:
        r = {"name": name, "kind": kind, "k": k, "bits_per_jet": bits, **score(run(kind, k))}
        if k:
            r["mean_bits_used"] = float(np.minimum(d["ntrk"], k).mean() * bits / k)
        results.append(r)
        print(f"{name:38s} bits/jet {bits:5d}  AUC {r['auc']:.3f}  b@1% {r['beff_1pct']:.3f}  b@10% {r['beff_10pct']:.3f}", flush=True)

    # learning curve: do the set models (tracks, or hits without the fit) catch up given more training jets?
    curve = []
    lc = [("NN + jet summary (BDT)", "summary", 0), ("NN + 16 tracks", "trk", 16),
          ("NN + hits of 16 tracks (no fit)", "hit", 16), ("NN + hits of 16 tracks (no fit), wide", "hitL", 16)]
    lc = [c for c in lc if any(r["name"] == c[0] for r in results)]
    for frac in [float(x) for x in os.environ.get("LC_FRACS", "0.1,0.25,0.5,1.0").split(",")]:
        n_train = int(0.5 * frac * len(y))
        for name, kind, k in lc:
            r = next((x for x in results if x["name"] == name), None) if frac == 1.0 else None
            sc = {kk: r[kk] for kk in ("auc", "beff_1pct", "beff_10pct")} if r else score(run(kind, k, frac))
            curve.append({"name": name, "frac": frac, "n_train_jets": n_train, **sc})
            print(f"learning curve {name:26s} train jets/half {n_train:6d}  AUC {sc['auc']:.3f}  b@10% {sc['beff_10pct']:.3f}", flush=True)

    meta = {"bits_track": BITS_TRACK, "bits_hit": BITS_HIT, "bits_summary": BITS_SUMMARY, "bits_puppi_jet": BITS_PUPPI_JET,
            "n_b": int(y.sum()), "n_light": int((1 - y).sum()), "median_ntrk": float(np.median(d["ntrk"])),
            "ntrk_quantiles": np.percentile(d["ntrk"], [50, 90, 99]).tolist()}
    json.dump({"meta": meta, "results": results, "learning_curve": curve}, open(os.path.join(out, "budget.json"), "w"), indent=1)

    plot_budget(results, out)


def plot_budget(results, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(16, 6.5))
    colors = {"ng": "#5790fc", "summary": "#964a8b", "trk": "#f89c20", "trkhit": "#e42536", "hit": "#7a21dd", "trkhit_nonn": "#9c9ca1",
              "summary_q": "#c849a9", "hitL": "#3f1d8f"}
    labels = {"ng": "NN tagger only", "summary": "NN + jet summary", "trk": "NN + top-k tracks", "trkhit": "NN + top-k tracks + hits",
              "hit": "NN + hits of top-k tracks (no track fit)", "trkhit_nonn": "pixel only (16 tracks + hits)",
              "summary_q": "NN + jet summary, 8-bit", "hitL": "NN + hits of 16 tracks (no fit), wide net"}
    for ax, key, yl in [(axs[0], "beff_10pct", "b-jet efficiency at 10% light mistag"), (axs[1], "beff_1pct", "b-jet efficiency at 1% light mistag")]:
        for kind in colors:
            rs = [r for r in results if r["kind"] == kind]
            xs = [max(r["bits_per_jet"], 8) for r in rs]
            ax.plot(xs, [r[key] for r in rs], "o-", color=colors[kind], lw=2, ms=7, label=labels[kind])
            for r in rs:
                if r["k"]:
                    ax.annotate(str(r["k"]), (max(r["bits_per_jet"], 8), r[key]), textcoords="offset points", xytext=(4, 4), fontsize=9, color=colors[kind])
        ax.axvline(BITS_PUPPI_JET, color="#888888", ls=":", lw=1.5)
        ax.text(BITS_PUPPI_JET * 0.95, 0.98, "today's NN input\n(16 PUPPI × 64 b)", fontsize=9, color="#666666",
                ha="right", va="top", transform=ax.get_xaxis_transform())
        ax.set_xscale("log"); ax.set_xlabel("extra bits per jet sent to the tagger (8 = none)"); ax.set_ylabel(yl); ax.grid(alpha=0.3)
    handles, labs = axs[0].get_legend_handles_labels()
    fig.legend(handles, labs, fontsize=10, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.08), frameon=False)
    axs[0].set_title("Phase-2 simulation, PU 200 · private work", loc="left", fontsize=11, color="#444444")
    fig.savefig(os.path.join(out, "budget.png"), dpi=130, bbox_inches="tight")



if __name__ == "__main__":
    if sys.argv[1] == "--replot":
        plot_budget(json.load(open(os.path.join(sys.argv[2], "budget.json")))["results"], sys.argv[2])
    else:
        main()

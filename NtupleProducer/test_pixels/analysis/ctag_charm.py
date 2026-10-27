#!/usr/bin/env python3
"""Per-jet L1 c-tagging with a charm-oriented pixel summary (charm_feats.py) on top of the b-oriented 8-number summary.

    python3 ctag_charm.py OUT.json L1EXT_QCD.npz [HLTPIX_QCD.npz] [EXTRA_C_LISTS_GLOB]

Same setup as ctag_compare.py: QCD jets only (c vs light = CvsL, c vs b = CvsB), background reweighted to the c-jet pT,
eta spectrum, HistGradientBoosting BDT trained even -> odd and odd -> even events (every jet gets an out-of-sample
score). Working points: CvsL c-eff at 1% / 10% light mistag, CvsB c-eff at 10% / 30% b mistag.
Rows: L1 NN (today's discriminant), NN only (BDT closure), + old summary (= ctag_compare "L1 + pixel"),
+ old + charm word, the same quantised to the assumed word widths, a single combined 64-bit word, + charm without the
old summary, + the raw lists of the 8 most significant tracks (ceiling of what the lists hold), single charm features
added one at a time (ablation), HLT pixel tracks (reference), and a statistics check training with extra c jets
from EXTRA_C_LISTS_GLOB (e.g. VBF H->cc lists; tested on QCD only).
v2 rows (charm_feats2.py): significances recalibrated (minimum-bias LUT) and the longitudinal IP added (3D significance),
for the b summary and the charm word; their gains are quoted against the old summary as well.
Uncertainties: paired bootstrap of the test jets (BOOT resamples) for the gain of each row over the old summary.
"""
import glob
import json
import os
import sys

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_curve

from charm_feats import CHARM_BITS, CHARM_NAMES, CHARM_WORD, WORD64_BITS, charm_features, quantize_charm, word64
from charm_feats2 import (CHARM2_BITS, CHARM2_NAMES, CHARM2_WORD, WORD64_2_BITS, charm2, quantize_charm2,
                          quantize_summary2, summary2, word64_2)
from train_sets import jet_features, kin_weights, load, quantize_summary, summary_features

MIS = np.logspace(-3.5, 0, 60)
WP = {"CvsL": (0.01, 0.1), "CvsB": (0.1, 0.3)}
BOOT = int(os.environ.get("BOOT", 200))
ABLATE = os.environ.get("ABLATE", "1") == "1"


def feats(d, kind):
    if kind.startswith("v2"):
        return feats2(d, kind)
    jf = jet_features(d)
    sb = summary_features(d["trk"], d["ntrk"])
    ch = charm_features(d["trk"], d["ntrk"], d["eta"], d["pt"])
    if kind == "nn":
        return jf
    if kind == "old":
        return np.column_stack([jf, sb])
    if kind == "old+charm":
        return np.column_stack([jf, sb, ch])
    if kind == "charm":
        return np.column_stack([jf, ch])
    if kind in ("old+charm q", "word64"):
        jq = jf.copy()
        jq[:, :8] = np.clip(np.floor(jq[:, :8] * 256) / 256, 0, 255 / 256)  # NN scores at L1 precision
        if kind == "word64":
            return np.column_stack([jq, word64(sb, ch)])
        return np.column_stack([jq, quantize_summary(sb), quantize_charm(ch)])
    if kind == "lists":
        t = d["trk"][:, :8].copy()
        t[np.arange(8)[None, :] >= d["ntrk"][:, None]] = np.nan  # missing tracks: NaN (native in HistGBT)
        return np.column_stack([jf, sb, ch, t.reshape(len(t), -1)])
    if kind.startswith("old+"):
        return np.column_stack([jf, sb, ch[:, CHARM_NAMES.index(kind[4:])]])
    raise ValueError(kind)


def feats2(d, kind):
    """v2: calibrated transverse + longitudinal IP (charm_feats2.py)."""
    jf = jet_features(d)
    s2 = summary2(d["trk"], d["ntrk"], d["eta"])
    if kind == "v2 sum":
        return np.column_stack([jf, s2])
    thr = 2.0 if kind.endswith("thr2") else 3.0
    c2 = charm2(d["trk"], d["ntrk"], d["eta"], d["pt"], sig_vtx=thr)
    if kind in ("v2 sum+charm", "v2 sum+charm thr2"):
        return np.column_stack([jf, s2, c2])
    if kind in ("v2 q", "v2 word64"):
        jq = jf.copy()
        jq[:, :8] = np.clip(np.floor(jq[:, :8] * 256) / 256, 0, 255 / 256)
        if kind == "v2 word64":
            return np.column_stack([jq, word64_2(s2, c2)])
        return np.column_stack([jq, quantize_summary2(s2), quantize_charm2(c2)])
    if kind == "v2 old+sum+charm":
        return np.column_stack([jf, summary_features(d["trk"], d["ntrk"]), s2, c2])
    if kind == "v2 lists":
        t = d["trk"][:, :8].copy()
        t[np.arange(8)[None, :] >= d["ntrk"][:, None]] = np.nan
        return np.column_stack([jf, s2, c2, t.reshape(len(t), -1)])
    if kind.startswith("v2 sum+"):
        return np.column_stack([jf, s2, c2[:, CHARM2_NAMES.index(kind[7:])]])
    raise ValueError(kind)


def bdt(X, y, w, fold, test, Xx=None, yx=None, wx=None):
    """Out-of-sample scores on `test` jets; (Xx, yx, wx): extra training jets (signal only), used in both folds."""
    pred = np.full(len(y), np.nan)
    for f in (0, 1):
        tr, te = (fold == f) & test, (fold != f) & test
        Xt, yt, wt = X[tr], y[tr], w[tr].copy()
        if Xx is not None:
            Xt, yt, wt = np.concatenate([Xt, Xx]), np.concatenate([yt, yx]), np.concatenate([wt, wx])
        wt[yt == 0] *= yt.sum() / wt[yt == 0].sum()
        clf = HistGradientBoostingClassifier(max_iter=300, max_leaf_nodes=31, random_state=1)
        pred[te] = clf.fit(Xt, yt, sample_weight=wt).predict_proba(X[te])[:, 1]
    return pred


def effs(y, pred, w, task):
    fpr, tpr, _ = roc_curve(y, pred, sample_weight=w)
    return [float(np.interp(m, fpr, tpr)) for m in WP[task]], fpr, tpr


def main():
    out, f_l1 = sys.argv[1], sys.argv[2]
    f_hlt = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else None
    extra_glob = sys.argv[4] if len(sys.argv) > 4 else None
    res = {"meta": {"charm_word": [{"name": n, "bits": b, "lo": r[0], "hi": r[1], "step": r[2]} for n, b, r in CHARM_WORD],
                    "charm_bits": CHARM_BITS, "charm2_bits": CHARM2_BITS, "word64_2_bits": WORD64_2_BITS,
                    "charm2_word": [{"name": n, "bits": b, "lo": r[0], "hi": r[1], "step": r[2]} for n, b, r in CHARM2_WORD], "old_summary_bits": 64, "word64_bits": WORD64_BITS, "boot": BOOT,
                    "inputs": {"l1ext": f_l1, "hltpix": f_hlt, "extra_c": extra_glob}},
           "CvsL": {}, "CvsB": {}}
    q = load(f_l1)
    extra = None
    if extra_glob:
        parts = [load(f) for f in sorted(glob.glob(extra_glob))]
        extra = {k: np.concatenate([p[k] for p in parts]) for k in ("trk", "ntrk", "pt", "eta", "flav", "scores")}
        extra = {k: v[extra["flav"] == 4] for k, v in extra.items()}
        print(f"extra c jets for training: {len(extra['pt'])}", flush=True)
    rng = np.random.default_rng(7)
    for task, bflav in (("CvsL", 0), ("CvsB", 5)):
        c = {k: v[q["flav"] == 4] for k, v in q.items()}
        o = {k: v[q["flav"] == bflav] for k, v in q.items()}
        d = {k: np.concatenate([c[k], o[k]]) for k in c}
        y = np.concatenate([np.ones(len(c["pt"])), np.zeros(len(o["pt"]))])
        w = np.concatenate([np.ones(len(c["pt"])), kin_weights(c, o)])
        fold = d["event"] % 2
        test = np.ones(len(y), bool)
        boots = [rng.integers(0, len(y), len(y)) for _ in range(BOOT)]
        preds = {}
        sc = d["scores"]
        den = sc[:, 1] + (sc[:, 2] + sc[:, 3] if task == "CvsL" else sc[:, 0])
        preds["L1 NN"] = sc[:, 1] / np.maximum(den, 1e-6)
        rows = [("NN only", "nn"), ("L1+pix old summary", "old"), ("L1+pix old + charm", "old+charm"),
                ("L1+pix old + charm, quantised", "old+charm q"), ("L1+pix 64-bit combined word", "word64"),
                ("L1+pix charm only (no old summary)", "charm"), ("L1+pix old + charm + 8 raw tracks", "lists")]
        if ABLATE:
            rows += [(f"L1+pix old + {n}", f"old+{n}") for n in CHARM_NAMES]
        rows += [("v2 L1+pix summary (3D IP)", "v2 sum"), ("v2 L1+pix summary + charm", "v2 sum+charm"),
                 ("v2 L1+pix summary + charm (s3>2 vertex)", "v2 sum+charm thr2"),
                 ("v2 L1+pix summary + charm, quantised", "v2 q"), ("v2 L1+pix 64-bit combined word", "v2 word64"),
                 ("v2 L1+pix old + v2 summary + charm", "v2 old+sum+charm"),
                 ("v2 L1+pix summary + charm + 8 raw tracks", "v2 lists")]
        if ABLATE:
            rows += [(f"v2 L1+pix summary + {n}", f"v2 sum+{n}") for n in CHARM2_NAMES]
        for name, kind in rows:
            preds[name] = bdt(feats(d, kind), y, w, fold, test)
            print(f"{task} {name:40s} done", flush=True)
        if extra is not None:  # extra c jets reweighted to the QCD c-jet pT, eta spectrum
            wx = kin_weights(c, extra)
            for name, kind in (("L1+pix old summary, +extra c train", "old"), ("L1+pix old + charm, +extra c train", "old+charm"),
                               ("v2 L1+pix summary + charm, +extra c train", "v2 sum+charm")):
                preds[name] = bdt(feats(d, kind), y, w, fold, test, feats(extra, kind), np.ones(len(wx)), wx)
                print(f"{task} {name:40s} done", flush=True)
        ref = preds["L1+pix old summary"]
        e_ref_b = np.array([effs(y[b], ref[b], w[b], task)[0] for b in boots])
        for name, p in preds.items():
            (lo, hi), fpr, tpr = effs(y, p, w, task)
            eb = np.array([effs(y[b], p[b], w[b], task)[0] for b in boots])
            r = {f"c_at_{WP[task][0]:g}": lo, f"c_at_{WP[task][1]:g}": hi,
                 "boot_std": eb.std(0).tolist(), "gain_vs_old": [lo - effs(y, ref, w, task)[0][0], hi - effs(y, ref, w, task)[0][1]],
                 "gain_vs_old_boot_std": (eb - e_ref_b).std(0).tolist(),
                 "roc_mistag": MIS.tolist(), "roc_ceff": np.interp(MIS, fpr, tpr).tolist(),
                 "n_c": int(y.sum()), "n_bkg": int((y == 0).sum())}
            res[task][name] = r
            print(f"{task} {name:40s} c-eff @{WP[task][0]:g} {lo:.3f}+-{r['boot_std'][0]:.3f}  @{WP[task][1]:g} {hi:.3f}"
                  f"+-{r['boot_std'][1]:.3f}  gain vs old {r['gain_vs_old'][1]:+.3f}+-{r['gain_vs_old_boot_std'][1]:.3f}", flush=True)
        if f_hlt:
            h = load(f_hlt)
            c = {k: v[h["flav"] == 4] for k, v in h.items() if k != "hit"}
            o = {k: v[h["flav"] == bflav] for k, v in h.items() if k != "hit"}
            dh = {k: np.concatenate([c[k], o[k]]) for k in c}
            yh = np.concatenate([np.ones(len(c["pt"])), np.zeros(len(o["pt"]))])
            wh = np.concatenate([np.ones(len(c["pt"])), kin_weights(c, o)])
            for name, kind in (("HLT pix old summary", "old"), ("HLT pix old + charm", "old+charm")):
                (lo, hi), fpr, tpr = effs(yh, bdt(feats(dh, kind), yh, wh, dh["event"] % 2, np.ones(len(yh), bool)), wh, task)
                res[task][name] = {f"c_at_{WP[task][0]:g}": lo, f"c_at_{WP[task][1]:g}": hi, "roc_mistag": MIS.tolist(),
                                   "roc_ceff": np.interp(MIS, fpr, tpr).tolist(), "n_c": int(yh.sum()), "n_bkg": int((yh == 0).sum())}
                print(f"{task} {name:40s} c-eff @{WP[task][0]:g} {lo:.3f}  @{WP[task][1]:g} {hi:.3f}", flush=True)
            del h, dh
    tmp = out + ".tmp"
    json.dump(res, open(tmp, "w"), indent=1)
    os.replace(tmp, out)


if __name__ == "__main__":
    main()

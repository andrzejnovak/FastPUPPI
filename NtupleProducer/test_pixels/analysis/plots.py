#!/usr/bin/env python3
"""Plots + summary numbers for the L1 pixel-track b-tagging study.

    python3 plots.py OUTDIR HH4b.npz QCD.npz [nano_for_hitmap.root]

Writes PNG/SVG plots and summary.json into OUTDIR.
"""
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_curve, roc_auc_score

plt.style.use(hep.style.CMS)
LABEL = dict(label="Private work", data=False, com=14, rlabel="Phase-2, PU 200")

# categorical palette (colour-blind-safe)
C = {"ng": "#5790fc", "pix": "#f89c20", "comb": "#e42536", "tc": "#964a8b", "b": "#e42536", "l": "#5790fc"}

PT_MIN, PT_MAX, ETA_MAX = 30.0, 300.0, 2.4
PT_BINS = np.array([30, 40, 50, 60, 75, 90, 110, 135, 165, 200, 300])
ETA_BINS = np.array([0, 0.8, 1.5, 2.4])
PIX = ["ipsig1", "ipsig2", "ipsig3", "nTrk", "nSig3", "nSig5", "sumSig", "maxSIP"]
NG = ["score_b", "score_c", "score_uds", "score_g", "score_tau_p", "score_tau_n", "score_mu", "score_e"]
KIN = ["pt", "eta"]


def load(path):
    return {k: v for k, v in np.load(path).items()}


def sel(d, mask):
    return {k: v[mask] for k, v in d.items()}


def cat(a, b):
    return {k: np.concatenate([a[k], b[k]]) for k in a}


def mat(d, cols):
    return np.stack([d[c] for c in cols], axis=1).astype(np.float32)


def ng_b(d):
    return d["score_b"] / np.clip(d["score_b"] + d["score_uds"] + d["score_g"], 1e-6, None)


def save(fig, out, name):
    fig.savefig(os.path.join(out, name + ".png"), dpi=130, bbox_inches="tight")
    plt.close(fig)


def kin_weights(ref, d):
    """Per-jet weights that make d's (pT, |eta|) distribution match ref's."""
    h_ref, _, _ = np.histogram2d(ref["pt"], abs(ref["eta"]), bins=[PT_BINS, ETA_BINS])
    h_d, _, _ = np.histogram2d(d["pt"], abs(d["eta"]), bins=[PT_BINS, ETA_BINS])
    ratio = np.divide(h_ref / h_ref.sum(), h_d / h_d.sum(), out=np.zeros_like(h_ref), where=h_d > 0)
    ip = np.clip(np.digitize(d["pt"], PT_BINS) - 1, 0, len(PT_BINS) - 2)
    ie = np.clip(np.digitize(abs(d["eta"]), ETA_BINS) - 1, 0, len(ETA_BINS) - 2)
    return ratio[ip, ie]


def wquantile(x, w, q):
    o = np.argsort(x)
    c = np.cumsum(w[o]) / w.sum()
    return float(np.interp(q, c, x[o]))


def eff_at(fpr, tpr, target):
    return float(np.interp(target, fpr, tpr))


def main():
    out, f_sig, f_bkg = sys.argv[1:4]
    nano = sys.argv[4] if len(sys.argv) > 4 else None
    os.makedirs(out, exist_ok=True)
    sig, bkg = load(f_sig), load(f_bkg)

    base_s = (sig["pt"] > PT_MIN) & (sig["pt"] < PT_MAX) & (abs(sig["eta"]) < ETA_MAX)
    base_b = (bkg["pt"] > PT_MIN) & (bkg["pt"] < PT_MAX) & (abs(bkg["eta"]) < ETA_MAX)
    bj = sel(sig, base_s & (sig["flav"] == 5))
    lj = sel(bkg, base_b & (bkg["flav"] == 0))
    # light jets reweighted to the b-jet (pT, |eta|) spectrum so kinematics carry no sample information
    bj["w"] = np.ones(len(bj["pt"]))
    lj["w"] = kin_weights(bj, lj)
    summary = {"n_b_jets": int(len(bj["pt"])), "n_light_jets": int(len(lj["pt"])),
               "n_sig_events": int(sig["evt"].max() + 1), "n_bkg_events": int(bkg["evt"].max() + 1)}

    # ---------------- feature distributions
    fig, axs = plt.subplots(1, 3, figsize=(24, 7))
    for ax, (var, bins, xl) in zip(axs, [("ipsig1", np.linspace(-10, 40, 51), "highest track IP significance"),
                                         ("ipsig2", np.linspace(-10, 30, 41), "2nd-highest track IP significance"),
                                         ("nSig3", np.arange(-0.5, 10.5, 1), "tracks with IP significance > 3")]):
        for d, lab, c in [(bj, "b jets (HH→4b)", C["b"]), (lj, "light jets (QCD)", C["l"])]:
            ax.hist(np.clip(d[var], bins[0], bins[-1] - 1e-3), bins=bins, weights=d["w"], histtype="step", lw=2.5, density=True, label=lab, color=c)
        ax.set_xlabel(xl); ax.set_ylabel("a.u."); ax.set_yscale("log"); ax.legend(fontsize=18)
    hep.cms.label(ax=axs[0], **LABEL)
    save(fig, out, "jet_pixel_features")

    fig, ax = plt.subplots(figsize=(9, 7))
    bins = np.linspace(0, 1, 41)
    for d, lab, c in [(bj, "b jets (HH→4b)", C["b"]), (lj, "light jets (QCD)", C["l"])]:
        ax.hist(ng_b(d), bins=bins, weights=d["w"], histtype="step", lw=2.5, density=True, label=lab, color=c)
    ax.set_xlabel("L1 NN tagger  b / (b + uds + g)"); ax.set_ylabel("a.u."); ax.set_yscale("log"); ax.legend(fontsize=18)
    hep.cms.label(ax=ax, **LABEL)
    save(fig, out, "jet_ng_score")

    # ---------------- classifiers (train on even events, evaluate on odd events)
    allj = cat(bj, lj)
    y = np.concatenate([np.ones(len(bj["pt"])), np.zeros(len(lj["pt"]))])
    train = (allj["evt"] % 2) == 0
    test = ~train
    models = {}
    for name, cols in [("pix", PIX + KIN), ("comb", NG + PIX + KIN), ("ngbdt", NG + KIN)]:
        clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1, max_leaf_nodes=31, random_state=1)
        clf.fit(mat(allj, cols)[train], y[train], sample_weight=allj["w"][train] / allj["w"][train][y[train] == 0].mean() * (y[train] == 0) + (y[train] == 1))
        models[name] = clf.predict_proba(mat(allj, cols)[test])[:, 1]
    yt = y[test]
    tst = sel(allj, test)
    wt = tst["w"]
    scores = {
        "L1 NN tagger (b/(b+uds+g))": (ng_b(tst), C["ng"], "-"),
        "L1 NN scores, BDT (same inputs, reference)": (models["ngbdt"], C["ng"], ":"),
        "Pixel tracks only (2nd IP sig.)": (tst["ipsig2"], C["tc"], "--"),
        "Pixel tracks only (BDT)": (models["pix"], C["pix"], "-"),
        "L1 NN scores + pixel tracks (BDT)": (models["comb"], C["comb"], "-"),
    }
    fig, ax = plt.subplots(figsize=(10, 9))
    summary["roc"] = {}
    for lab, (s, c, ls) in scores.items():
        fpr, tpr, _ = roc_curve(yt, s, sample_weight=wt)
        auc = roc_auc_score(yt, s, sample_weight=wt)
        ax.plot(tpr, np.clip(fpr, 1e-5, 1), color=c, ls=ls, lw=2.5, label=f"{lab}  AUC={auc:.3f}")
        summary["roc"][lab] = {"auc": float(auc),
                               "beff_at_1pct": eff_at(fpr, tpr, 0.01), "beff_at_10pct": eff_at(fpr, tpr, 0.10)}
    ax.set_yscale("log"); ax.set_ylim(1e-3, 1); ax.set_xlim(0, 1)
    ax.set_xlabel("b-jet efficiency"); ax.set_ylabel("light-jet mistag rate"); ax.grid(alpha=0.3)
    ax.legend(fontsize=14, loc="upper left")
    ax.text(0.98, 0.02, f"L1 jets {PT_MIN:.0f}<$p_T$<{PT_MAX:.0f} GeV, |η|<{ETA_MAX}\nlight jets reweighted to b-jet $p_T$, |η|", transform=ax.transAxes, ha="right", fontsize=15)
    hep.cms.label(ax=ax, **LABEL)
    save(fig, out, "roc")

    # ROC per pT bin: NN alone vs NN + pixel
    ptbins = [(30, 60), (60, 100), (100, 300)]
    fig, axs = plt.subplots(1, 3, figsize=(27, 8), sharey=True)
    summary["roc_ptbins"] = {}
    for ax, (lo, hi) in zip(axs, ptbins):
        m = (tst["pt"] >= lo) & (tst["pt"] < hi)
        res = {}
        for lab, s, c in [("L1 NN tagger", ng_b(tst), C["ng"]), ("pixel only (BDT)", models["pix"], C["pix"]),
                          ("L1 NN + pixel (BDT)", models["comb"], C["comb"])]:
            fpr, tpr, _ = roc_curve(yt[m], s[m], sample_weight=wt[m])
            ax.plot(tpr, np.clip(fpr, 1e-5, 1), color=c, lw=2.5, label=lab)
            res[lab] = {"beff_at_1pct": eff_at(fpr, tpr, 0.01), "beff_at_10pct": eff_at(fpr, tpr, 0.10),
                        "n_b": int(yt[m].sum()), "n_l": int((1 - yt[m]).sum())}
        summary["roc_ptbins"][f"{lo}-{hi}"] = res
        ax.set_yscale("log"); ax.set_ylim(1e-3, 1); ax.set_xlim(0, 1); ax.grid(alpha=0.3)
        ax.set_xlabel("b-jet efficiency")
        ax.set_title(f"{lo:.0f} < $p_T$ < {hi:.0f} GeV", fontsize=20)
        ax.legend(fontsize=16, loc="upper left")
    axs[0].set_ylabel("light-jet mistag rate")
    hep.cms.label(ax=axs[0], **LABEL)
    save(fig, out, "roc_ptbins")

    # ---------------- HH->4b napkin math: >= N tags among the 4 leading L1 jets, per-jet mistag fixed
    # thresholds set on the QCD light-jet test sample, applied to all HH4b jets (odd events)
    sig_all = sel(sig, base_s & ((sig["evt"] % 2) == 1))
    preds = {}
    for name, cols in [("comb", NG + PIX + KIN), ("pix", PIX + KIN)]:
        clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1, max_leaf_nodes=31, random_state=1)
        clf.fit(mat(allj, cols)[train], y[train], sample_weight=allj["w"][train] / allj["w"][train][y[train] == 0].mean() * (y[train] == 0) + (y[train] == 1))
        preds[name] = (clf, cols)
    l_test = sel(lj, (lj["evt"] % 2) == 1)
    disc_sig = {"L1 NN tagger": ng_b(sig_all), "L1 NN + pixel": preds["comb"][0].predict_proba(mat(sig_all, preds["comb"][1]))[:, 1]}
    disc_l = {"L1 NN tagger": ng_b(l_test), "L1 NN + pixel": preds["comb"][0].predict_proba(mat(l_test, preds["comb"][1]))[:, 1]}
    summary["hh4b"] = {}
    fig, ax = plt.subplots(figsize=(10, 8))
    mistags = np.array([0.003, 0.01, 0.02, 0.05, 0.1, 0.2])
    for lab, c in [("L1 NN tagger", C["ng"]), ("L1 NN + pixel", C["comb"])]:
        effs3, effs4 = [], []
        for mt in mistags:
            thr = wquantile(disc_l[lab], l_test["w"], 1 - mt)
            tagged = disc_sig[lab] > thr
            # 4 leading jets per event (jets are pT ordered within the event)
            evts = sig_all["evt"]
            order = np.lexsort((-sig_all["pt"], evts))
            ev_sorted, tag_sorted = evts[order], tagged[order]
            first = np.r_[True, ev_sorted[1:] != ev_sorted[:-1]]
            rank = np.arange(len(ev_sorted)) - np.maximum.accumulate(np.where(first, np.arange(len(ev_sorted)), 0))
            lead = rank < 4
            ntag = np.bincount(ev_sorted[lead], weights=tag_sorted[lead].astype(float), minlength=evts.max() + 1)
            nev = len(np.unique(sig["evt"][(sig["evt"] % 2) == 1]))
            effs3.append(float((ntag >= 3).sum() / nev))
            effs4.append(float((ntag >= 4).sum() / nev))
        ax.plot(mistags, effs3, "o-", color=c, lw=2.5, label=f"{lab}: ≥3 b tags")
        ax.plot(mistags, effs4, "s--", color=c, lw=2.5, label=f"{lab}: 4 b tags")
        summary["hh4b"][lab] = {"mistag": mistags.tolist(), "eff_ge3": effs3, "eff_4": effs4}
    ax.set_xscale("log"); ax.set_xlabel("per-jet light mistag rate (working point)")
    ax.set_ylabel("HH→4b event fraction"); ax.grid(alpha=0.3); ax.legend(fontsize=16)
    ax.text(0.02, 0.97, f"4 leading L1 jets, $p_T$>{PT_MIN:.0f} GeV, |η|<{ETA_MAX}", transform=ax.transAxes, va="top", fontsize=15)
    hep.cms.label(ax=ax, **LABEL)
    save(fig, out, "hh4b_event_eff")

    # ---------------- hit map from one ntuple
    if nano:
        import uproot
        h = uproot.open(nano)["Events"].arrays(["PixelHits_x", "PixelHits_y", "PixelHits_z"], entry_stop=5, library="np")
        x, yy, z = (np.concatenate(h[k]) for k in ["PixelHits_x", "PixelHits_y", "PixelHits_z"])
        r = np.hypot(x, yy)
        fig, axs = plt.subplots(1, 2, figsize=(22, 8), gridspec_kw={"width_ratios": [2.2, 1]})
        axs[0].scatter(z, r, s=0.3, alpha=0.4, color="#3f90da", rasterized=True)
        axs[0].set_xlabel("z [cm]"); axs[0].set_ylabel("r [cm]")
        axs[1].scatter(x, yy, s=0.3, alpha=0.4, color="#3f90da", rasterized=True)
        axs[1].set_xlabel("x [cm]"); axs[1].set_ylabel("y [cm]"); axs[1].set_aspect("equal")
        hep.cms.label(ax=axs[0], **LABEL)
        save(fig, out, "hit_map")

    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()

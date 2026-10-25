#!/usr/bin/env python3
"""Direct test: HH->4b L1 seed efficiency against measured minimum-bias rate, with real pixel taggers.

    python3 direct_rate.py OUT.json HH4B_GLOB MBSEL_GLOB LISTS_HH LISTS_QCD LISTS_MB

Inputs: extended ntuples for HH->4b and for the targeted minimum-bias sample (events with official L1 HT > 90 GeV,
23411 of 654520), and per-jet pixel lists (make_lists.py with JET_PTMIN=15) for HH->4b, QCD and that minimum bias.
Seeds: HT + sum over the 4 leading jets (pT > 15, |eta| < 2.4) of a per-jet b score, with the score from
  NN       : today's L1 NN, b/(b+uds+g)
  pixel    : BDT on NN scores + jet pT, eta + 8-number pixel summary (all pixel tracks)
  pixel>2  : same with only pixel tracks above 2 GeV (proxy for L1 tracks extended into the pixels)
Working points are chosen on even events (HH and minimum bias) and evaluated on odd events. Rates use only
HT cuts >= 100 GeV, safely above the 90 GeV pre-selection. Also: gain on top of the planned menu seeds
(QuadJet70_55_40_40 and PuppiHT400, PuppiHT450; online thresholds from the CMSSW menu scalings) at fixed added rate.
"""
import glob
import json
import os
import sys

import awkward as ak
import numpy as np
import uproot
from sklearn.ensemble import HistGradientBoostingClassifier

from pt2_test import keep_pt
from train_sets import jet_features, kin_weights, load, summary_features

MB_TOTAL = int(os.environ.get("MB_TOTAL", 654520))  # all minimum-bias events the selected ones were drawn from
BX_KHZ = 2760 * 11.245
HT_MIN = float(os.environ.get("HT_MIN", 100))  # lowest HT cut scanned: where the minimum-bias preselection is complete
RATES = (5.0, 10.0, 14.0, 20.0)
ADDED = (2.5, 5.0, 10.0)
QUAD_BARREL, QUAD_ENDCAP, HT_QUAD, HT_ALONE = (41.1, 29.4, 25.0, 25.0), (32.7, 25.0, 25.0, 25.0), 316.3, 361.0
BR = ["luminosityBlock", "event", "L1NGJets_pt", "L1NGJets_eta", "L1NGJets_score_b", "L1NGJets_score_uds",
      "L1NGJets_score_g", "GenJets_pt", "GenJets_eta", "GenJets_hadronFlavour"]


def events(pat):
    """pat: one glob, or several separated by commas."""
    files = [f for p in pat.split(",") for f in sorted(glob.glob(p))]
    a = ak.concatenate([uproot.open(f)["Events"].arrays(filter_name=BR) for f in files])
    pt, eta = a.L1NGJets_pt, a.L1NGJets_eta
    acc = abs(eta) < 2.4
    ht = ak.to_numpy(ak.sum(pt[acc & (pt > 30)], axis=1))
    idx = ak.local_index(pt)
    sel = acc & (pt > 15)
    order = ak.argsort(pt[sel], ascending=False)
    lead = idx[sel][order][:, :4]
    nn = a.L1NGJets_score_b / np.maximum(a.L1NGJets_score_b + a.L1NGJets_score_uds + a.L1NGJets_score_g, 1e-6)
    # planned menu: k-th leading jet in |eta| < 2.4 above the k-th threshold of its region
    jsort = ak.argsort(pt[acc], ascending=False)
    jpt, jeta = ak.pad_none(pt[acc][jsort], 4, clip=True), ak.pad_none(eta[acc][jsort], 4, clip=True)
    quad = np.ones(len(ht), bool)
    for k in range(4):
        p, e = ak.to_numpy(ak.fill_none(jpt[:, k], 0.0)), ak.to_numpy(ak.fill_none(jeta[:, k], 0.0))
        quad &= p > np.where(abs(e) < 1.5, QUAD_BARREL[k], QUAD_ENDCAP[k])
    gen = (a.GenJets_hadronFlavour == 5) & (a.GenJets_pt > 30) & (abs(a.GenJets_eta) < 2.4)
    return {"lumi": ak.to_numpy(a.luminosityBlock), "event": ak.to_numpy(a.event), "ht": ht, "lead": lead,
            "nn_sum": ak.to_numpy(ak.sum(nn[lead], axis=1)), "menu": (quad & (ht > HT_QUAD)) | (ht > HT_ALONE),
            "fid": ak.to_numpy(ak.sum(gen, axis=1)) >= 4}


def jet_scores(ev, lists, scores):
    """Sum of per-jet scores over each event's 4 leading jets, joined by (lumi, event, jet index)."""
    key = {(l, e, j): s for l, e, j, s in zip(lists["lumi"], lists["event"], lists["jidx"], scores)}
    out = np.zeros(len(ev["ht"]))
    for i, (l, e, lead) in enumerate(zip(ev["lumi"], ev["event"], ak.to_list(ev["lead"]))):
        out[i] = sum(key.get((l, e, j), 0.0) for j in lead)
    return out


def best(sig_s, sig_ht, sig_ok, mb_s, mb_ht, mb_w, target, base_sig=None, base_mb=None):
    """(HT cut, score cut) maximising signal efficiency with rate (or added rate on top of a base seed) <= target."""
    best_ = None
    s_grid = np.unique(np.quantile(np.concatenate([sig_s, mb_s]), np.linspace(0, 0.995, 150)))
    base_rate = (mb_w * base_mb).sum() if base_mb is not None else 0.0
    for h in np.arange(HT_MIN, 600, 10):
        for s in s_grid:
            p_mb = (mb_ht > h) & (mb_s > s)
            if base_mb is not None:
                p_mb = p_mb | base_mb
            if (mb_w * p_mb).sum() - base_rate > target:
                continue
            p_sig = (sig_ht > h) & (sig_s > s)
            if base_sig is not None:
                p_sig = p_sig | base_sig
            eff = (p_sig & sig_ok).sum() / sig_ok.sum()
            if best_ is None or eff > best_[0]:
                best_ = (eff, h, s)
            break  # lowest passing score cut at this HT is the best one
    return best_


def main():
    out, hh_pat, mb_pat, f_hh, f_qcd, f_mb = sys.argv[1:7]
    hh, mb = events(hh_pat), events(mb_pat)
    print(f"HH4b events {len(hh['ht'])} (fiducial {hh['fid'].sum()}), minimum-bias selected events {len(mb['ht'])}", flush=True)
    lh, lq = load(f_hh), load(f_qcd)
    parts = [load(f) for f in f_mb.split(",")]
    lm = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]} if len(parts) > 1 else parts[0]

    # per-jet pixel taggers, trained on even events of HH b vs QCD light jets
    b = {k: v[(lh["flav"] == 5) & (lh["event"] % 2 == 0)] for k, v in lh.items()}
    l = {k: v[(lq["flav"] == 0) & (lq["event"] % 2 == 0)] for k, v in lq.items()}
    tr = {k: np.concatenate([b[k], l[k]]) for k in b}
    y = np.concatenate([np.ones(len(b["pt"])), np.zeros(len(l["pt"]))])
    w = np.concatenate([np.ones(len(b["pt"])), kin_weights(b, l)])
    w[y == 0] *= y.sum() / w[y == 0].sum()
    per_jet = {}
    for name, ptmin in (("pixel", 0.0), ("pixel>2", 2.0)):
        feats = lambda d: np.column_stack([jet_features(d), summary_features(*keep_pt(d, ptmin))])
        clf = HistGradientBoostingClassifier(max_iter=300, max_leaf_nodes=31, random_state=1).fit(feats(tr), y, sample_weight=w)
        per_jet[name] = (clf.predict_proba(feats(lh))[:, 1], clf.predict_proba(feats(lm))[:, 1])
    sums = {"NN": (hh["nn_sum"], mb["nn_sum"])}
    for name, (s_hh, s_mb) in per_jet.items():
        sums[name] = (jet_scores(hh, lh, s_hh), jet_scores(mb, lm, s_mb))

    ev_hh, ev_mb = hh["event"] % 2 == 0, mb["event"] % 2 == 0
    w_fold = lambda m: len(mb["ht"]) / MB_TOTAL * BX_KHZ / m.sum()  # rate per minimum-bias event in a fold
    res = {"n_hh": int(len(hh["ht"])), "n_hh_fid": int(hh["fid"].sum()), "n_mb_sel": int(len(mb["ht"])),
           "menu": {"rate_khz_odd": float(mb["menu"][~ev_mb].sum() * w_fold(~ev_mb)),
                    "eff_odd": float((hh["menu"] & hh["fid"])[~ev_hh].sum() / (hh["fid"] & ~ev_hh).sum())},
           "standalone": {}, "on_top_of_menu": {}}
    flags = {"lumi": hh["lumi"], "event": hh["event"], "fid": hh["fid"], "odd": ~ev_hh, "menu": hh["menu"]}
    print("planned menu alone:", json.dumps(res["menu"]), flush=True)
    for tag, (s_hh, s_mb) in sums.items():
        for r in RATES:
            e, h, s = best(s_hh[ev_hh], hh["ht"][ev_hh], hh["fid"][ev_hh], s_mb[ev_mb], mb["ht"][ev_mb],
                           np.full(ev_mb.sum(), w_fold(ev_mb)), r)
            p_hh, p_mb = (hh["ht"] > h) & (s_hh > s), (mb["ht"] > h) & (s_mb > s)
            row = {"ht_cut": float(h), "score_cut": float(s), "eff_train": float(e),
                   "eff_odd": float((p_hh & hh["fid"])[~ev_hh].sum() / (hh["fid"] & ~ev_hh).sum()),
                   "rate_khz_odd": float(p_mb[~ev_mb].sum() * w_fold(~ev_mb)), "n_mb_pass_odd": int(p_mb[~ev_mb].sum())}
            res["standalone"].setdefault(tag, {})[r] = row
            flags[f"{tag}_alone_{r:g}"] = p_hh
            print(f"{tag:8s} {r:5.1f} kHz: HT>{h:.0f} score>{s:.2f}  eff(odd) {row['eff_odd']:.3f}  rate(odd) {row['rate_khz_odd']:.1f} kHz "
                  f"({row['n_mb_pass_odd']} events)", flush=True)
        for dr in ADDED:
            e, h, s = best(s_hh[ev_hh], hh["ht"][ev_hh], hh["fid"][ev_hh], s_mb[ev_mb], mb["ht"][ev_mb],
                           np.full(ev_mb.sum(), w_fold(ev_mb)), dr, hh["menu"][ev_hh], mb["menu"][ev_mb])
            p_hh = ((hh["ht"] > h) & (s_hh > s)) | hh["menu"]
            p_mb = ((mb["ht"] > h) & (s_mb > s)) | mb["menu"]
            row = {"ht_cut": float(h), "score_cut": float(s),
                   "eff_odd": float((p_hh & hh["fid"])[~ev_hh].sum() / (hh["fid"] & ~ev_hh).sum()),
                   "added_rate_khz_odd": float((p_mb[~ev_mb].sum() - mb["menu"][~ev_mb].sum()) * w_fold(~ev_mb))}
            res["on_top_of_menu"].setdefault(tag, {})[dr] = row
            flags[f"{tag}_menu_{dr:g}"] = p_hh
            print(f"{tag:8s} menu + {dr:4.1f} kHz: eff(odd) {row['eff_odd']:.3f}  added rate(odd) {row['added_rate_khz_odd']:.1f} kHz", flush=True)
    json.dump(res, open(out, "w"), indent=1)
    np.savez(out.replace(".json", "_flags.npz"), **flags)  # per-event HH->4b decisions, for the kappa_lambda split


if __name__ == "__main__":
    main()

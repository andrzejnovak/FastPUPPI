#!/usr/bin/env python3
"""Efficiency vs L1 rate curves for HH->4b seeds with different per-jet b taggers, for the summary page.

    python3 direct_curves.py OUT.json OUT_FLAGS.npz HH4B_GLOB MBSEL_GLOBS OFFLINE_FLAGS.npz \
        HLT_LISTS(hh,qcd,mb1,mb2) L1EXT_LISTS(hh,qcd,mb1,mb2)
Taggers (per-jet b score, summed over the 4 leading jets as in direct_rate.py):
  NN          today's L1 NN, b/(b+uds+g)                      (baseline, no pixel information)
  HLT pixel   BDT on NN scores + pixel summary from HLT pixel tracks
  L1 pixel    BDT on NN scores + pixel summary from L1 tracks extended into the pixel layers (l1ext.py)
  perfect     1 for jets matched to a generator b jet, else 0   (ceiling)
Seeds: HT + score sum; thresholds maximise the generator-fiducial efficiency on even events at each rate, evaluated
on odd events, standalone and on top of the planned menu. Efficiencies for three event sets: all, generator
fiducial, offline 4b + 3b (offline_sel.py, b-response corrected). Rates from 2.0M minimum-bias events
(env MB_TOTAL, HT_MIN as in direct_rate.py). Per-event decisions at each rate point are saved for the m_HH plots.
"""
import json
import sys

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

import direct_rate as D
from train_sets import jet_features, kin_weights, load, pixel_summary

STANDALONE = (2.0, 3.0, 5.0, 7.5, 10.0, 14.0, 20.0, 30.0)
ADDED = (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 7.5, 10.0, 15.0)


def load_mb(spec):
    parts = [load(f) for f in spec.split(",")]
    return {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}


def pixel_tagger(fh, fq, fmb, l1=False):
    lh, lq, lm = load(fh), load(fq), load_mb(fmb)
    b = {k: v[(lh["flav"] == 5) & (lh["event"] % 2 == 0)] for k, v in lh.items()}
    l = {k: v[(lq["flav"] == 0) & (lq["event"] % 2 == 0)] for k, v in lq.items()}
    tr = {k: np.concatenate([b[k], l[k]]) for k in b}
    y = np.concatenate([np.ones(len(b["pt"])), np.zeros(len(l["pt"]))])
    w = np.concatenate([np.ones(len(b["pt"])), kin_weights(b, l)])
    w[y == 0] *= y.sum() / w[y == 0].sum()
    feats = lambda d: np.column_stack([jet_features(d), pixel_summary(d, l1)])
    clf = HistGradientBoostingClassifier(max_iter=300, max_leaf_nodes=31, random_state=1).fit(feats(tr), y, sample_weight=w)
    return lh, lm, clf.predict_proba(feats(lh))[:, 1], clf.predict_proba(feats(lm))[:, 1]


def main():
    out, out_flags, hh_pat, mb_pat, off_path = sys.argv[1:6]
    hlt, l1 = sys.argv[6].split(":"), sys.argv[7].split(":")
    hh, mb = D.events(hh_pat), D.events(mb_pat)
    o = np.load(off_path)
    opos = {(l, e): i for i, (l, e) in enumerate(zip(o["lumi"], o["event"]))}
    oi = np.array([opos.get((l, e), -1) for l, e in zip(hh["lumi"], hh["event"])])
    offsel = (oi >= 0) & np.where(oi >= 0, (o["resolved_4b"] | o["3b_mass"])[np.maximum(oi, 0)], False)
    sets = {"all": np.ones(len(hh["ht"]), bool), "fiducial": hh["fid"], "offline_4b3b": offsel}

    sums = {"NN": (hh["nn_sum"], mb["nn_sum"])}
    for name, (fh, fq, fm1, fm2) in (("HLT pixel", hlt), ("L1 pixel", l1)):
        lh, lm, s_hh, s_mb = pixel_tagger(fh, fq, f"{fm1},{fm2}", l1=name == "L1 pixel")
        sums[name] = (D.jet_scores(hh, lh, s_hh), D.jet_scores(mb, lm, s_mb))
        if name == "L1 pixel":  # perfect tagger from the same jets (generator flavour; unmatched pileup jets = not b)
            sums["perfect"] = (D.jet_scores(hh, lh, (lh["flav"] == 5).astype(float)),
                               D.jet_scores(mb, lm, (lm["flav"] == 5).astype(float)))
        print(f"{name} tagger trained", flush=True)

    ev_hh, ev_mb = hh["event"] % 2 == 0, mb["event"] % 2 == 0
    w_fold = lambda m: len(mb["ht"]) / D.MB_TOTAL * D.BX_KHZ / m.sum()
    eff = lambda p: {k: float((p & m & ~ev_hh).sum() / (m & ~ev_hh).sum()) for k, m in sets.items()}
    res = {"n_odd": {k: int((m & ~ev_hh).sum()) for k, m in sets.items()},
           "menu": {"rate_khz": float(mb["menu"][~ev_mb].sum() * w_fold(~ev_mb)), "eff": eff(hh["menu"])},
           "standalone": {}, "on_top_of_menu": {}}
    flags = {"lumi": hh["lumi"], "event": hh["event"], "odd": ~ev_hh, "menu": hh["menu"], **sets}
    print("menu:", json.dumps(res["menu"]), flush=True)
    wmb = np.full(ev_mb.sum(), w_fold(ev_mb))
    for tag, (s_hh, s_mb) in sums.items():
        for r in STANDALONE:
            e, h, s = D.best(s_hh[ev_hh], hh["ht"][ev_hh], hh["fid"][ev_hh], s_mb[ev_mb], mb["ht"][ev_mb], wmb, r)
            p_hh, p_mb = (hh["ht"] > h) & (s_hh > s), (mb["ht"] > h) & (s_mb > s)
            res["standalone"].setdefault(tag, []).append(
                {"target_khz": r, "ht_cut": float(h), "score_cut": float(s),
                 "rate_khz": float(p_mb[~ev_mb].sum() * w_fold(~ev_mb)), "eff": eff(p_hh)})
            flags[f"{tag}|alone|{r:g}"] = p_hh
        for dr in ADDED:
            e, h, s = D.best(s_hh[ev_hh], hh["ht"][ev_hh], hh["fid"][ev_hh], s_mb[ev_mb], mb["ht"][ev_mb], wmb, dr,
                             hh["menu"][ev_hh], mb["menu"][ev_mb])
            p_hh = ((hh["ht"] > h) & (s_hh > s)) | hh["menu"]
            p_mb = ((mb["ht"] > h) & (s_mb > s)) | mb["menu"]
            row = {"target_khz": dr, "ht_cut": float(h), "score_cut": float(s),
                   "added_rate_khz": float((p_mb[~ev_mb].sum() - mb["menu"][~ev_mb].sum()) * w_fold(~ev_mb)), "eff": eff(p_hh)}
            res["on_top_of_menu"].setdefault(tag, []).append(row)
            flags[f"{tag}|menu|{dr:g}"] = p_hh
            print(f"{tag:10s} menu + {dr:4.1f} kHz (measured {row['added_rate_khz']:.1f}): "
                  + " ".join(f"{k} {v:.3f}" for k, v in row["eff"].items()), flush=True)
    json.dump(res, open(out, "w"), indent=1)
    np.savez_compressed(out_flags, **flags)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Per-event and per-jet inputs for the thesis-style plots: the (score sum, HT) seed plane and jet-level efficiencies.

    python3 seed_plane.py OUT.npz HH4B_GLOB MBSEL_GLOBS HLT_LISTS(hh,qcd,mb1,mb2) L1EXT_LISTS(hh,qcd,mb1,mb2)
Same taggers and training as direct_curves.py (pixel BDTs trained on even events of HH b jets vs QCD light jets).
Writes, for HH->4b and minimum bias: lumi, event, HT, planned-menu flag and the 4-leading-jet score sums (NN, HLT pixel,
L1 pixel, perfect); and per jet (HH lists for b, QCD lists for light; odd events only, out of sample): pT, eta,
flavour and each tagger's score.
"""
import sys

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

import direct_rate as D
from direct_curves import load_mb
from train_sets import jet_features, kin_weights, load, pixel_summary


def nn_score(d):
    sc = d["scores"]
    return sc[:, 0] / np.maximum(sc[:, 0] + sc[:, 2] + sc[:, 3], 1e-6)


def tagger(fh, fq, fmb, l1=False):
    lh, lq, lm = load(fh), load(fq), load_mb(fmb)
    b = {k: v[(lh["flav"] == 5) & (lh["event"] % 2 == 0)] for k, v in lh.items()}
    l = {k: v[(lq["flav"] == 0) & (lq["event"] % 2 == 0)] for k, v in lq.items()}
    tr = {k: np.concatenate([b[k], l[k]]) for k in b}
    y = np.concatenate([np.ones(len(b["pt"])), np.zeros(len(l["pt"]))])
    w = np.concatenate([np.ones(len(b["pt"])), kin_weights(b, l)])
    w[y == 0] *= y.sum() / w[y == 0].sum()
    feats = lambda d: np.column_stack([jet_features(d), pixel_summary(d, l1)])
    clf = HistGradientBoostingClassifier(max_iter=300, max_leaf_nodes=31, random_state=1).fit(feats(tr), y, sample_weight=w)
    return lh, lq, lm, (clf.predict_proba(feats(d))[:, 1] for d in (lh, lq, lm))


def main():
    out, hh_pat, mb_pat = sys.argv[1:4]
    hlt, l1 = sys.argv[4].split(":"), sys.argv[5].split(":")
    hh, mb = D.events(hh_pat), D.events(mb_pat)
    res = {f"{p}_{k}": d[k] for p, d in (("hh", hh), ("mb", mb)) for k in ("lumi", "event", "ht", "menu")}
    res["hh_nn"], res["mb_nn"] = hh["nn_sum"], mb["nn_sum"]
    for name, key, (fh, fq, fm1, fm2) in (("HLT pixel", "hlt", hlt), ("L1 pixel", "l1", l1)):
        lh, lq, lm, (s_h, s_q, s_m) = tagger(fh, fq, f"{fm1},{fm2}", l1=key == "l1")
        res[f"hh_{key}"], res[f"mb_{key}"] = D.jet_scores(hh, lh, s_h), D.jet_scores(mb, lm, s_m)
        if key == "l1":
            res["hh_perfect"] = D.jet_scores(hh, lh, (lh["flav"] == 5).astype(float))
            res["mb_perfect"] = D.jet_scores(mb, lm, (lm["flav"] == 5).astype(float))
            # per-jet, odd events: b jets from HH, light jets from QCD (the NN score comes with the same lists)
            for tag, d, s in (("b", lh, s_h), ("light", lq, s_q)):
                m = (d["event"] % 2 == 1) & (d["flav"] == (5 if tag == "b" else 0))
                res.update({f"jet_{tag}_pt": d["pt"][m], f"jet_{tag}_eta": d["eta"][m], f"jet_{tag}_l1": s[m],
                            f"jet_{tag}_nn": nn_score(d)[m]})
        else:
            for tag, d, s in (("b", lh, s_h), ("light", lq, s_q)):
                m = (d["event"] % 2 == 1) & (d["flav"] == (5 if tag == "b" else 0))
                res[f"jet_{tag}_hlt"] = s[m]
        print(f"{name} tagger done", flush=True)
    np.savez_compressed(out, **res)
    print("wrote", out, {k: v.shape for k, v in res.items()})


if __name__ == "__main__":
    main()

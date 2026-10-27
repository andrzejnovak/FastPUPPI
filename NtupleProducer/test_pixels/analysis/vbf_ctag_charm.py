#!/usr/bin/env python3
"""VBF H -> cc L1 seed (vbf_ctag.py) with the charm-oriented pixel summary (charm_feats.py) in the per-jet c score.

    python3 vbf_ctag_charm.py OUT.json SIG_GLOB SIG_LISTS MB_GLOBS MB_LISTS QCD_LISTS [FLAV]
Same seed, menu, working-point choice (even events) and quoted efficiency (odd events) as vbf_ctag.py, whose helpers
are imported unchanged. Per-jet scores (c vs rest BDTs trained on QCD jets):
  none, NN       as in vbf_ctag.py
  pixel          NN scores, pT, eta + old 8-number pixel summary (= vbf_ctag.py "pixel")
  pixel+charm    + the charm word (charm_feats.CHARM_WORD)
  word64         NN scores + the single 64-bit combined b + charm word (charm_feats.word64), quantised
  v2             NN scores + v2 summary + v2 charm word (charm_feats2.py: calibrated 3D impact parameters)
  v2_word64      NN scores + the v2 single 64-bit word, quantised
TAGS (env, separated by ',' or ':') restricts the list.
"""
import itertools
import json
import os
import sys

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

from charm_feats import charm_features, word64
from charm_feats2 import charm2, summary2, word64_2
from train_sets import jet_features, kin_weights, load, summary_features
from vbf_ctag import ADDED, BX_KHZ, MB_TOTAL, MJJ, events, merged, nn_score, second_score


def feats(d, kind):
    jf = jet_features(d)
    if kind.startswith("v2"):  # calibrated transverse + longitudinal IP summaries (charm_feats2.py)
        s2 = summary2(d["trk"], d["ntrk"], d["eta"])
        c2 = charm2(d["trk"], d["ntrk"], d["eta"], d["pt"])
        if kind == "v2":
            return np.column_stack([jf, s2, c2])
        if kind == "v2_word64":
            jq = jf.copy()
            jq[:, :8] = np.clip(np.floor(jq[:, :8] * 256) / 256, 0, 255 / 256)
            return np.column_stack([jq, word64_2(s2, c2)])
    sb = summary_features(d["trk"], d["ntrk"])
    if kind == "pixel":
        return np.column_stack([jf, sb])
    ch = charm_features(d["trk"], d["ntrk"], d["eta"], d["pt"])
    if kind == "pixel+charm":
        return np.column_stack([jf, sb, ch])
    if kind == "word64":
        jq = jf.copy()
        jq[:, :8] = np.clip(np.floor(jq[:, :8] * 256) / 256, 0, 255 / 256)
        return np.column_stack([jq, word64(sb, ch)])
    raise ValueError(kind)


def tagger(qcd, flav, kind):
    """BDT flavour vs rest on QCD jets, background reweighted to the signal-flavour pT, eta spectrum (as vbf_ctag)."""
    s = {k: v[qcd["flav"] == flav] for k, v in qcd.items()}
    o = {k: v[qcd["flav"] != flav] for k, v in qcd.items()}
    tr = {k: np.concatenate([s[k], o[k]]) for k in s}
    y = np.concatenate([np.ones(len(s["pt"])), np.zeros(len(o["pt"]))])
    w = np.concatenate([np.ones(len(s["pt"])), kin_weights(s, o)])
    w[y == 0] *= y.sum() / w[y == 0].sum()
    clf = HistGradientBoostingClassifier(max_iter=300, max_leaf_nodes=31, random_state=1).fit(feats(tr, kind), y, sample_weight=w)
    return lambda d: clf.predict_proba(feats(d, kind))[:, 1]


def main():
    out, sig_pat, sig_lists, mb_pat, mb_lists, qcd_lists = sys.argv[1:7]
    flav = int(sys.argv[7]) if len(sys.argv) > 7 else 4
    tags = os.environ.get("TAGS", "none,NN,pixel,pixel+charm,word64").replace(":", ",").split(",")  # ':' for sbatch --export
    sig, mb = events(sig_pat, flav), events(mb_pat, flav)
    ls, lm = merged(sig_lists), merged(mb_lists)
    lq = {k: v for k, v in load(qcd_lists).items() if k != "hit"}
    print(f"signal {len(sig['acc'])} events ({sig['acc'].sum()} accepted), minimum bias {len(mb['acc'])} events", flush=True)
    scores = {}
    for tag in tags:
        if tag == "none":
            scores[tag] = (np.ones(len(sig["acc"])), np.ones(len(mb["acc"])))
        elif tag == "NN":
            scores[tag] = (second_score(sig, ls, nn_score(ls, flav)), second_score(mb, lm, nn_score(lm, flav)))
        else:
            f = tagger(lq, flav, tag)
            scores[tag] = (second_score(sig, ls, f(ls)), second_score(mb, lm, f(lm)))
        print(f"scores {tag} ready", flush=True)
    w = BX_KHZ / MB_TOTAL
    se, me = sig["event"] % 2 == 0, mb["event"] % 2 == 0
    acc = sig["acc"]
    eff = lambda p, f: float((p & acc & f).sum() / (acc & f).sum())
    rate = lambda p, f: float(p[f].sum() * w * len(f) / f.sum())  # fold rate scaled to all events
    base = {"menu_eff_odd": eff(sig["menu"], ~se), "menu_rate_khz_odd": rate(mb["menu"], ~me),
            "n_mb": int(len(mb["acc"])), "n_sig_acc": int(acc.sum()), "n_sig_acc_odd": int((acc & ~se).sum())}
    print("menu alone:", base, flush=True)
    res = {"base": base, "on_top_of_menu": {}}
    for tag, (ss, sm) in scores.items():
        grid = np.unique(np.quantile(np.concatenate([ss, sm]), np.linspace(0, 0.995, 120))) if tag != "none" else [0.0]
        res["on_top_of_menu"][tag] = {}
        for target in ADDED:
            best = None
            for key, mcut in itertools.product(sig["mjj"], MJJ):
                vs, vm = sig["mjj"][key] > mcut, mb["mjj"][key] > mcut
                for s in grid:
                    pm = (vm & (sm > s)) | mb["menu"]
                    if rate(pm, me) - rate(mb["menu"], me) > target:
                        continue
                    e = eff((vs & (ss > s)) | sig["menu"], se)
                    if best is None or e > best[0]:
                        best = (e, key, mcut, s)
                    break
            if best is None:
                print(f"{tag:11s} +{target:3.1f} kHz: no working point within the added rate", flush=True)
                continue
            e, (l, sub, d), mcut, s = best
            ps = (sig["mjj"][(l, sub, d)] > mcut) & (ss > s)
            pm = (mb["mjj"][(l, sub, d)] > mcut) & (sm > s)
            n_odd = int((acc & ~se).sum())
            e_odd = eff(ps | sig["menu"], ~se)
            row = {"lead": l, "sub": sub, "deta": d, "mjj": mcut, "score_cut": float(s), "eff_even": float(e),
                   "eff_odd": e_odd, "eff_odd_binom_err": float(np.sqrt(e_odd * (1 - e_odd) / n_odd)),
                   "gain_odd_events": int((ps & ~sig["menu"] & acc & ~se).sum()),
                   "seed_alone_eff_odd": eff(ps, ~se),
                   "added_rate_khz_odd": rate(pm | mb["menu"], ~me) - rate(mb["menu"], ~me),
                   "n_mb_pass_odd_not_menu": int((pm & ~mb["menu"] & ~me).sum())}
            res["on_top_of_menu"][tag][target] = row
            print(f"{tag:11s} +{target:3.1f} kHz: pair {l}/{sub} m_jj>{mcut} deta>{d} score>{s:.3f}  eff(odd) {row['eff_odd']:.3f} "
                  f"(menu {base['menu_eff_odd']:.3f}, +{row['gain_odd_events']} events)  added rate(odd) "
                  f"{row['added_rate_khz_odd']:.2f} kHz ({row['n_mb_pass_odd_not_menu']} MB events)", flush=True)
    tmp = out + ".tmp"
    json.dump(res, open(tmp, "w"), indent=1)
    os.replace(tmp, out)


if __name__ == "__main__":
    main()

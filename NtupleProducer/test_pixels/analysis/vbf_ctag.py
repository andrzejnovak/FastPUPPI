#!/usr/bin/env python3
"""VBF H -> cc at L1: a looser VBF seed with two flavour-tagged central jets, at fixed rate on top of the menu.

    python3 vbf_ctag.py OUT.json SIG_GLOB SIG_LISTS MB_GLOBS MB_LISTS QCD_LISTS [FLAV]
SIG_*: VBF H -> cc (or bb, FLAV=5) ntuples and their per-jet L1 + pixel lists (make_l1ext_lists.py); MB_*: comma-
separated globs / lists of all re-simulated minimum bias (official-HT-selected, new HT > 60 and VBF-like
preselected events; together complete for VBF seeds down to 50 / 20 GeV online, m_jj > 400), each event weighted
BX_KHZ / MB_TOTAL. QCD_LISTS: training jets for the per-jet tagger.
Per-jet c score (FLAV=4) or b score (FLAV=5):
  NN     today's L1 NN, c / (c + uds + g) or b / (b + uds + g)
  pixel  BDT on the NN scores, pT, eta and the 8-number pixel summary, trained on QCD jets (flavour vs the rest)
Seed: SC4 jets (|eta| < 5, online pT), any pair with pT > LEAD, > SUB, m_jj > MJJ, |deta| > DETA, and the
second-highest per-jet score of the central NG jets (pT > 20, |eta| < 2.4) above S. Working points are chosen on
even events (signal and minimum bias) to maximise the efficiency at a given added rate on top of the planned menu,
and quoted on odd events. Signal efficiency is on the generator acceptance of vbf_menu.py.
"""
import glob
import itertools
import json
import os
import sys

import awkward as ak
import numpy as np
import uproot
import vector
from sklearn.ensemble import HistGradientBoostingClassifier

from train_sets import jet_features, kin_weights, load, summary_features
from vbf_menu import BR as MENU_BR
from vbf_menu import menu_flags, mjj

vector.register_awkward()
MB_TOTAL, BX_KHZ = 1999360, 2760 * 11.245
LEAD, SUB, MJJ, DETA = (50, 60, 70, 80, 90, 105), (20, 25, 30), (400, 500, 620, 800, 1000), (0.0, 2.5, 3.5, 4.5)
ADDED = (0.5, 1.0, 2.0, 5.0)
BR = MENU_BR + ["luminosityBlock", "event", "GenJets_phi"]


def merged(spec):
    parts = [load(f) for p in spec.split(",") for f in sorted(glob.glob(p))]
    return {k: np.concatenate([p[k] for p in parts]) for k in parts[0] if k != "hit"}  # hit features unused


def events(spec, flav):
    """Per-event flags, file by file (the jet-pair arrays of all minimum bias at once would not fit in memory)."""
    files = [f for p in spec.split(",") for f in sorted(glob.glob(p))]
    parts = [events_one(uproot.open(f)["Events"].arrays(filter_name=BR), flav) for f in files]
    return {k: (np.concatenate([q[k] for q in parts]) if k != "mjj" else
                {key: np.concatenate([q["mjj"][key] for q in parts]) for key in parts[0]["mjj"]}) for k in parts[0]}


def events_one(a, flav):
    g = ak.zip({k: a[f"GenJets_{k}"] for k in ("pt", "eta", "phi", "mass", "hadronFlavour")})
    hq = g[(g.hadronFlavour == flav) & (g.pt > 30) & (abs(g.eta) < 2.4)]
    oth = g[(g.hadronFlavour != flav) & (g.pt > 30) & (abs(g.eta) < 4.7)]
    pr = ak.combinations(oth, 2)
    m = mjj(pr["0"].pt, pr["0"].eta, pr["0"].phi, pr["0"].mass, pr["1"].pt, pr["1"].eta, pr["1"].phi, pr["1"].mass)
    acc = ak.to_numpy((ak.num(hq) >= 2) & ak.any((m > 500) & (abs(pr["0"].eta - pr["1"].eta) > 3), axis=1))
    seeds = menu_flags(a)
    menu = np.logical_or.reduce(list(seeds.values()))
    # best m_jj per (LEAD, SUB, DETA) over ordered pairs of distinct SC4 jets
    j = ak.zip({k: a[f"scPuppiCorrJets_{k}"] for k in ("pt", "eta", "phi", "mass")})
    pr = ak.argcombinations(j, 2)
    j1, j2 = j[pr["0"]], j[pr["1"]]
    mm = mjj(j1.pt, j1.eta, j1.phi, j1.mass, j2.pt, j2.eta, j2.phi, j2.mass)
    hi, lo = np.maximum(j1.pt, j2.pt), np.minimum(j1.pt, j2.pt)
    de = abs(j1.eta - j2.eta)
    best = {}
    for l, s, d in itertools.product(LEAD, SUB, DETA):
        ok = (hi > l) & (lo > s) & (de > d)
        best[(l, s, d)] = ak.to_numpy(ak.fill_none(ak.max(ak.where(ok, mm, 0.0), axis=1), 0.0))
    return {"lumi": ak.to_numpy(a.luminosityBlock), "event": ak.to_numpy(a.event), "acc": acc, "menu": menu, "mjj": best,
            **{f"seed_{k}": v for k, v in seeds.items()}}


def second_score(ev, lists, score):
    """Per event: second-highest per-jet score among central jets with pT > 20 (0 if fewer than two)."""
    sel = lists["pt"] > 20
    by = {}
    for l, e, s in zip(lists["lumi"][sel], lists["event"][sel], score[sel]):
        by.setdefault((int(l), int(e)), []).append(s)
    return np.array([sorted(by.get((int(l), int(e)), [0.0, 0.0]) + [0.0, 0.0])[-2] for l, e in zip(ev["lumi"], ev["event"])])


def tagger(qcd, flav):
    """BDT flavour vs rest on QCD jets, background reweighted to the signal-flavour pT, eta spectrum."""
    s = {k: v[qcd["flav"] == flav] for k, v in qcd.items()}
    o = {k: v[qcd["flav"] != flav] for k, v in qcd.items()}
    tr = {k: np.concatenate([s[k], o[k]]) for k in s}
    y = np.concatenate([np.ones(len(s["pt"])), np.zeros(len(o["pt"]))])
    w = np.concatenate([np.ones(len(s["pt"])), kin_weights(s, o)])
    w[y == 0] *= y.sum() / w[y == 0].sum()
    feats = lambda d: np.column_stack([jet_features(d), summary_features(d["trk"], d["ntrk"])])
    clf = HistGradientBoostingClassifier(max_iter=300, max_leaf_nodes=31, random_state=1).fit(feats(tr), y, sample_weight=w)
    return lambda d: clf.predict_proba(feats(d))[:, 1]


def nn_score(d, flav):
    sc = d["scores"]  # b, c, uds, g, ...
    num = sc[:, 1] if flav == 4 else sc[:, 0]
    return num / np.maximum(num + sc[:, 2] + sc[:, 3], 1e-6)


def main():
    out, sig_pat, sig_lists, mb_pat, mb_lists, qcd_lists = sys.argv[1:7]
    flav = int(sys.argv[7]) if len(sys.argv) > 7 else 4
    sig, mb = events(sig_pat, flav), events(mb_pat, flav)
    ls, lm, lq = merged(sig_lists), merged(mb_lists), load(qcd_lists)
    print(f"signal {len(sig['acc'])} events ({sig['acc'].sum()} accepted), minimum bias {len(mb['acc'])} events", flush=True)
    pix = tagger(lq, flav)
    scores = {"none": (np.ones(len(sig["acc"])), np.ones(len(mb["acc"]))),
              "NN": (second_score(sig, ls, nn_score(ls, flav)), second_score(mb, lm, nn_score(lm, flav))),
              "pixel": (second_score(sig, ls, pix(ls)), second_score(mb, lm, pix(lm)))}
    w = BX_KHZ / MB_TOTAL
    se, me = sig["event"] % 2 == 0, mb["event"] % 2 == 0
    acc = sig["acc"]
    eff = lambda p, f: float((p & acc & f).sum() / (acc & f).sum())
    rate = lambda p, f: float(p[f].sum() * w * len(f) / f.sum())  # fold rate scaled to all events
    base = {"menu_eff_odd": eff(sig["menu"], ~se), "menu_rate_khz_odd": rate(mb["menu"], ~me),
            "seed_rate_khz_all": {k[5:]: rate(mb[k], np.ones(len(me), bool)) for k in mb if k.startswith("seed_")},
            "seed_eff_all": {k[5:]: eff(sig[k], np.ones(len(se), bool)) for k in sig if k.startswith("seed_")},
            "n_mb": int(len(mb["acc"])), "n_sig_acc": int(acc.sum())}
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
                print(f"{tag:6s} +{target:3.1f} kHz: no working point within the added rate", flush=True)
                continue
            e, (l, sub, d), mcut, s = best
            ps = (sig["mjj"][(l, sub, d)] > mcut) & (ss > s)
            pm = (mb["mjj"][(l, sub, d)] > mcut) & (sm > s)
            row = {"lead": l, "sub": sub, "deta": d, "mjj": mcut, "score_cut": float(s), "eff_even": float(e),
                   "eff_odd": eff(ps | sig["menu"], ~se), "seed_alone_eff_odd": eff(ps, ~se),
                   "added_rate_khz_odd": rate(pm | mb["menu"], ~me) - rate(mb["menu"], ~me),
                   "n_mb_pass_odd_not_menu": int((pm & ~mb["menu"] & ~me).sum())}
            res["on_top_of_menu"][tag][target] = row
            print(f"{tag:6s} +{target:3.1f} kHz: pair {l}/{sub} m_jj>{mcut} deta>{d} score>{s:.3f}  eff(odd) {row['eff_odd']:.3f} "
                  f"(menu {base['menu_eff_odd']:.3f})  added rate(odd) {row['added_rate_khz_odd']:.2f} kHz "
                  f"({row['n_mb_pass_odd_not_menu']} events)", flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()

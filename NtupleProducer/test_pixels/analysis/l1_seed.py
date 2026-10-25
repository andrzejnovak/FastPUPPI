#!/usr/bin/env python3
"""Are HH->4b events lost at L1 because the L1 b-tag lacks information?

    python3 l1_seed.py OUTDIR "HH4b_files_glob" "MinBias_files_glob" [rate_kHz]

Seed (as in TrainTagger tagger/plot/bbbb.py): L1 SC4NG jets with |eta| < 2.4;
HT = sum pT of jets with pT > 30 GeV; b-tag = sum over the 4 leading jets (pT > 15 GeV) of a per-jet score.
Rate = fraction of minimum-bias events passing x 2760 bunches x 11.245 kHz.
For each per-jet score, (HT cut, score cut) is chosen to maximise HH->4b efficiency at the target rate.

Scores compared:
  HT only           : no b-tag requirement
  L1 NN tagger      : b / (b + uds + g) from the SC4NG tagger
  perfect b-tag     : 1 if the L1 jet is matched (dR < 0.3) to a gen jet with a b hadron, else 0
The gap between "L1 NN tagger" and "perfect b-tag" is the most any additional information could
recover at the same rate.
"""
import glob
import json
import os
import sys

import awkward as ak
import numpy as np
import uproot

MINBIAS_RATE_KHZ = 2760 * 11.245
PT_CUT, ETA_CUT, HT_CUT, DR_GEN = 15.0, 2.4, 30.0, 0.3
BR = ["L1NGJets_pt", "L1NGJets_eta", "L1NGJets_phi", "L1NGJets_score_b", "L1NGJets_score_uds", "L1NGJets_score_g",
      "GenJets_pt", "GenJets_eta", "GenJets_phi", "GenJets_hadronFlavour"]


def load(pattern):
    files = sorted(glob.glob(pattern))
    arr = ak.concatenate([uproot.open(f)["Events"].arrays(filter_name=BR, library="ak") for f in files])
    return arr, len(files)


def event_quantities(a):
    pt, eta, phi = a.L1NGJets_pt, a.L1NGJets_eta, a.L1NGJets_phi
    acc = abs(eta) < ETA_CUT
    ht = ak.to_numpy(ak.sum(pt[acc & (pt > HT_CUT)], axis=1))
    # 4 leading jets in acceptance (L1NGJets are pT ordered)
    sel = acc & (pt > PT_CUT)
    order = ak.argsort(pt[sel], ascending=False)
    jets = ak.zip({"pt": pt, "eta": eta, "phi": phi,
                   "nn": a.L1NGJets_score_b / np.maximum(a.L1NGJets_score_b + a.L1NGJets_score_uds + a.L1NGJets_score_g, 1e-6)})[sel][order][:, :4]
    # truth: L1 jet matched to a gen jet containing a b hadron
    gen = ak.zip({"pt": a.GenJets_pt, "eta": a.GenJets_eta, "phi": a.GenJets_phi, "fl": a.GenJets_hadronFlavour})
    pairs = ak.cartesian({"j": jets, "g": gen}, nested=True)
    dr = np.hypot(pairs.j.eta - pairs.g.eta, (pairs.j.phi - pairs.g.phi + np.pi) % (2 * np.pi) - np.pi)
    isb = ak.any((dr < DR_GEN) & (pairs.g.fl == 5), axis=2)
    nn_sum = ak.to_numpy(ak.sum(jets.nn, axis=1))
    truth_sum = ak.to_numpy(ak.sum(isb, axis=1)).astype(float)
    nlead = ak.to_numpy(ak.num(jets))
    # offline-like acceptance: 4 gen b jets with pT > 30, |eta| < 2.4
    genb = (gen.fl == 5) & (gen.pt > 30) & (abs(gen.eta) < ETA_CUT)
    n_genb = ak.to_numpy(ak.sum(genb, axis=1))
    pad = lambda x, fill: ak.to_numpy(ak.fill_none(ak.pad_none(x, 4, clip=True), fill))
    return {"ht": ht, "nn": nn_sum, "truth": truth_sum, "nlead": nlead, "n_genb": n_genb,
            "jet_nn": pad(jets.nn, -1.0), "jet_b": pad(isb, False).astype(bool), "jet_pt": pad(jets.pt, 0.0)}


def n_tagged(q, eb, emis, u):
    """Number of the 4 leading jets tagged by a tagger with per-jet efficiency eb (true b) and mistag emis."""
    valid = q["jet_pt"] > 0
    return ((u < np.where(q["jet_b"], eb, emis)) & valid).sum(axis=1).astype(float)


def nn_jet_roc(sig, mb, quantiles=np.linspace(0, 0.9999, 200)):
    """Per-jet NN operating points: eff on b-matched HH->4b jets vs mistag on all minimum-bias jets."""
    sb = sig["jet_nn"][sig["jet_b"] & (sig["jet_pt"] > 0)]
    mj = mb["jet_nn"][mb["jet_pt"] > 0]
    thr = np.unique(np.quantile(mj, quantiles))
    return [{"thr": float(t), "eff_b": float((sb > t).mean()), "mistag": float((mj > t).mean())} for t in thr]


def best_wp(mb, sig, score, target, sig_mask):
    """(HT cut, score cut) with the highest signal efficiency at <= target rate."""
    n_mb = len(mb["ht"])
    ht_grid = np.arange(0, 600, 5)
    best = None
    s_vals = np.unique(np.round(np.concatenate([mb[score], sig[score]]), 3)) if score else np.array([-1.0])
    if score and len(s_vals) > 400:
        s_vals = np.quantile(np.concatenate([mb[score], sig[score]]), np.linspace(0, 1, 400))
    for s in s_vals:
        mb_s = mb[score] > s if score else np.ones(n_mb, bool)
        sig_s = sig[score] > s if score else np.ones(len(sig["ht"]), bool)
        # lowest HT cut that satisfies the rate
        rates = np.array([((mb["ht"] > h) & mb_s).sum() for h in ht_grid]) / n_mb * MINBIAS_RATE_KHZ
        ok = np.where(rates <= target)[0]
        if not len(ok):
            continue
        h = ht_grid[ok[0]]
        eff = ((sig["ht"] > h) & sig_s & sig_mask).sum() / sig_mask.sum()
        if best is None or eff > best["eff"]:
            best = {"ht_cut": float(h), "score_cut": float(s), "eff": float(eff), "rate_khz": float(rates[ok[0]]),
                    "n_mb_pass": int(((mb["ht"] > h) & mb_s).sum())}
    return best or {}


def main():
    out, sig_glob, mb_glob = sys.argv[1:4]
    target = float(sys.argv[4]) if len(sys.argv) > 4 else 14.0
    os.makedirs(out, exist_ok=True)
    sa, nsf = load(sig_glob)
    ma, nmf = load(mb_glob)
    sig, mb = event_quantities(sa), event_quantities(ma)
    acc = sig["n_genb"] >= 4
    summary = {"target_rate_khz": target, "n_sig_events": int(len(acc)), "n_sig_in_acceptance": int(acc.sum()),
               "n_minbias_events": int(len(mb["ht"])), "minbias_rate_khz": MINBIAS_RATE_KHZ,
               "minbias_events_at_target": target / MINBIAS_RATE_KHZ * len(mb["ht"]), "seeds": {}}
    wps = {}
    for name, score in [("HT only", None), ("HT + L1 NN tagger", "nn"), ("HT + perfect b-tag", "truth")]:
        for label, mask in [("acceptance", acc), ("all", np.ones(len(acc), bool))]:
            wp = best_wp(mb, sig, score, target, mask)
            summary["seeds"].setdefault(name, {})[label] = wp
        wps[name] = summary["seeds"][name]["acceptance"]
        print(f"{name:22s} {json.dumps(wps[name])}")

    # who is lost: passes the perfect-tag seed but fails the NN seed (events in acceptance)
    def passes(name, score):
        wp = wps[name]
        return (sig["ht"] > wp["ht_cut"]) & ((sig[score] > wp["score_cut"]) if score else True)
    p_nn, p_true, p_ht = passes("HT + L1 NN tagger", "nn"), passes("HT + perfect b-tag", "truth"), passes("HT only", None)
    lost = acc & p_true & ~p_nn
    gained = acc & p_nn & ~p_true
    wp_nn = wps["HT + L1 NN tagger"]
    summary["lost_vs_perfect"] = {
        "n": int(lost.sum()), "frac_of_acceptance": float(lost.sum() / acc.sum()),
        "fail_ht_only": int((lost & (sig["ht"] <= wp_nn["ht_cut"]) & (sig["nn"] > wp_nn["score_cut"])).sum()),
        "fail_btag_only": int((lost & (sig["ht"] > wp_nn["ht_cut"]) & (sig["nn"] <= wp_nn["score_cut"])).sum()),
        "fail_both": int((lost & (sig["ht"] <= wp_nn["ht_cut"]) & (sig["nn"] <= wp_nn["score_cut"])).sum()),
        "n_true_b_in_lead4_hist": np.bincount(sig["truth"][lost].astype(int), minlength=5).tolist(),
    }
    summary["nn_not_perfect"] = int(gained.sum())
    summary["or_nn_ht"] = float((acc & (p_nn | p_ht)).sum() / acc.sum())
    summary["n_true_b_in_lead4_acceptance"] = np.bincount(sig["truth"][acc].astype(int), minlength=5).tolist()

    # --- L1 math: better tagging buys lower HT at fixed rate. Efficiency vs (eps_b, eps_mis) and rate.
    rng = np.random.default_rng(1)
    u_sig, u_mb = rng.random(sig["jet_nn"].shape), rng.random(mb["jet_nn"].shape)
    roc = nn_jet_roc(sig, mb)
    summary["nn_jet_roc"] = roc
    # same, restricted to where the seed operates: jets with pT > 30 GeV in events with HT > 150 GeV
    hard = lambda q: dict(q, jet_pt=np.where((q["jet_pt"] > 30) & (q["ht"] > 150)[:, None], q["jet_pt"], 0.0))
    summary["nn_jet_roc_hard"] = nn_jet_roc(hard(sig), hard(mb))
    rates = [5.0, 10.0, 14.0, 20.0, 30.0]
    scan = []
    for r in rates:
        for name, score in [("HT only", None), ("HT + L1 NN tagger", "nn"), ("HT + perfect b-tag", "truth")]:
            scan.append({"target_khz": r, "tagger": name, **best_wp(mb, sig, score, r, acc)})
        # NN as a per-jet tagger: count jets above per-jet thresholds (a few points along its ROC)
        for pt_ in roc[::20]:
            sig["ntag"], mb["ntag"] = (sig["jet_nn"] > pt_["thr"]).sum(1).astype(float), (mb["jet_nn"] > pt_["thr"]).sum(1).astype(float)
            scan.append({"target_khz": r, "tagger": "NN count", "eps_b": pt_["eff_b"], "eps_mis": pt_["mistag"],
                         **best_wp(mb, sig, "ntag", r, acc)})
        for eb in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            for em in [0.0, 0.001, 0.003, 0.01, 0.03, 0.1]:
                sig["ntag"], mb["ntag"] = n_tagged(sig, eb, em, u_sig), n_tagged(mb, eb, em, u_mb)
                scan.append({"target_khz": r, "tagger": "parametric", "eps_b": eb, "eps_mis": em,
                             **best_wp(mb, sig, "ntag", r, acc)})
        print(f"rate {r} kHz done", flush=True)
    summary["scan"] = scan
    # HH->4b HT spectrum (acceptance): how much lowering the HT cut is worth on its own
    summary["sig_ht_eff"] = {int(h): float((sig["ht"][acc] > h).mean()) for h in range(0, 505, 25)}
    json.dump(summary, open(os.path.join(out, "l1_seed.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("scan", "nn_jet_roc")}, indent=1))


if __name__ == "__main__":
    main()

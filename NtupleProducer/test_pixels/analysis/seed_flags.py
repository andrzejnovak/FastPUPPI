#!/usr/bin/env python3
"""Per-event HH->4b pass flags for the seeds in l1_seed.json at one target rate, joined to gen m_HH.

    python3 seed_flags.py l1seed_full/l1_seed.json "HH4b_glob" "genmhh_glob" OUT.npz [rate_kHz]
"""
import glob
import json
import sys

import numpy as np
import uproot

from l1_seed import event_quantities, load, n_tagged

wps, sig_glob, mhh_glob, out = sys.argv[1:5]
rate = float(sys.argv[5]) if len(sys.argv) > 5 else 14.0
s = json.load(open(wps))
sa, _ = load(sig_glob)
sig = event_quantities(sa)
ev = [uproot.open(f)["Events"].arrays(["luminosityBlock", "event"], library="np") for f in sorted(glob.glob(sig_glob))]
ids = list(zip(np.concatenate([e["luminosityBlock"] for e in ev]), np.concatenate([e["event"] for e in ev])))
# same random stream as l1_seed.py (first draw of default_rng(1) with the signal jet shape)
u_sig = np.random.default_rng(1).random(sig["jet_nn"].shape)

flags = {}
for x in s["scan"]:
    if x["target_khz"] != rate or not x:
        continue
    t = x["tagger"]
    if t == "HT only":
        key, score = "ht_only", None
    elif t == "HT + L1 NN tagger":
        key, score = "nn", sig["nn"]
    elif t == "HT + perfect b-tag":
        key, score = "perfect", sig["truth"]
    elif t == "parametric" and (x["eps_b"], x["eps_mis"]) in ((0.7, 0.01), (0.7, 0.03), (0.5, 0.03)):
        key, score = f"param_eb{x['eps_b']}_em{x['eps_mis']}", n_tagged(sig, x["eps_b"], x["eps_mis"], u_sig)
    else:
        continue
    flags[key] = (sig["ht"] > x["ht_cut"]) & ((score > x["score_cut"]) if score is not None else True)
    print(f"{key:22s} HT>{x['ht_cut']:.0f} eff(acc)={flags[key][sig['n_genb'] >= 4].mean():.3f}")

g = {k: np.concatenate([np.load(f)[k] for f in sorted(glob.glob(mhh_glob))]) for k in ("lumi", "event", "mhh", "pthh")}
order = {e: i for i, e in enumerate(zip(g["lumi"], g["event"]))}
idx = np.array([order.get(e, -1) for e in ids])
print(f"matched {np.mean(idx >= 0):.4f} of {len(ids)} events; duplicate gen event ids: {len(g['event']) - len(order)}")
mhh = np.where(idx >= 0, g["mhh"][idx], -1.0)
np.savez(out, mhh=mhh, acc=sig["n_genb"] >= 4, ht=sig["ht"], rate_khz=rate, **flags)
print("wrote", out)

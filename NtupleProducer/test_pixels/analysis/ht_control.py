#!/usr/bin/env python3
"""Control for the HH->4b seeds: spend the same added rate on lower HT thresholds of the planned menu, no b tag.

    python3 ht_control.py OUT.npz HH4B_GLOB MB_GLOBS [ADDED ...]
Planned menu as direct_rate.py: (QuadJet70_55_40_40 and HT > HT_QUAD) or HT > HT_ALONE. Both HT cuts are lowered by
the same amount; the smallest cuts with added rate (even minimum-bias events) <= ADDED are kept, and the per-event
HH->4b decisions written for all events (keyed by lumi, event) next to curves_flags.npz. Default ADDED: 2.5 kHz.
"""
import glob
import sys

import awkward as ak
import numpy as np
import uproot

from direct_rate import BX_KHZ, HT_ALONE, HT_QUAD, QUAD_BARREL, QUAD_ENDCAP

MB_TOTAL = 1999360
BR = ["luminosityBlock", "event", "L1NGJets_pt", "L1NGJets_eta"]


def ht_quad(pat):
    out = {"lumi": [], "event": [], "ht": [], "quad": []}
    for f in [f for p in pat.split(",") for f in sorted(glob.glob(p))]:
        a = uproot.open(f)["Events"].arrays(filter_name=BR)
        pt, eta = a.L1NGJets_pt, a.L1NGJets_eta
        acc = abs(eta) < 2.4
        js = ak.argsort(pt[acc], ascending=False)
        jpt, jeta = ak.pad_none(pt[acc][js], 4, clip=True), ak.pad_none(eta[acc][js], 4, clip=True)
        quad = np.ones(len(a), bool)
        for k in range(4):
            p, e = ak.to_numpy(ak.fill_none(jpt[:, k], 0.0)), ak.to_numpy(ak.fill_none(jeta[:, k], 0.0))
            quad &= p > np.where(abs(e) < 1.5, QUAD_BARREL[k], QUAD_ENDCAP[k])
        out["lumi"].append(ak.to_numpy(a.luminosityBlock))
        out["event"].append(ak.to_numpy(a.event))
        out["ht"].append(ak.to_numpy(ak.sum(pt[acc & (pt > 30)], axis=1)))
        out["quad"].append(quad)
    return {k: np.concatenate(v) for k, v in out.items()}


def main():
    out, hh_pat, mb_pat = sys.argv[1:4]
    added = [float(x) for x in sys.argv[4:]] or [2.5]
    hh, mb = ht_quad(hh_pat), ht_quad(mb_pat)
    me = mb["event"] % 2 == 0
    w = BX_KHZ / MB_TOTAL
    seed = lambda d, dlt: (d["quad"] & (d["ht"] > HT_QUAD - dlt)) | (d["ht"] > HT_ALONE - dlt)
    rate = lambda p, f: p[f].sum() * w * len(f) / f.sum()
    base = rate(seed(mb, 0.0), me)
    res = {"lumi": hh["lumi"], "event": hh["event"], "menu": seed(hh, 0.0)}
    for a in added:
        dlt = 0.0
        while rate(seed(mb, dlt + 1.0), me) - base <= a and dlt < 300:
            dlt += 1.0
        odd_added = rate(seed(mb, dlt), ~me) - rate(seed(mb, 0.0), ~me)
        print(f"+{a:g} kHz: HT cuts lowered by {dlt:.0f} GeV ({HT_QUAD - dlt:.0f} with quad jets, {HT_ALONE - dlt:.0f} alone); "
              f"added rate on odd events {odd_added:.2f} kHz", flush=True)
        res[f"HTlow|menu|{a:g}"] = seed(hh, dlt)
        res[f"HTlow_delta|{a:g}"] = np.array(dlt)
    np.savez(out, **res)


if __name__ == "__main__":
    main()

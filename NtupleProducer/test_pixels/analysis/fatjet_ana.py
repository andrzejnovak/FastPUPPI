#!/usr/bin/env python3
"""Boosted H -> cc / bb at L1: large-jet seeds against minimum-bias rate, from the fatjet_parts.py tables.

    python3 fatjet_ana.py OUT.json SIG_NAME:SIG_GLOB [...] MB:MB_GLOB[,MB_GLOB...] [SUBJET_SCORES.npz]
Signal: events with a merged Higgs candidate (>= 2 generator jets of the flavour within dR < 0.8, |eta| < 2.4); the
L1 large jet matched to it (dR < 0.4). Minimum bias: all re-simulated events, weighted BX_KHZ / MB_TOTAL (complete
for large-jet seeds where the event preselections are; compare MB globs with and without the VBF-like set).
Seeds, on the highest-pT large jet passing them (up to 3 per event):
  pt        large jet pT > X
  mass      + constituent mass in [M_LO, M_HI]
  prong     + two-prong score > P
  subjet    + both R = 0.4 jets inside with per-jet score > S (if SUBJET_SCORES given: lumi, event, jidx, score)
Working points chosen on even events to maximise the signal efficiency for H pT > 300 GeV at a given added rate on
top of SingleJet230 | HT450 (the menu seeds a boosted Higgs mostly fires), quoted on odd events.
"""
import glob
import itertools
import json
import sys

import numpy as np

MB_TOTAL, BX_KHZ = 1999360, 2760 * 11.245
PT = (100, 125, 150, 175, 200, 250)
MWIN = ((0, 1e9), (40, 200), (60, 180), (80, 160), (90, 150))
PRONG = (-2.0, 0.95, 0.97, 0.98, 0.99, 0.995)
ADDED = (1.0, 2.0, 5.0)
HPT_EDGES = (150, 200, 250, 300, 350, 400, 500, 800)


def read(spec):
    J, E, off = [], [], 0
    for f in [f for p in spec.split(",") for f in sorted(glob.glob(p))]:
        d = np.load(f)
        j = d["jet"].copy()
        j[:, 0] += off
        J.append(j)
        E.append(d["ev"])
        off += len(d["ev"])
    J, E = np.concatenate(J), np.concatenate(E)
    cols = dict(zip(np.load(f)["jet_cols"], range(J.shape[1])))
    ecol = dict(zip(np.load(f)["ev_cols"], range(E.shape[1])))
    return J, E, cols, ecol


def subjet_ok(J, E, c, e, sub, s):
    """Both R = 0.4 jets inside each large jet have score > s (False if fewer than two)."""
    if sub is None:
        return np.ones(len(J), bool)
    ev = J[:, c["evt"]].astype(int)
    out = np.ones(len(J), bool)
    for col in ("sub0", "sub1"):
        k = J[:, c[col]].astype(int)
        sc = np.array([sub.get((int(E[i, e["lumi"]]), int(E[i, e["event"]]), j), 0.0) if j >= 0 else 0.0
                       for i, j in zip(ev, k)])
        out &= sc > s
    return out


def event_pass(J, nev, c, ok):
    p = np.zeros(nev, bool)
    p[J[ok, c["evt"]].astype(int)] = True
    return p


def main():
    out = sys.argv[1]
    sub = None
    args = sys.argv[2:]
    if not args[-1].startswith("MB:"):
        d = np.load(args[-1])
        sub = {(int(l), int(e), int(j)): float(s) for l, e, j, s in zip(d["lumi"], d["event"], d["jidx"], d["score"])}
        args = args[:-1]
    sigs, mbspec = args[:-1], args[-1].split(":", 1)[1]
    Jm, Em, c, e = read(mbspec)
    nmb = len(Em)
    w = BX_KHZ / MB_TOTAL
    me = Em[:, e["event"]] % 2 == 0
    menu_mb = (Em[:, e["single230"]] > 0) | (Em[:, e["ht450"]] > 0)
    rate = lambda p, f: float(p[f].sum() * w * nmb / f.sum())
    res = {"minbias": {"events": nmb, "menu_rate_khz": rate(menu_mb, np.ones(nmb, bool)),
                       "rate_khz_lead_pt": {x: rate(event_pass(Jm, nmb, c, Jm[:, c["pt"]] > x), np.ones(nmb, bool)) for x in PT}}}
    print("minimum bias", json.dumps(res["minbias"]), flush=True)
    sub_grid = (-1.0,) if sub is None else tuple(np.quantile(list(sub.values()), (0, 0.5, 0.7, 0.8, 0.9, 0.95)))
    sub_mb = {s: subjet_ok(Jm, Em, c, e, sub, s) for s in sub_grid}
    for spec in sigs:
        name, pat = spec.split(":", 1)
        Js, Es, _, _ = read(pat)
        ns = len(Es)
        hpt = Es[:, e["hpt"]]
        fid = (Es[:, e["nq"]] >= 2) & (abs(Es[:, e["heta"]]) < 2.4)
        se = Es[:, e["event"]] % 2 == 0
        menu_s = (Es[:, e["single230"]] > 0) | (Es[:, e["ht450"]] > 0)
        hm = Js[:, c["dr_h"]] < 0.4  # large jet matched to the Higgs candidate
        sub_s = {s: subjet_ok(Js, Es, c, e, sub, s) for s in sub_grid}
        target_sel = fid & (hpt > 300)
        eff = lambda p, f, sel=target_sel: float((p & sel & f).sum() / max((sel & f).sum(), 1))
        r = {"events": ns, "fiducial": int(fid.sum()), "fid_hpt300": int(target_sel.sum()),
             "menu_eff_odd_hpt300": eff(menu_s, ~se),
             "matched_mass_q16_50_84": np.percentile(Js[hm & (hpt[Js[:, c["evt"]].astype(int)] > 300), c["mass"]], [16, 50, 84]).tolist(),
             "seeds": {}}
        print(f"{name}: {ns} events, {fid.sum()} merged, {target_sel.sum()} with H pT > 300; menu keeps (odd) "
              f"{r['menu_eff_odd_hpt300']:.3f}; matched-jet mass q16/50/84 {np.round(r['matched_mass_q16_50_84'], 1)}", flush=True)
        for kind in ("pt", "mass", "prong", "subjet"):
            if kind == "subjet" and sub is None:
                continue
            mw = MWIN if kind != "pt" else MWIN[:1]
            pg = PRONG if kind in ("prong",) else PRONG[:1]
            sg = sub_grid if kind == "subjet" else sub_grid[:1]
            r["seeds"][kind] = {}
            for target in ADDED:
                best = None
                for x, (mlo, mhi), p, s in itertools.product(PT, mw, pg, sg):
                    def ok(J, subok):
                        return (J[:, c["pt"]] > x) & (J[:, c["mass"]] > mlo) & (J[:, c["mass"]] < mhi) & (J[:, c["prong"]] > p) & subok
                    pm = event_pass(Jm, nmb, c, ok(Jm, sub_mb[s]))
                    if rate(pm | menu_mb, me) - rate(menu_mb, me) > target:
                        continue
                    ps = event_pass(Js, ns, c, ok(Js, sub_s[s]))
                    ev_ = eff(ps | menu_s, se)
                    if best is None or ev_ > best[0]:
                        best = (ev_, x, mlo, mhi, p, s, ps, pm)
                if best is None:
                    continue
                ev_, x, mlo, mhi, p, s, ps, pm = best
                row = {"pt": x, "mass": [mlo, mhi], "prong": p, "subjet": float(s), "eff_even": ev_,
                       "eff_odd_hpt300": eff(ps | menu_s, ~se),
                       "added_rate_khz_odd": rate(pm | menu_mb, ~me) - rate(menu_mb, ~me),
                       "n_mb_added_odd": int((pm & ~menu_mb & ~me).sum()),
                       "by_hpt_odd": [{"hpt": [lo, hi], "n": int((fid & (hpt >= lo) & (hpt < hi) & ~se).sum()),
                                       "menu": eff(menu_s, ~se, fid & (hpt >= lo) & (hpt < hi)),
                                       "menu_plus_seed": eff(ps | menu_s, ~se, fid & (hpt >= lo) & (hpt < hi))}
                                      for lo, hi in zip(HPT_EDGES[:-1], HPT_EDGES[1:])]}
                r["seeds"][kind][target] = row
                print(f"  {kind:6s} +{target:.0f} kHz: pT>{x} m[{mlo:g},{mhi:g}] prong>{p:g} sub>{s:.2f}  eff(odd, H pT>300) "
                      f"{row['eff_odd_hpt300']:.3f}  added rate(odd) {row['added_rate_khz_odd']:.2f} kHz ({row['n_mb_added_odd']} events)",
                      flush=True)
        res[name] = r
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()

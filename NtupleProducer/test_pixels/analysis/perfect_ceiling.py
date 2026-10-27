#!/usr/bin/env python3
"""Perfect-b-tag ceiling with a flavour-aware minimum-bias rate.

    python3 perfect_ceiling.py OUT.json OUT_FLAGS.npz HH4B_GLOB MB_GLOBS QCD_GLOB OFFLINE_FLAGS LISTS_HH LISTS_QCD
The minimum bias carries no flavour truth (its high-HT jets come from pileup interactions without a generator record),
so a seed on generator flavour seemed to cost no rate (direct_curves.py "perfect"). Here the perfect seed
(HT > h and at least k true b jets among the 4 leading L1 jets, as direct_curves.py) gets its rate from the QCD
probability P(n_b >= k | L1 HT bin, menu flag), applied to every minimum-bias event (k >= 3: P(>= 2) per bin times
the pooled ratio, too rare per bin). Pileup b jets are invisible in
QCD as well, so this is still a lower bound on the perfect seed's rate (an upper bound on the ceiling).
Thresholds are chosen on even HH events, efficiencies quoted on odd ones (as direct_curves.py). Writes flags under
the direct_curves.py keys "perfect|menu|<added kHz>" and "perfect|alone|<kHz>".
"""
import json
import os
import sys

import numpy as np

os.environ.setdefault("MB_TOTAL", "1999360")
import direct_rate as D  # noqa: E402
from train_sets import load  # noqa: E402

ADDED = (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 7.5, 10.0, 15.0)
STANDALONE = (2.0, 3.0, 5.0, 7.5, 10.0, 14.0, 20.0, 30.0)
HT_EDGES = np.array([150, 175, 200, 225, 250, 300, 350, 400, 500, 700, 1e9])
HT_GRID = np.arange(150, 600, 10)


def main():
    out, out_flags, hh_pat, mb_pat, qcd_pat, off_path, f_hh, f_q = sys.argv[1:9]
    hh, mb, qcd = D.events(hh_pat), D.events(mb_pat), D.events(qcd_pat)
    lh, lq = load(f_hh), load(f_q)
    nb_hh = D.jet_scores(hh, lh, (lh["flav"] == 5).astype(float))
    nb_q = D.jet_scores(qcd, lq, (lq["flav"] == 5).astype(float))
    print(f"HH {len(hh['ht'])}, MB {len(mb['ht'])}, QCD {len(qcd['ht'])} events", flush=True)

    # QCD: P(n_b >= k | HT bin, menu flag), k = 1..4
    iq = np.clip(np.digitize(qcd["ht"], HT_EDGES) - 1, -1, len(HT_EDGES) - 2)
    P = np.zeros((2, len(HT_EDGES) - 1, 5))
    N = np.zeros((2, len(HT_EDGES) - 1), int)
    for m in (0, 1):
        for b in range(len(HT_EDGES) - 1):
            sel = (iq == b) & (qcd["menu"] == bool(m))
            N[m, b] = sel.sum()
            for k in range(1, 5):
                P[m, b, k] = (nb_q[sel] >= k).mean() if sel.sum() >= 20 else np.nan
    # sparse bins: fall back to the other menu flag, then to the nearest filled HT bin
    for m in (0, 1):
        for b in range(len(HT_EDGES) - 1):
            if np.isnan(P[m, b, 1]):
                P[m, b] = P[1 - m, b]
        for b in range(len(HT_EDGES) - 1):
            if np.isnan(P[m, b, 1]):
                filled = [c for c in range(len(HT_EDGES) - 1) if not np.isnan(P[m, c, 1])]
                P[m, b] = P[m, min(filled, key=lambda c: abs(c - b))]
    P[:, :, 0] = 1.0
    # n_b >= 3, 4 are too rare per bin (0-3 QCD events): P(>= k) = P(>= 2) x the ratio pooled over all HT bins
    for m in (0, 1):
        sel = qcd["menu"] == bool(m)
        n2 = max((nb_q[sel] >= 2).sum(), 1)
        for k in (3, 4):
            P[m, :, k] = P[m, :, 2] * (nb_q[sel] >= k).sum() / n2
    res_ratio = {m: [float((nb_q[qcd["menu"] == bool(m)] >= k).sum() / max((nb_q[qcd["menu"] == bool(m)] >= 2).sum(), 1)) for k in (3, 4)] for m in (0, 1)}
    print("pooled P(>=3)/P(>=2), P(>=4)/P(>=2), not menu / menu:", res_ratio, flush=True)
    print("QCD P(n_b >= 1/2/3) per HT bin (not menu-accepted):", flush=True)
    for b in range(len(HT_EDGES) - 1):
        print(f"  HT {HT_EDGES[b]:4.0f}-{HT_EDGES[b + 1]:5.0f}: N {N[0, b]:5d}/{N[1, b]:5d}  "
              + " ".join(f"{P[0, b, k]:.4f}" for k in (1, 2, 3)), flush=True)

    # expected perfect-seed weight per minimum-bias event (kHz) for each (HT cut, k)
    im = np.clip(np.digitize(mb["ht"], HT_EDGES) - 1, 0, len(HT_EDGES) - 2)
    pk = P[mb["menu"].astype(int), im]  # (n_mb, 5)
    w = D.BX_KHZ / D.MB_TOTAL
    rate = lambda h, k, base: float((w * pk[:, k] * ((mb["ht"] > h) & ~base)).sum())

    o = np.load(off_path)
    opos = {(l, e): i for i, (l, e) in enumerate(zip(o["lumi"], o["event"]))}
    oi = np.array([opos.get((l, e), -1) for l, e in zip(hh["lumi"], hh["event"])])
    offsel = (oi >= 0) & np.where(oi >= 0, (o["resolved_4b"] | o["3b_mass"])[np.maximum(oi, 0)], False)
    sets = {"all": np.ones(len(hh["ht"]), bool), "fiducial": hh["fid"], "offline_4b3b": offsel}
    even = hh["event"] % 2 == 0
    eff = lambda p: {k: float((p & m & ~even).sum() / (m & ~even).sum()) for k, m in sets.items()}
    res = {"qcd_P_nb": P.tolist(), "qcd_N": N.tolist(), "ht_edges": HT_EDGES.tolist(), "on_top_of_menu": [], "standalone": [],
           "old_free_rate_note": "direct_curves.py perfect seed: MB flavour labels empty, rate ~0"}
    flags = {}
    for mode, targets in (("menu", ADDED), ("alone", STANDALONE)):
        base_mb = mb["menu"].astype(bool) if mode == "menu" else np.zeros(len(mb["ht"]), bool)
        base_hh = hh["menu"].astype(bool) if mode == "menu" else np.zeros(len(hh["ht"]), bool)
        table = {(h, k): rate(h, k, base_mb) for h in HT_GRID for k in (1, 2, 3, 4)}
        for t in targets:
            best = None
            for (h, k), r in table.items():
                if r > t:
                    continue
                p = ((hh["ht"] > h) & (nb_hh >= k)) | base_hh
                e = (p & hh["fid"] & even).sum() / (hh["fid"] & even).sum()
                if best is None or e > best[0]:
                    best = (e, h, k, r)
            _, h, k, r = best
            p = ((hh["ht"] > h) & (nb_hh >= k)) | base_hh
            row = {"target_khz": t, "ht_cut": float(h), "n_b_min": int(k), "rate_khz": r, "eff": eff(p)}
            res["on_top_of_menu" if mode == "menu" else "standalone"].append(row)
            flags[f"perfect|{mode}|{t:g}"] = p
            print(f"perfect {mode:5s} {t:5.1f} kHz: HT > {h:.0f}, n_b >= {k} ({r:.2f} kHz)  "
                  + " ".join(f"{a} {v:.3f}" for a, v in row["eff"].items()), flush=True)
    flags.update({"lumi": hh["lumi"], "event": hh["event"]})
    json.dump(res, open(out, "w"), indent=1)
    np.savez_compressed(out_flags, **flags)
    print("wrote", out, out_flags)


if __name__ == "__main__":
    main()

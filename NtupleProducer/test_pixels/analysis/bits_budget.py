#!/usr/bin/env python3
"""Inputs for the bit budget of the L1-track pixel extension: per crossing, how many L1 tracks would request pixel
hits and how many clusters their search windows hold (default and narrow windows).

    python3 bits_budget.py OUT.json SAMPLE file.root [file.root ...]
Requesting tracks: L1 tracks with pT > 2 GeV within dR < 0.4 of L1 jets (pT > 30, |eta| < 2.4) and |z0 - z_vtx| < 1.5 cm.
Per event: HT (as in the seed study), number of requesting tracks, clusters in their windows (summed over tracks).
"""
import json
import sys

import awkward as ak
import numpy as np
import uproot

import l1ext as X
import make_jets as MJ

WINDOWS = {"default": (X.WIN_RPHI, X.WIN_Z, X.WIN_R), "narrow": (0.08, 0.8, 0.8)}
out, sample, files = sys.argv[1], sys.argv[2], sys.argv[3:]
br = ["L1NGJets_pt", "L1NGJets_eta", "L1NGJets_phi", "L1Tracks_*", "L1TracksVtx_z0", "PixelClusters_*"]
rows = []
for f in files:
    for arr in uproot.iterate(f + ":Events", filter_name=br, step_size=50):
        for e in arr:
            jpt, jeta, jphi = (ak.to_numpy(e[f"L1NGJets_{k}"]) for k in ("pt", "eta", "phi"))
            js = (jpt > 30) & (abs(jeta) < 2.4)
            ht = float(jpt[js].sum())
            tpt, teta, tphi, tz0, tq = (ak.to_numpy(e[f"L1Tracks_{k}"]) for k in ("pt", "eta", "phi", "z0", "charge"))
            zl1 = float(e.L1TracksVtx_z0[0]) if len(e.L1TracksVtx_z0) else 0.0
            inc = np.zeros(len(tpt), bool)
            for j in np.where(js)[0]:
                inc |= np.hypot(teta - jeta[j], MJ.dphi(tphi, jphi[j])) < 0.4
            req = np.where(inc & (tpt > 2) & (abs(tz0 - zl1) < 1.5))[0]
            row = {"ht": ht, "njet": int(js.sum()), "ntrk_req": int(len(req)), "nclus_event": int(len(e.PixelClusters_x))}
            if len(req):
                cl = X.sort_phi(X.clusters_of(e))
                for name, (wr, wz, wR) in WINDOWS.items():
                    X.WIN_RPHI, X.WIN_Z, X.WIN_R = wr, wz, wR
                    n = 0
                    for t in req:
                        sub = X.phi_window(cl, tphi[t])
                        n += len(X.window({"pt": tpt[t], "eta": teta[t], "phi": tphi[t], "z0": tz0[t], "charge": tq[t]}, sub)[0])
                    row[f"nclus_{name}"] = n
            else:
                row.update(nclus_default=0, nclus_narrow=0)
            rows.append(row)
summ = {}
for cut in (0, 140, 200):
    sel = [r for r in rows if r["ht"] > cut]
    if not sel:
        continue
    summ[f"ht>{cut}"] = {"n_events": len(sel), **{k: float(np.mean([r[k] for r in sel]))
                                                  for k in ("njet", "ntrk_req", "nclus_default", "nclus_narrow", "nclus_event")}}
print(sample, json.dumps(summ, indent=1))
json.dump({"sample": sample, "summary": summ, "rows": rows}, open(out, "w"))

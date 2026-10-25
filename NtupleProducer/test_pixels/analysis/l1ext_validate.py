#!/usr/bin/env python3
"""Validate the L1-track pixel extension against HLT pixel tracks (cluster truth links).

    python3 l1ext_validate.py OUT.json file.root [file.root ...]   (env: NEVT, CURV_SIGN)
For L1 tracks (pT > 2 GeV) inside L1 jets (pT > 30, |eta| < 2.4, dR < 0.4): reference = HLT pixel track matched in
(dR < 0.02, |dpT|/pT < 0.3). Reports extension efficiency, hit purity (picked clusters on the reference track),
and d0 / z0 residuals to the reference.
"""
import json
import os
import sys

import numpy as np
import uproot

import l1ext as X

NEVT = int(os.environ.get("NEVT", 50))
for _k in ("CURV_SIGN", "NBEST", "MIN_HITS", "MAX_LAYERS"):
    setattr(X, _k, int(os.environ.get(_k, getattr(X, _k))))
for _k in ("WIN_RPHI", "WIN_Z", "WIN_R", "MISS_PENALTY", "COT_SIG"):
    setattr(X, _k, float(os.environ.get(_k, getattr(X, _k))))
BR = ["L1Tracks_*", "PixelClusters_*", "PixelTracks_pt", "PixelTracks_eta", "PixelTracks_phi", "PixelTracks_dxyBS",
      "PixelTracks_dzBS", "PixelTracks_dxyErr", "L1NGJets_pt", "L1NGJets_eta", "L1NGJets_phi"]

rows = []
for f in sys.argv[2:]:
    for ev in uproot.open(f)["Events"].iterate(filter_name=BR, entry_stop=NEVT, step_size=10, library="ak"):
        for e in ev:
            cl = X.sort_phi(X.clusters_of(e))
            jpt, jeta, jphi = (np.asarray(e[f"L1NGJets_{c}"]) for c in ("pt", "eta", "phi"))
            js = (jpt > 30) & (abs(jeta) < 2.4)
            tpt, teta, tphi, tz0, tq = (np.asarray(e[f"L1Tracks_{c}"]) for c in ("pt", "eta", "phi", "z0", "charge"))
            ppt, peta, pphi = (np.asarray(e[f"PixelTracks_{c}"]) for c in ("pt", "eta", "phi"))
            pdxy, pdz, perr = (np.asarray(e[f"PixelTracks_{c}"]) for c in ("dxyBS", "dzBS", "dxyErr"))
            for t in range(len(tpt)):
                if tpt[t] < 2 or not js.any():
                    continue
                if np.min(np.hypot(jeta[js] - teta[t], X.dphi(jphi[js], tphi[t]))) > 0.4:
                    continue
                sub = X.phi_window(cl, tphi[t])
                res = X.extend({"pt": tpt[t], "eta": teta[t], "phi": tphi[t], "z0": tz0[t], "charge": tq[t]}, sub)
                dr = np.hypot(peta - teta[t], X.dphi(pphi, tphi[t]))
                ok = (dr < 0.02) & (abs(ppt - tpt[t]) / tpt[t] < 0.3)
                ref = int(np.where(ok)[0][np.argmin(dr[ok])]) if ok.any() else -1
                row = {"pt": float(tpt[t]), "eta": float(teta[t]), "ref": ref, "ext": res is not None}
                if ref >= 0:
                    row.update(ref_dxy=float(pdxy[ref]), ref_dz=float(pdz[ref]), ref_err=float(perr[ref]))
                if res is not None:
                    d0, z0, chi2, nh, idx = res
                    row.update(d0=float(d0), z0=float(z0), chi2=float(chi2), nh=int(nh),
                               purity=float(np.mean(sub["trk"][idx] == ref)) if ref >= 0 else -1.0,
                               on_any=float(np.mean(sub["trk"][idx] >= 0)))
                rows.append(row)

R = rows
ref = [r for r in R if r["ref"] >= 0]
ext_ref = [r for r in ref if r["ext"]]
pur = np.array([r["purity"] for r in ext_ref])
d = np.array([r["d0"] - r["ref_dxy"] for r in ext_ref])
dz = np.array([r["z0"] - r["ref_dz"] for r in ext_ref])
good = pur == 1
summ = {"settings": {k: getattr(X, k) for k in ("CURV_SIGN", "NBEST", "MIN_HITS", "MAX_LAYERS", "WIN_RPHI", "WIN_Z", "WIN_R",
                                                 "MISS_PENALTY", "COT_SIG")}, "n_l1": len(R), "frac_with_ref": len(ref) / len(R),
        "eff_ext_all": float(np.mean([r["ext"] for r in R])), "eff_ext_ref": len(ext_ref) / max(len(ref), 1),
        "frac_all_hits_correct": float(good.mean()), "mean_purity": float(pur.mean()),
        "d0_res_um_all": float(np.std(np.clip(d, -0.1, 0.1)) * 1e4), "d0_res_um_correct": float(np.std(d[good]) * 1e4),
        "d0_mad_um_all": float(np.median(abs(d)) * 1.4826e4), "z0_mad_um_all": float(np.median(abs(dz)) * 1.4826e4),
        "ref_dxy_err_um_median": float(np.median([r["ref_err"] for r in ref]) * 1e4),
        "nh_mean": float(np.mean([r["nh"] for r in R if r["ext"]]))}
print(json.dumps(summ, indent=1))
json.dump({"summary": summ, "rows": R}, open(sys.argv[1], "w"))

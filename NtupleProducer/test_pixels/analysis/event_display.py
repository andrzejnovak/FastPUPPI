#!/usr/bin/env python3
"""Event display of the L1 track -> pixel hit association for one displaced track in a b jet (HH->4b, PU 200).

    python3 event_display.py ntuple.root OUT.png [entry]
Finds a track in a generator-b L1 jet whose pixel refit is significantly displaced and whose picked clusters are all
on the matching HLT pixel track. Left: transverse plane, rotated so the track runs along +u; the vertical axis is
stretched (mm vs cm) so the displacement and the pileup clusters in the window are visible. Right: r-z view.
"""
import sys

import awkward as ak
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import uproot

import l1ext as X

f, out = sys.argv[1], sys.argv[2]
start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
br = ["L1Tracks_*", "PixelClusters_*", "PixelTracks_pt", "PixelTracks_eta", "PixelTracks_phi", "PixelTracks_dxyBS",
      "L1NGJets_*", "GenJets_pt", "GenJets_eta", "GenJets_phi", "GenJets_hadronFlavour", "L1TracksVtx_z0"]
arr = uproot.open(f)["Events"].arrays(filter_name=br, entry_start=start, entry_stop=start + 40)
pick = None
for ie in range(len(arr)):
    e = arr[ie]
    cl = X.sort_phi(X.clusters_of(e))
    jpt, jeta, jphi = (ak.to_numpy(e[f"L1NGJets_{k}"]) for k in ("pt", "eta", "phi"))
    geta, gphi, gfl = (ak.to_numpy(e[f"GenJets_{k}"]) for k in ("eta", "phi", "hadronFlavour"))
    tpt, teta, tphi, tz0, tq = (ak.to_numpy(e[f"L1Tracks_{k}"]) for k in ("pt", "eta", "phi", "z0", "charge"))
    ppt, peta, pphi = (ak.to_numpy(e[f"PixelTracks_{k}"]) for k in ("pt", "eta", "phi"))
    for j in np.where((jpt > 40) & (abs(jeta) < 1.2))[0]:
        dr = np.hypot(geta - jeta[j], X.dphi(gphi, jphi[j]))
        if not len(dr) or dr.min() > 0.3 or gfl[np.argmin(dr)] != 5:
            continue
        for t in np.where((np.hypot(teta - jeta[j], X.dphi(tphi, jphi[j])) < 0.4) & (tpt > 2) & (tpt < 8) & (abs(teta) < 0.8))[0]:
            sub = X.phi_window(cl, tphi[t])
            r = X.extend({"pt": tpt[t], "eta": teta[t], "phi": tphi[t], "z0": tz0[t], "charge": tq[t]}, sub)
            if r is None or r[3] < 4:
                continue
            d = np.hypot(peta - teta[t], X.dphi(pphi, tphi[t]))
            ok = (d < 0.02) & (abs(ppt - tpt[t]) / tpt[t] < 0.3)
            if not ok.any():
                continue
            ref = np.where(ok)[0][np.argmin(d[ok])]
            sig = abs(r[0]) / X.d0_err(tpt[t], teta[t])
            if np.all(sub["trk"][r[4]] == ref) and 0.03 < abs(r[0]) < 0.15 and sig > 4:
                pick = (ie, t, sub, r, ref, jpt[j])
                break
        if pick:
            break
    if pick:
        break
ie, t, sub, (d0, z0, chi2, nh, idx), ref, jetpt = pick
e = arr[ie]
tpt, teta, tphi, tz0, tq = (float(e[f"L1Tracks_{k}"][t]) for k in ("pt", "eta", "phi", "z0", "charge"))
k = X.CURV_SIGN * tq * X.B_K / tpt
cot = np.sinh(teta)
r, z, ph = sub["r"], sub["z"], sub["phi"]
# rotate so the L1 track (prompt helix) runs along +u: v = transverse offset from the prompt prediction [mm]
phi_pred = tphi - np.arcsin(np.clip(k * r / 2, -1, 1))
u = r
v = r * X.dphi(ph, phi_pred) * 10
zp = tz0 + cot * 2 * np.arcsin(np.clip(k * r / 2, -1, 1)) / k
barrel = abs(sub["lid"]) < 10
strip = barrel & (abs(v) < 3) & (abs(z - zp) < 1.5)
fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
a = ax[0]
a.scatter(u[strip], v[strip], s=6, c="0.65", label=f"pixel clusters in the window ({strip.sum()})")
on = sub["trk"] == ref
a.scatter(u[on & barrel], v[on & barrel], s=70, facecolors="none", edgecolors="tab:blue", lw=1.5, label="hits of the HLT pixel track")
a.scatter(u[idx], v[idx], s=22, c="tab:red", zorder=5, label="hits picked by the L1-track extension")
rr = np.linspace(0, 16, 200)
a.plot(rr, 0 * rr, "k--", lw=1, label="L1 track (Outer Tracker fit, d0 = 0)")
_, _, _, phi0 = X.fit(r[idx], ph[idx], z[idx], barrel[idx], k, tphi, cot)
a.plot(rr, (rr * X.dphi(phi0, tphi) + d0) * 10, c="tab:red", lw=1, label=f"pixel refit: d0 = {d0 * 1e4:.0f} um")
a.set_xlim(0, 16)
a.set_ylim(-3, 3)
a.set_xlabel("radius along the track [cm]")
a.set_ylabel("transverse offset from the L1 track [mm]")
a.set_title(f"b jet (pT {jetpt:.0f} GeV), L1 track pT {tpt:.1f} GeV: transverse plane", fontsize=10)
a.legend(fontsize=7.5, loc="upper left")
b = ax[1]
st2 = barrel & (abs(v) < 3) & (abs(z - zp) < 1.5)
b.scatter(r[st2], (z[st2] - zp[st2]) * 10, s=6, c="0.65")
b.scatter(r[on & barrel], (z[on & barrel] - zp[on & barrel]) * 10, s=70, facecolors="none", edgecolors="tab:blue", lw=1.5)
b.scatter(r[idx], (z[idx] - zp[idx]) * 10, s=22, c="tab:red", zorder=5)
b.axhline(0, c="k", ls="--", lw=1)
b.set_xlim(0, 16)
b.set_ylim(-15, 15)
b.set_xlabel("radius [cm]")
b.set_ylabel("z offset from the L1 track prediction [mm]")
b.set_title(f"r-z view (L1 z0 = {tz0:.2f} cm, refit z0 = {z0:.2f} cm)", fontsize=10)
fig.suptitle("L1 track extended into the pixel detector: the right hits picked out of PU 200 (gray)", fontsize=11)
fig.tight_layout()
fig.savefig(out, dpi=140)
print(f"event {ie + start}, track {t}: pT {tpt:.1f}, d0 refit {d0 * 1e4:.0f} um, {nh} hits, window clusters {strip.sum()}")

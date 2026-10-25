#!/usr/bin/env python3
"""Event display of the L1 track -> pixel hit association for one displaced track in a b jet (HH->4b, PU 200).

    python3 event_display.py ntuple.root OUT.png [entry]
Finds a track in a generator-b L1 jet whose pixel refit is significantly displaced and whose picked clusters are all
on the matching HLT pixel track. Four steps, zooming in:
  1. tracker in 3D (pixel layers from the clusters; Outer Tracker schematic, TDR radii) with the track and the slice;
  2. the slice in the transverse plane, true scale: L1 track (Outer Tracker) and its prompt extrapolation (d0 = 0);
  3. pixel layers, frame rotated along the track, offset stretched (mm vs cm): search windows and candidate clusters;
  4. same frame: picked clusters and the pixel refit, extrapolated to the beam line (d0).
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
ref_dxy = float(e["PixelTracks_dxyBS"][ref])
k = X.CURV_SIGN * tq * X.B_K / tpt
cot = np.sinh(teta)
cl_all = X.clusters_of(e)
cand, _, _, barrel_w, rphi_w, zp_w, _ = X.window({"pt": tpt, "eta": teta, "phi": tphi, "z0": tz0, "charge": tq}, sub)
r, z, ph = sub["r"], sub["z"], sub["phi"]
barrel = abs(sub["lid"]) < 10
on = sub["trk"] == ref

# colours as on the page: Outer Tracker = amber, L1 track + pixels = orange, HLT pixel tracks = green
C_OT, C_EXT, C_HLT, C_PU, INK, INK2 = "#eda100", "#eb6834", "#1baf7a", "#b9b7b0", "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False})
PIX_R = [np.median(cl_all["r"][cl_all["lid"] == l]) for l in (1, 2, 3, 4)]
PIX_SPAN = [np.percentile(cl_all["r"][cl_all["lid"] == l], [0.5, 99.5]) for l in (1, 2, 3, 4)]
PIX_DZ = [np.median(abs(cl_all["z"][abs(cl_all["lid"]) == l])) for l in range(11, 17)]
OT_R = [23.0, 35.7, 50.8, 68.6, 88.6, 108.0]  # Outer Tracker barrel layers (TDR, schematic)
OT_ZB, OT_DZ = 120.0, [131.0, 155.0, 185.0, 220.0, 265.0]


def helix(rr, d=0.0, phi0=tphi, z0_=tz0):
    """Points of the track at radii rr (prompt helix, small-d0 shift perpendicular to the direction)."""
    a = np.arcsin(np.clip(k * rr / 2, -1, 1))
    p = phi0 - a
    s_ = 2 * a / k
    return rr * np.cos(p) - d * np.sin(phi0), rr * np.sin(p) + d * np.cos(phi0), z0_ + cot * s_


def rot(x, y):
    """Frame along the track direction: u along, w across."""
    return x * np.cos(tphi) + y * np.sin(tphi), -x * np.sin(tphi) + y * np.cos(tphi)


fig = plt.figure(figsize=(12.5, 10.2))
gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.0], height_ratios=[0.85, 1.0], hspace=0.26, wspace=0.16, left=0.05,
                      right=0.98, top=0.93, bottom=0.06)


def step(ax, n, title, sub_):
    ax.set_title(f"{n} · {title}", loc="left", fontsize=11.5, fontweight="bold", color=INK, pad=18)
    ax.text(0, 1.01, sub_, transform=ax.transAxes, fontsize=9, color=INK2, va="bottom")


# ---------- 1. tracker in 3D ----------
# drawn in the track frame: beam axis horizontal, the track's azimuth pointing up (plot axes: z, across, along)
ax = fig.add_subplot(gs[0, 0], projection="3d", computed_zorder=False)
ax.set_title("1 · Tracker", loc="left", fontsize=11.5, fontweight="bold", color=INK)
th = np.linspace(0, 2 * np.pi, 120)


def p3(x, y, zz, **kw):
    u_, w_ = rot(np.asarray(x, float), np.asarray(y, float))
    return ax.plot(zz + 0 * u_, w_, u_, **kw)


for R in OT_R:
    for zz in (-OT_ZB, OT_ZB):
        p3(R * np.cos(th), R * np.sin(th), zz, c="#d9d7cf", lw=0.6)
for zz in OT_DZ:
    for sgn in (-1, 1):
        p3(110 * np.cos(th), 110 * np.sin(th), sgn * zz, c="#e4e2db", lw=0.5)
for a_ in np.linspace(0, 2 * np.pi, 16, endpoint=False):
    ax.plot([-265, 265], [110 * np.sin(a_)] * 2, [110 * np.cos(a_)] * 2, c="#e4e2db", lw=0.5)
for R in PIX_R:
    for zz in (-20, 20):
        p3(R * np.cos(th), R * np.sin(th), zz, c=INK2, lw=0.6)
    for a_ in np.linspace(0, 2 * np.pi, 8, endpoint=False):
        ax.plot([-20, 20], [R * np.sin(a_)] * 2, [R * np.cos(a_)] * 2, c=INK2, lw=0.4)
for zz in PIX_DZ:
    for sgn in (-1, 1):
        p3(16 * np.cos(th), 16 * np.sin(th), sgn * zz, c=INK2, lw=0.5)
rs = np.random.default_rng(1).choice(len(cl_all["x"]), 6000, replace=False)
uc, wc = rot(cl_all["x"][rs], cl_all["y"][rs])
ax.scatter(cl_all["z"][rs], wc, uc, s=0.4, c="#9c9a93", alpha=0.7, depthshade=False)
# the slice of panel 2: +-PHI_WIN around the track, following the track in z
rr = np.linspace(0, 112, 60)
zt = helix(rr)[2]
fan = [(zt[i], sg * rr[i] * np.sin(X.PHI_WIN), rr[i] * np.cos(X.PHI_WIN)) for sg in (-1, 1)
       for i in (range(len(rr)) if sg < 0 else range(len(rr) - 1, -1, -1))]
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ax.add_collection3d(Poly3DCollection([fan], facecolor=C_OT, alpha=0.13, edgecolor=C_OT, linewidth=0.6))
hx, hy, hz = helix(np.linspace(0, 108, 200))
hu, hw = rot(hx, hy)
ax.plot(hz, hw, hu, c=C_OT, lw=2.6)
ox, oy, oz = helix(np.array(OT_R))
ou, ow = rot(ox, oy)
ax.scatter(oz, ow, ou, s=18, c=C_OT, edgecolors="white", linewidths=0.6, depthshade=False)
ax.text(float(hz[-1]) + 12, float(hw[-1]), float(hu[-1]) + 4, "L1 track", color=INK, fontsize=9)
ax.text(30, 0, -40, "pixel detector", color=INK2, fontsize=8.5)
ax.set_box_aspect((2.4, 1, 1), zoom=1.5)
ax.set_xlim(-265, 265); ax.set_ylim(-112, 112); ax.set_zlim(-112, 112)
ax.view_init(elev=14, azim=-58)
ax.set_axis_off()
ax.text2D(0.02, 0.02, "Outer Tracker (light, schematic) · pixel layers (dark) · amber: the slice in 2\n"
          f"grey: 6,000 of the event's {len(cl_all['x']):,} pixel clusters (PU 200)", transform=ax.transAxes,
          fontsize=8.5, color=INK2)

# ---------- 2. the slice, transverse plane, true scale ----------
ax = fig.add_subplot(gs[0, 1])
step(ax, 2, "Seed: Outer Tracker L1 track", f"transverse slice, true scale · pT {tpt:.1f} GeV in a b jet of {jetpt:.0f} GeV")
wedge = np.linspace(-X.PHI_WIN, X.PHI_WIN, 60)
for R in OT_R:
    ax.plot(R * np.cos(wedge), R * np.sin(wedge), c="#d6d4cc", lw=3, solid_capstyle="butt")
for R in PIX_R:
    ax.plot(R * np.cos(wedge), R * np.sin(wedge), c=INK2, lw=1.2)
u_all, w_all = rot(sub["x"], sub["y"])
ax.scatter(u_all, w_all, s=1.2, c=C_PU, lw=0)
u_, w_ = rot(*helix(np.linspace(OT_R[0], 108, 100))[:2])
ax.plot(u_, w_, c=C_OT, lw=2.4, label="L1 track: fit to Outer Tracker stubs (d0 = 0)")
u_, w_ = rot(*helix(np.array(OT_R))[:2])
ax.scatter(u_, w_, s=26, c=C_OT, edgecolors="white", linewidths=0.8, zorder=5)
u_, w_ = rot(*helix(np.linspace(0, OT_R[0], 50))[:2])
ax.plot(u_, w_, c=C_OT, lw=1.6, ls=(0, (4, 2.5)), label="extrapolated into the pixel layers")
ax.add_patch(plt.Rectangle((-0.5, -2.5), 17, 5, fill=False, ec=INK, lw=1))
ax.annotate("zoomed in 3 and 4", (16.5, -2.5), (22, -10), fontsize=9, color=INK, ha="left", va="center",
            arrowprops=dict(arrowstyle="-", color=INK, lw=0.8))
ax.text(OT_R[-1] + 1, 7.5, "Outer Tracker\nlayers", fontsize=8.5, color=INK2, ha="right")
ax.text(8, 4, "pixel layers", fontsize=8.5, color=INK2, ha="center")
ax.set_aspect("equal")
ax.set_xlim(-2, 114); ax.set_ylim(-16, 30)
ax.set_xlabel("along the track [cm]"); ax.set_ylabel("across [cm]")
ax.legend(loc="upper left", fontsize=8.5)
ax.grid(False)

# ---------- 3 and 4. pixel layers: rotated frame, offset stretched ----------
# offset v [mm] from the prompt prediction at each cluster's radius; window |v| < WIN_RPHI, |z - z_pred| < WIN_Z
phi_pred = tphi - np.arcsin(np.clip(k * r / 2, -1, 1))
v = r * X.dphi(ph, phi_pred) * 10
zp = tz0 + cot * 2 * np.arcsin(np.clip(k * r / 2, -1, 1)) / k
inz = barrel & (abs(z - zp) < X.WIN_Z)
show = inz & (abs(v) < 4)
incand = np.zeros(len(r), bool)
incand[cand] = True
_, _, _, phi0 = X.fit(r[idx], ph[idx], z[idx], barrel[idx], k, tphi, cot)
rr = np.linspace(0, 16.5, 200)
vfit = (rr * X.dphi(phi0, tphi) + d0) * 10
W = X.WIN_RPHI * 10
for n, ax in ((3, fig.add_subplot(gs[1, 0])), (4, fig.add_subplot(gs[1, 1]))):
    for lo, hi in PIX_SPAN:
        ax.axvspan(lo, hi, color="#efeee9", lw=0, zorder=0)
    ax.axvline(0, c=INK2, lw=1, zorder=1)
    ax.text(0.15, 5.4, "beam line", fontsize=8.5, color=INK2, va="top")
    ax.axhline(0, c=C_OT, lw=1.6, ls=(0, (4, 2.5)), zorder=1)
    ax.plot([-0.3, 0.3], [0, 0], c=INK, lw=0)
    ax.set_xlim(-0.6, 16.5); ax.set_ylim(-4, 5.6)
    ax.set_xlabel("radius [cm]")
    ax.grid(False)
    if n == 3:
        step(ax, 3, "Extend: search window in each pixel layer",
             f"offset across the track stretched ×10 (mm vs cm) · only clusters within {X.WIN_Z:.1f} cm in z")
        for lo, hi in PIX_SPAN:
            ax.add_patch(plt.Rectangle((lo - 0.15, -W), hi - lo + 0.3, 2 * W, fc="#fbe3d6", ec=C_EXT, lw=1, zorder=1))
        ax.scatter(r[show & ~incand], v[show & ~incand], s=9, c=C_PU, lw=0, zorder=2, label="pileup clusters near the track")
        ax.scatter(r[show & incand], v[show & incand], s=22, c=INK2, lw=0, zorder=3,
                   label=f"candidates in the windows ({(show & incand).sum()})")
        ax.plot([], [], c=C_OT, lw=1.6, ls=(0, (4, 2.5)), label="L1 track prediction (d0 = 0)")
        ax.plot([], [], marker="s", ms=9, c="#fbe3d6", mec=C_EXT, ls="", label=f"window ±{W:.1f} mm")
        ax.set_ylabel("offset from the L1 track prediction [mm]")
        ax.legend(loc="upper right", fontsize=8.5, ncol=2)
    else:
        step(ax, 4, "Refit: d0 and z0 from the picked pixel hits",
             f"best of all one-hit-per-layer combinations (χ²) · {nh} hits · z0 {tz0:.2f} → {z0:.2f} cm")
        ax.scatter(r[show & incand], v[show & incand], s=12, c=C_PU, lw=0, zorder=2, label="other candidates")
        ax.scatter(r[on & barrel], v[on & barrel], s=110, facecolors="none", edgecolors=C_HLT, lw=1.6, zorder=3,
                   label="hits of the HLT pixel track (reference)")
        ax.scatter(r[idx], v[idx], s=30, c=C_EXT, zorder=4, label="hits picked")
        ax.plot(rr, vfit, c=C_EXT, lw=2, zorder=3, label="pixel refit")
        ax.plot([], [], c=C_OT, lw=1.6, ls=(0, (4, 2.5)), label="L1 track (d0 = 0)")
        ax.annotate("", (0, d0 * 10), (0, 0), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.2, shrinkA=0, shrinkB=0))
        ax.text(0.3, -0.3, f"d0 = {abs(d0) * 1e4:.0f} µm\nHLT: {abs(ref_dxy) * 1e4:.0f} µm", fontsize=9.5, color=INK,
                va="top", fontweight="bold")
        ax.legend(loc="upper right", fontsize=8.5, ncol=2)
fig.suptitle("L1 track extended into the pixel detector (HH→4b, PU 200)", x=0.04, ha="left", fontsize=12.5, color=INK)
fig.savefig(out, dpi=140)
print(f"event {ie + start}, track {t}: pT {tpt:.1f}, d0 refit {d0 * 1e4:.0f} um (HLT {ref_dxy * 1e4:.0f}), {nh} hits, "
      f"candidates {len(cand)}, clusters {len(cl_all['x'])}")

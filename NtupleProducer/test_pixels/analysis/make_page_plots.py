#!/usr/bin/env python3
"""Plots for the four-tab summary page (plots_page/).

    python3 make_page_plots.py
Inputs: curves.json + curves_flags.npz (direct_curves.py), tag_chain.json (tag_compare.py), genmhh dumps and the
Run-3 kappa_lambda m_HH shapes (as kl_direct.py), l1ext_val/scan_0.json (association validation), one HH4b ntuple
for the OT-only d0 comparison. Colours keep one meaning across plots: grey = planned menu alone (current-style),
blue = + today's L1 NN seed (planned), orange = + L1 tracks with pixel hits, aqua = + HLT pixel tracks.
"""
import glob
import json
import re

import awkward as ak
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import uproot

import l1ext as X

OUT = "plots_page"
C = {"menu": "#9a9890", "NN": "#2a78d6", "L1 pixel": "#eb6834", "HLT pixel": "#1baf7a", "perfect": "#0b0b0b",
     "OT only": "#eda100", "offline": "#6250d6", "missed": "#e34948"}
INK, INK2 = "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.grid": True, "grid.color": "#ecebe7", "grid.linewidth": 0.8,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False})
ADD = "2.5"

curves = json.load(open("curves.json"))
fl = dict(np.load("curves_flags.npz"))
odd = fl["odd"]


# ---------- kappa_lambda weights from gen m_HH (as kl_direct.py) ----------
g = {k: np.concatenate([np.load(f)[k] for f in sorted(glob.glob("/scratch/submit/cms/novaka/l1pixels/genmhh/mhh_*.npz"))])
     for k in ("lumi", "event", "mhh")}
pos = {(l, e): i for i, (l, e) in enumerate(zip(g["lumi"], g["event"]))}
mhh = np.array([g["mhh"][pos[(l, e)]] for l, e in zip(fl["lumi"], fl["event"])])
nano = {}
for f in sorted(glob.glob("klreweight/nano_mhh_kl*.npz")):
    m = np.load(f)["mhh"]
    nano[float(re.search(r"kl(\d+p\d+)", f).group(1).replace("p", "."))] = m[m > 0]
bins = np.concatenate([np.arange(240, 600, 20), np.arange(600, 800, 50), [800, 1000, 1300, 5000]])
dens = {kl: np.histogram(m, bins)[0] / len(m) for kl, m in nano.items()}
ib = np.clip(np.digitize(mhh, bins) - 1, 0, len(bins) - 2)
wkl = {1.0: np.ones(len(mhh)), 5.0: np.where(dens[1.0] > 0, dens[5.0] / np.maximum(dens[1.0], 1e-12), 0.0)[ib]}

trig = {"menu": fl["menu"], "NN": fl[f"NN|menu|{ADD}"], "L1 pixel": fl[f"L1 pixel|menu|{ADD}"],
        "perfect": fl[f"perfect|menu|{ADD}"]}


# ---------- 1. cutflow: L1 efficiency on all events vs on offline-selected events ----------
def frac(sel, t=None, w=None):
    w = np.ones(len(sel)) if w is None else w
    m = sel & odd & (t if t is not None else True)
    return 100 * (w * m).sum() / (w * odd).sum()


def tint(c, f=0.6):
    rgb = np.array(matplotlib.colors.to_rgb(c))
    return tuple(rgb + (1 - rgb) * f)


# Same seeds, two denominators: all SM events vs the 7.9% passing offline 4b + 3b. The trigger misses mostly soft events
# the offline selection drops anyway, so its efficiency on the analysed events is much higher.
f_off = frac(fl["offline_4b3b"])
rows = [("planned menu alone\n(current-style)", "menu", C["menu"]), ("+ today's L1 NN seed\n(planned)", "NN", C["NN"]),
        ("+ L1 tracks with\npixel hits", "L1 pixel", C["L1 pixel"]), ("+ perfect L1 b-tag\n(ceiling)", "perfect", "#6d6b64")]
fig, ax = plt.subplots(figsize=(11, 4.4))
for yy, (lab, k, col) in zip(np.arange(len(rows))[::-1], rows):
    for dy, sel, c, scale in ((0.2, fl["all"], tint(col), 1.0), (-0.2, fl["offline_4b3b"], col, 100 / f_off)):
        v = frac(sel, trig[k]) * scale
        ax.barh(yy + dy, v, color=c, height=0.36, edgecolor="white", linewidth=1.5)
        txt = f"{v:.1f}%"
        if k in ("L1 pixel", "perfect"):
            txt += f"   ×{v / (frac(sel, trig['NN']) * scale):.2f} vs NN"
        ax.text(v + 0.8, yy + dy, txt, va="center", fontsize=9, color=INK if dy < 0 else INK2,
                fontweight="bold" if dy < 0 else "normal")
ax.set_yticks(np.arange(len(rows))[::-1], [r[0] for r in rows], fontsize=9)
ax.set_xlim(0, 118)
ax.set_xticks(range(0, 101, 20))
ax.set_axisbelow(True)
ax.set_xlabel("fraction kept by L1 [%]")
ax.grid(axis="y", visible=False)
ax.legend(handles=[matplotlib.patches.Patch(color=tint(C["menu"]), label="of all SM HH→4b events"),
                   matplotlib.patches.Patch(color=C["menu"],
                                            label=f"of events passing the offline 4b + 3b selection ({f_off:.1f}% of all)")],
          loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=9, handlelength=1.6)
fig.suptitle(f"SM HH→4b kept by L1: same seeds, two denominators (seeds at +{ADD} kHz on top of the planned menu)",
             fontsize=10.5, color=INK, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(f"{OUT}/cutflow.png", dpi=150)
plt.close(fig)


# ---------- 2. m_HH: what is triggered, what is added, what is missed ----------
mb = np.concatenate([np.arange(250, 700, 25), [700, 800, 1000]])
fig, axs = plt.subplots(2, 2, figsize=(11, 6.4), sharex=True)
for col, kl in enumerate((1.0, 5.0)):
    for row, (lab, sel) in enumerate((("all events (trigger level)", fl["all"]), ("offline 4b + 3b selected", fl["offline_4b3b"]))):
        ax = axs[row, col]
        w = wkl[kl] * (sel & odd)
        parts = [("planned menu alone", trig["menu"], C["menu"]),
                 ("added by the NN seed", trig["NN"] & ~trig["menu"], C["NN"]),
                 ("added by the pixel seed", trig["L1 pixel"] & ~trig["NN"], C["L1 pixel"]),
                 ("missed even with pixels", ~trig["L1 pixel"] & ~trig["NN"], "#e8e6e0")]
        bottom = np.zeros(len(mb) - 1)
        tot = (w).sum()
        for name, m, colr in parts:
            h, _ = np.histogram(np.clip(mhh, mb[0], mb[-1] - 1), mb, weights=w * m)
            h = h / tot / np.diff(mb) * 100
            ax.bar(mb[:-1], h, width=np.diff(mb), bottom=bottom, align="edge", color=colr, edgecolor="white", linewidth=1,
                   label=f"{name} ({100 * (w * m).sum() / tot:.1f}%)")
            bottom += h
        ax.set_title(f"κλ = {kl:g}, {lab}", fontsize=10, color=INK, loc="left")
        ax.legend(fontsize=8, loc="upper right")
        ax.grid(axis="x", visible=False)
        if col == 0:
            ax.set_ylabel("fraction per GeV × 100")
        if row == 1:
            ax.set_xlabel("generator m_HH [GeV]")
fig.suptitle("Which HH events each trigger level keeps (+2.5 kHz seeds on top of the planned menu; odd half)",
             fontsize=10.5, color=INK, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(f"{OUT}/mhh_categories.png", dpi=150)
plt.close(fig)


# ---------- 3. rate: efficiency vs rate, and the rate saved at equal efficiency ----------
fig, axs = plt.subplots(1, 2, figsize=(11, 4))
for ax, (sec, rk, title) in zip(axs, (("on_top_of_menu", "added_rate_khz", "Added on top of the planned menu (19 kHz)"),
                                      ("standalone", "rate_khz", "Standalone HT + b-tag seed"))):
    for tag in ("NN", "HLT pixel", "L1 pixel"):
        rows = sorted(curves[sec][tag], key=lambda r: r[rk])
        x = [r[rk] for r in rows]
        y = np.maximum.accumulate([100 * r["eff"]["offline_4b3b"] for r in rows])
        ax.plot(x, y, "-o", color=C[tag], lw=2, ms=4.5, label={"NN": "today's L1 NN", "HLT pixel": "HLT pixel tracks",
                                                                "L1 pixel": "L1 tracks + pixel hits"}[tag])
    if sec == "on_top_of_menu":
        ax.axhline(100 * curves["menu"]["eff"]["offline_4b3b"], color=C["menu"], ls=":", lw=1.5)
        ax.text(0.3, 100 * curves["menu"]["eff"]["offline_4b3b"] + 0.4, "planned menu alone", color=INK2, fontsize=8, ha="left")
        ax.set_xlim(0, 16)
        ax.set_ylim(83, 100.5)
        ax.annotate("", xy=(0.4, 92.6), xytext=(2.3, 92.6), arrowprops=dict(arrowstyle="->", color=INK, lw=1.2))
        ax.text(2.5, 92.0, "same efficiency at ~0.3–0.4 kHz\ninstead of 2.3 kHz", fontsize=8, color=INK, va="top")
    else:
        ax.set_xlim(0, 32)
        ax.annotate("", xy=(2.7, 80.6), xytext=(9.6, 80.6), arrowprops=dict(arrowstyle="->", color=INK, lw=1.2))
        ax.text(10, 80.2, "NN at 9.6 kHz = pixels at 2.7 kHz", fontsize=8, color=INK, va="center")
    ax.set_xlabel("L1 rate [kHz]" if sec == "standalone" else "added L1 rate [kHz]")
    ax.set_ylabel("efficiency, offline 4b + 3b SM events [%]")
    ax.set_title(title, fontsize=10, color=INK, loc="left")
    ax.legend(fontsize=8.5, loc="lower right")
fig.suptitle("The same signal for much less rate: efficiency vs L1 rate (2.0M minimum-bias events)", fontsize=10.5,
             color=INK, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(f"{OUT}/rate_curves.png", dpi=150)
plt.close(fig)


# ---------- 4. ROC chain ----------
tc = json.load(open("tag_chain.json"))
fig, ax = plt.subplots(figsize=(6.4, 4.6))
spec = [("L1 NN", "today's L1 NN (baseline)", C["NN"], "-"), ("OT only", "+ Outer Tracker displaced tracks", C["OT only"], "-"),
        ("L1 + pixel", "+ L1 tracks with pixel hits", C["L1 pixel"], "-"), ("HLT pixel", "+ HLT pixel tracks", C["HLT pixel"], "-"),
        ("offline UParT", "offline UParT (other jets; reference)", C["offline"], "--")]
for key, lab, col, ls in spec:
    r = tc[key]
    ax.plot(np.array(r["roc_beff"]) * 100, r["roc_mistag"], ls, color=col, lw=2,
            label=f"{lab}: {100 * r['b_at_1pct']:.0f}%")
ax.set_yscale("log")
ax.set_ylim(1e-3, 1)
ax.set_xlim(0, 100)
ax.axhline(0.01, color="#c3c2b7", lw=1, ls=":")
ax.set_xlabel("b-jet efficiency [%]")
ax.set_ylabel("light-jet mistag rate (QCD)")
ax.set_title("Per-jet b tagging; legend: b efficiency at 1% mistag", fontsize=10, color=INK, loc="left")
ax.legend(fontsize=8, loc="lower right")
fig.tight_layout()
fig.savefig(f"{OUT}/roc_chain.png", dpi=150)
plt.close(fig)


# ---------- 5. d0 vs HLT: Outer Tracker alone vs with pixel hits ----------
val = json.load(open("l1ext_val/scan_0.json"))["rows"]
pix = np.array([(r["d0"] - r["ref_dxy"]) * 1e4 for r in val if r.get("ext") and "ref_dxy" in r and "d0" in r])
f = sorted(glob.glob("/scratch/submit/cms/novaka/l1pixels/local_v3/perfNano_HH4b_*.root"))[0]
a = uproot.open(f)["Events"].arrays(filter_name=["L1TracksExt_*", "PixelTracks_pt", "PixelTracks_eta", "PixelTracks_phi",
                                                "PixelTracks_dxyBS"], entry_stop=200)
ot = []
for e in a:
    tpt, teta, tphi, td0 = (ak.to_numpy(e[f"L1TracksExt_{k}"]) for k in ("pt", "eta", "phi", "d0"))
    ppt, peta, pphi, pd = (ak.to_numpy(e[f"PixelTracks_{k}"]) for k in ("pt", "eta", "phi", "dxyBS"))
    for t in np.where((tpt > 2) & (abs(td0) < 1))[0]:
        d = np.hypot(peta - teta[t], X.dphi(pphi, tphi[t]))
        ok = (d < 0.02) & (abs(ppt - tpt[t]) / tpt[t] < 0.3)
        if ok.any():
            ot.append((-td0[t] - pd[np.where(ok)[0][np.argmin(d[ok])]]) * 1e4)
ot = np.array(ot)
fig, ax = plt.subplots(figsize=(6.4, 4))
hb = np.linspace(-1500, 1500, 121)
mad = lambda x: 1.4826 * np.median(abs(x - np.median(x)))
ax.hist(np.clip(ot, hb[0], hb[-1]), hb, density=True, histtype="step", lw=2, color=C["OT only"],
        label=f"Outer Tracker only (displaced L1 tracks): {mad(ot):.0f} µm")
ax.hist(np.clip(pix, hb[0], hb[-1]), hb, density=True, histtype="step", lw=2, color=C["L1 pixel"],
        label=f"L1 track + pixel hits: {mad(pix):.0f} µm")
ax.set_yscale("log")
ax.set_xlabel("d0 − d0(HLT pixel track) [µm]")
ax.set_ylabel("tracks (normalised)")
ax.set_title("Impact parameter vs HLT pixel tracks (pT > 2 GeV; legend: robust width)", fontsize=10, color=INK, loc="left")
ax.legend(fontsize=8, loc="upper right")
fig.tight_layout()
fig.savefig(f"{OUT}/d0_resolution.png", dpi=150)
plt.close(fig)
print("plots written to", OUT, "| OT-only tracks", len(ot), "pixel-extended", len(pix))


# ---------- 6. charm tagging: c vs light and c vs b, with and without pixels (ctag_compare.py) ----------
ct = json.load(open("ctag_chain.json"))
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
for ax, (task, bkg) in zip(axs, (("CvsL", "light-jet"), ("CvsB", "b-jet"))):
    for tag, col, ls, lab in (("L1 NN", C["NN"], "-", "today's L1 NN"), ("OT only", C["OT only"], "-", "+ Outer Tracker displaced tracks"),
                              ("L1 + pixel", C["L1 pixel"], "-", "+ L1 tracks with pixel hits"), ("HLT pixel", C["HLT pixel"], "-", "+ HLT pixel tracks")):
        r = ct[task][tag]
        lo = [k for k in r if k.startswith("c_at_")]
        ax.plot(np.array(r["roc_ceff"]) * 100, r["roc_mistag"], c=col, ls=ls, lw=2.2,
                label=f"{lab}: {100 * r[lo[1]]:.0f}%")
    ref = 0.1 if task == "CvsL" else 0.3
    ax.axhline(ref, c="#b0aea6", lw=0.8, ls=":")
    ax.set_yscale("log")
    ax.set_xlim(0, 100)
    ax.set_ylim(1e-2 if task == "CvsL" else 3e-2, 1)
    ax.set_xlabel("c-jet efficiency [%]")
    ax.set_ylabel(f"{bkg} mistag rate (QCD)")
    ax.set_title(f"c vs {'light' if task == 'CvsL' else 'b'}; legend: c efficiency at {int(ref * 100)}% {bkg} mistag",
                 loc="left", fontsize=10, color=INK)
    ax.legend(loc="lower right", fontsize=8.5)
fig.suptitle("L1 charm tagging needs pixels: QCD jets (L1 jets pT > 15 GeV, |eta| < 2.4)", fontsize=10.5, color=INK, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(f"{OUT}/ctag_roc.png", dpi=150)
plt.close(fig)

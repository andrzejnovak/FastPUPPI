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
import os
import re

import awkward as ak
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import uproot

import l1ext as X

OUT = "plots_page"
V2DIR = "/scratch/submit/cms/novaka/l1pixels/derived/analysis_v2"


def inp(name):
    """Tagger-dependent inputs: with PIXSUM=v2, the recalibrated-summary outputs of run_v2.sh."""
    if os.environ.get("PIXSUM", "v1") != "v2":
        return name
    stem, ext = os.path.splitext(name)
    return f"{V2DIR}/{stem.replace('_flags', '')}_v2{'_flags' if stem.endswith('_flags') else ''}{ext}"

C = {"menu": "#9a9890", "NN": "#2a78d6", "L1 pixel": "#eb6834", "HLT pixel": "#1baf7a", "perfect": "#0b0b0b",
     "OT only": "#eda100", "offline": "#6250d6", "missed": "#e34948"}
INK, INK2 = "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.grid": True, "grid.color": "#ecebe7", "grid.linewidth": 0.8,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False})
ADD = "2.5"

curves = json.load(open(inp("curves.json")))
fl = dict(np.load(inp("curves_flags.npz")))
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
tc = json.load(open(inp("tag_chain.json")))
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


# ---------- 7. is the trigger the bottleneck? boosted ggH vs Higgs pT, ZH(nunu) vs generator MET ----------
FJ = "/scratch/submit/cms/novaka/l1pixels/derived/fatjet_parts"
zh = json.load(open("zh_met.json"))
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
edges = np.array([100, 150, 200, 250, 300, 400, 600])
for name, col, lab in (("ggHcc_pt150", C["L1 pixel"], "ggH, H→cc"), ("ggHbb_pt150", C["NN"], "ggH, H→bb")):
    E = np.concatenate([np.load(f)["ev"] for f in sorted(glob.glob(f"{FJ}/{name}_*.npz"))])
    hpt, menu = E[:, 2], (E[:, 6] > 0) | (E[:, 7] > 0)
    idx = np.digitize(hpt, edges) - 1
    ok = (idx >= 0) & (idx < len(edges) - 1)
    n = np.bincount(idx[ok], minlength=len(edges) - 1)
    k = np.bincount(idx[ok], weights=menu[ok], minlength=len(edges) - 1)
    eff = k / np.maximum(n, 1)
    err = np.sqrt(eff * (1 - eff) / np.maximum(n, 1))
    mid = 0.5 * (edges[1:] + edges[:-1])
    axs[0].errorbar(mid, eff * 100, yerr=err * 100, xerr=0.5 * np.diff(edges), fmt="o", ms=5, c=col, lw=1.6,
                    label=f"{lab} ({len(E)} events)")
axs[0].set_xlabel("Higgs pT (generator jets of the Higgs flavour within ΔR < 0.8) [GeV]")
axs[0].set_ylabel("kept by the planned menu [%]")
axs[0].set_title("Boosted ggH: SingleJet230 or HT450 already fire", loc="left", fontsize=10, color=INK)
for name, col, lab in (("ZHnunu_cc", C["L1 pixel"], "ZH(νν), H→cc"), ("ZHnunu_bb", C["NN"], "ZH(νν), H→bb")):
    rows = [r for r in zh[name]["by_genmet"] if r["n"]]
    lo = np.array([r["genmet"][0] for r in rows]); hi = np.array([min(r["genmet"][1], 600) for r in rows])
    for key, fmt, mfc, sub in (("menu", "o", col, "menu"), ("MET200", "s", "white", "PuppiMET200 alone")):
        e = np.array([r[key] for r in rows]); n = np.array([r["n"] for r in rows])
        axs[1].errorbar(0.5 * (lo + hi), e * 100, yerr=100 * np.sqrt(e * (1 - e) / n), xerr=0.5 * (hi - lo), fmt=fmt, ms=5,
                        c=col, mfc=mfc, lw=1.4, label=f"{lab}: {sub}")
axs[1].axvline(150, c="#b0aea6", lw=0.8, ls=":")
axs[1].text(155, 8, "typical 0-lepton\noffline cut", fontsize=8, color=INK2)
axs[1].set_xlabel("generator MET (Z pT) [GeV]")
axs[1].set_title("ZH(νν): MET seeds already fire above 150 GeV", loc="left", fontsize=10, color=INK)
for ax in axs:
    ax.set_ylim(0, 105)
    ax.set_xlim(0 if ax is axs[1] else 100, 600)
    ax.legend(loc="lower right", fontsize=8.5)
fig.suptitle("Where L1 is not the bottleneck: private Phase-2 samples, PU 200 (~5k events per sample)", fontsize=10.5,
             color=INK, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(f"{OUT}/menu_vs_pt.png", dpi=150)
plt.close(fig)


# ---------- 8. VBF H -> cc / bb: looser VBF seed + two flavour-tagged jets on top of the menu (vbf_ctag.py) ----------
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), sharey=False)
for ax, (fn, flav) in zip(axs, (("vbf_ctag_cc.json", "cc"), ("vbf_ctag_bb.json", "bb"))):
    v = json.load(open(fn))
    base = v["base"]
    n_odd = base["n_sig_acc"] / 2
    ax.axhline(100 * base["menu_eff_odd"], c=C["menu"], lw=1.6, ls="--", label=f"planned menu: {100 * base['menu_eff_odd']:.0f}%")
    q = "c" if flav == "cc" else "b"
    for tag, col, lab in (("none", INK2, "looser VBF seed, no tag"), ("NN", C["NN"], f"+ two {q}-tagged jets, today's NN"),
                          ("pixel", C["L1 pixel"], f"+ two {q}-tagged jets, L1 tracks with pixel hits")):
        rows = sorted(v["on_top_of_menu"][tag].values(), key=lambda r: r["added_rate_khz_odd"])
        x = np.array([r["added_rate_khz_odd"] for r in rows]); y = np.array([r["eff_odd"] for r in rows])
        nmb = np.array([max(r["n_mb_pass_odd_not_menu"], 1) for r in rows])
        ax.errorbar(x, 100 * y, xerr=x / np.sqrt(nmb), yerr=100 * np.sqrt(y * (1 - y) / n_odd), fmt="o-", ms=5, lw=1.8,
                    c=col, mfc=col if tag != "none" else "white", label=lab)
    ax.set_xlim(0, 6.5)
    ax.set_xlabel("added L1 rate on top of the planned menu [kHz]")
    ax.set_ylabel(f"VBF H→{flav} in acceptance kept [%]")
    ax.set_title(f"VBF H→{flav}", loc="left", fontsize=10, color=INK)
    ax.set_ylim(100 * base["menu_eff_odd"] - 1.5, 100 * base["menu_eff_odd"] + 14)
    ax.legend(loc="upper left", fontsize=8.5)
fig.suptitle("VBF H→cc / bb: what a flavour-tagged VBF seed adds (working points chosen on even events, shown on odd; "
             "PU 200 minimum bias)", fontsize=10.5, color=INK, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(f"{OUT}/vbf_tag_rate.png", dpi=150)
plt.close(fig)


# ---------- 9. headline: efficiency vs generator m_HH, with where the kappa_lambda information lives ----------
# kappa_lambda information per m_HH bin near the SM: s_i(k) = sigma(k)/sigma(1) * shape_k[i], quadratic in k through
# k = 0, 1, 2.45; Fisher information (d s_i / d k)^2 / s_i (signal-dominated). Per-event weight (d ln s_i / d k)^2.
import os
XS = lambda k: (70.38 - 51.85 * k + 11.42 * k ** 2) / (70.38 - 51.85 + 11.42)  # ggF HH, LHC HH WG parameterisation
ks = np.array([0.0, 1.0, 2.45])
S3 = np.array([XS(k) * dens[k] for k in ks])
cf = np.array([np.polyfit(ks, S3[:, i], 2) for i in range(S3.shape[1])])
ds, s1 = 2 * cf[:, 0] + cf[:, 1], S3[1]
info = np.where(s1 > 0, ds ** 2 / np.maximum(s1, 1e-12), 0.0)
w_info = (ds / np.maximum(s1, 1e-12))[ib] ** 2
ctl = dict(np.load("ht_control_flags.npz")) if os.path.exists("ht_control_flags.npz") else None
if ctl is not None:
    cpos = {(l, e): i for i, (l, e) in enumerate(zip(ctl["lumi"], ctl["event"]))}
    cidx = np.array([cpos[(l, e)] for l, e in zip(fl["lumi"], fl["event"])])
    trig_ctl = ctl[f"HTlow|menu|{ADD}"][cidx]
lines = [("menu", fl["menu"], C["menu"], "-", "Run-3-style menu (no L1 b tag)")]
if ctl is not None:
    lines.append(("HT", trig_ctl, INK2, ":", f"+{ADD} kHz on lower HT cuts, no tag"))
lines += [("NN", fl[f"NN|menu|{ADD}"], C["NN"], "-", f"+{ADD} kHz seed, today's L1 NN"),
          ("L1 pixel", fl[f"L1 pixel|menu|{ADD}"], C["L1 pixel"], "-", f"+{ADD} kHz seed, L1 tracks + pixel hits"),
          ("perfect", fl[f"perfect|menu|{ADD}"], C["perfect"], "--", f"+{ADD} kHz seed, perfect b tag")]
fig = plt.figure(figsize=(11, 7.2))
gs = fig.add_gridspec(3, 2, height_ratios=[1, 3, 1.4], hspace=0.08, wspace=0.18)
for col, (title, den, mb_) in enumerate((("Trigger level: all SM HH→4b events", fl["all"], [250, 300, 350, 400, 450, 500, 600, 800, 1200]),
                                          ("Analysis level: events passing offline 4b + 3b", fl["offline_4b3b"], [250, 350, 400, 450, 550, 700, 1200]))):
    mb_ = np.array(mb_)
    ax0, ax1, ax2 = (fig.add_subplot(gs[r, col]) for r in range(3))
    # where the information is (share per GeV, rebinned)
    centers = 0.5 * (bins[1:] + bins[:-1])
    share = np.histogram(centers, mb_, weights=info)[0] / info.sum()
    ax0.bar(mb_[:-1], 100 * share, width=np.diff(mb_), align="edge", color="#d9d6cc", edgecolor="white", lw=2)
    ax0.set_ylabel("κλ info [%]", fontsize=8.5)
    ax0.set_title(title, loc="left", fontsize=10, color=INK)
    sel = odd & den
    effs = {}
    for name, flag, c, ls, lab in lines:
        k = np.histogram(np.clip(mhh[sel], mb_[0], mb_[-1] - 1), mb_, weights=flag[sel].astype(float))[0]
        n = np.histogram(np.clip(mhh[sel], mb_[0], mb_[-1] - 1), mb_)[0]
        e = k / np.maximum(n, 1)
        effs[name] = (e, n)
        x = 0.5 * (mb_[1:] + mb_[:-1])
        if name == "perfect":
            ax1.plot(x, 100 * e, c=c, lw=1.1, ls="--", alpha=0.7, label=lab)
            continue
        ax1.errorbar(x, 100 * e, yerr=100 * np.sqrt(e * (1 - e) / np.maximum(n, 1)), xerr=0.5 * np.diff(mb_), fmt="o",
                     ms=4.5, c=c, lw=2 if name in ("L1 pixel", "NN") else 1.4, ls=ls, label=lab)
    ax1.set_ylim(0, 105)
    ax1.set_ylabel("kept by L1 [%]")
    for name, c in (("L1 pixel", C["L1 pixel"]),):
        x = 0.5 * (mb_[1:] + mb_[:-1])
        rel = lambda e, n: np.sqrt((1 - e) / np.maximum(e * n, 1))  # relative binomial error (ratio errors added in quadrature: conservative)
        e1, n1 = effs[name]
        for ref, fmt, mfc, lw, lab in (("NN", "o", c, 1.8, "pixel seed / NN seed"), ("menu", "s", "white", 1.2, "pixel seed / Run-3-style")):
            e0 = effs[ref][0]
            r = e1 / np.maximum(e0, 1e-6)
            ax2.errorbar(x, r, xerr=0.5 * np.diff(mb_), yerr=r * np.hypot(rel(e1, n1), rel(e0, n1)), fmt=fmt, ms=4.5, c=c, mfc=mfc,
                         lw=lw, label=lab)
    ax2.axhline(1, c="#b0aea6", lw=0.8)
    ax2.set_ylim(0.9, 2.8 if col == 0 else 2.8)
    ax2.set_ylabel("ratio")
    ax2.set_xlabel("generator m$_{HH}$ [GeV]")
    for ax in (ax0, ax1, ax2):
        ax.set_xlim(mb_[0], mb_[-1])
        ax.axvspan(mb_[0], 400, color="#eb6834", alpha=0.05, lw=0)
    ax0.tick_params(labelbottom=False); ax1.tick_params(labelbottom=False)
    if col == 0:
        ax1.legend(loc="lower right", fontsize=8)
        ax2.legend(loc="upper right", fontsize=8)
    lo_share = 100 * info[bins[:-1] < 400].sum() / info.sum()
    ax0.text(410, ax0.get_ylim()[1] * 0.85, f"← m$_{{HH}}$ < 400 GeV: {lo_share:.0f}% of the κλ information near the SM",
             fontsize=8.5, color=INK2, va="top")
fig.suptitle(f"Where pixels pay: the low-m$_{{HH}}$ region that measures κλ (SM HH→4b, odd events; seeds at +{ADD} kHz on top of the menu)",
             fontsize=10.5, color=INK, x=0.01, ha="left")
fig.savefig(f"{OUT}/mhh_eff.png", dpi=150, bbox_inches="tight")
plt.close(fig)
for den_name in ("all", "offline_4b3b"):
    s = odd & fl[den_name]
    print(f"kl-information-weighted efficiency [{den_name}]: " +
          "  ".join(f"{name} {100 * (w_info[s] * flag[s]).sum() / w_info[s].sum():.1f}" for name, flag, *_ in lines))


# ---------- 10. thesis-style: efficiency vs offline HT and vs offline b-tag sum (UParT, 4 leading jets) ----------
def offline_event_vars():
    parts = [dict(np.load(f)) for f in sorted(glob.glob("/scratch/submit/cms/novaka/l1pixels/offline/HH4b_*.npz"))]
    lumi = np.concatenate([p["lumi"] for p in parts]); event = np.concatenate([p["event"] for p in parts])
    nj = np.concatenate([p["njet"] for p in parts])
    j = {k: np.concatenate([p[k] for p in parts]) for k in ("pt", "eta", "upart", "nconst", "nhf", "nemf")}
    good = (j["pt"] > 30) & (abs(j["eta"]) < 2.5) & (j["nconst"] > 1) & (j["nhf"] < 0.9) & (j["nemf"] < 0.9)
    evi = np.repeat(np.arange(len(nj)), nj)
    ht = np.bincount(evi[good], weights=j["pt"][good], minlength=len(nj))
    # 4 leading good jets by pT (dumps are pT-ordered within an event)
    rank = np.zeros(len(evi), int)
    gi = np.where(good)[0]
    first = np.r_[0, np.cumsum(np.bincount(evi[gi], minlength=len(nj)))[:-1]]
    rank[gi] = np.arange(len(gi)) - first[evi[gi]]
    lead4 = good & (rank < 4)
    bsum = np.bincount(evi[lead4], weights=j["upart"][lead4], minlength=len(nj))
    pos_ = {(l, e): i for i, (l, e) in enumerate(zip(lumi, event))}
    idx = np.array([pos_.get((l, e), -1) for l, e in zip(fl["lumi"], fl["event"])])
    ok = idx >= 0
    return np.where(ok, ht[np.maximum(idx, 0)], np.nan), np.where(ok, bsum[np.maximum(idx, 0)], np.nan), ok


oht, obsum, has_off = offline_event_vars()
print("offline variables matched for", has_off.sum(), "of", len(has_off), "HH events")
lines10 = [l for l in lines if l[0] != "HT"] if ctl is None else lines
fig = plt.figure(figsize=(13, 6.2))
gs = fig.add_gridspec(3, 3, height_ratios=[1, 3, 1.4], hspace=0.08, wspace=0.22)
panels = (("Offline H$_T$ [GeV]", oht, odd & has_off, np.arange(0, 820, 50), "All SM HH→4b events"),
          ("Σ$_{4\\ jets}$ offline UParT b score", obsum, odd & has_off, np.linspace(0, 4, 11), "All SM HH→4b events"),
          ("Σ$_{4\\ jets}$ offline UParT b score", obsum, odd & has_off & (mhh < 400), np.linspace(0, 4, 9),
           "m$_{HH}$ < 400 GeV (the κλ region)"))
for col, (xlab, var, base_sel, edges, title) in enumerate(panels):
    ax0, ax1, ax2 = (fig.add_subplot(gs[r, col]) for r in range(3))
    v = np.clip(var, edges[0], edges[-1] - 1e-6)
    n_all = np.histogram(v[base_sel], edges)[0]
    ax0.bar(edges[:-1], n_all / n_all.sum() * 100, width=np.diff(edges), align="edge", color="#d9d6cc", edgecolor="white", lw=1.5)
    ax0.set_ylabel("events [%]", fontsize=8.5)
    ax0.set_title(title, loc="left", fontsize=10, color=INK)
    x = 0.5 * (edges[1:] + edges[:-1])
    effs = {}
    for name, flag, c, ls, lab in lines10:
        k = np.histogram(v[base_sel], edges, weights=flag[base_sel].astype(float))[0]
        e = k / np.maximum(n_all, 1)
        effs[name] = e
        if name == "perfect":
            ax1.plot(x, 100 * e, c=c, lw=1.1, ls="--", alpha=0.7, label=lab)
            continue
        ax1.errorbar(x, 100 * e, yerr=100 * np.sqrt(e * (1 - e) / np.maximum(n_all, 1)), xerr=0.5 * np.diff(edges),
                     fmt="o", ms=4, c=c, lw=2 if name in ("L1 pixel", "NN") else 1.3, ls=ls, label=lab)
    rel = lambda e: np.sqrt((1 - e) / np.maximum(e * n_all, 1))
    for ref, fmt, mfc, lab in (("NN", "o", C["L1 pixel"], "pixel seed / NN seed"), ("menu", "s", "white", "pixel seed / Run-3-style")):
        r = effs["L1 pixel"] / np.maximum(effs[ref], 1e-6)
        ax2.errorbar(x, r, xerr=0.5 * np.diff(edges), yerr=r * np.hypot(rel(effs["L1 pixel"]), rel(effs[ref])), fmt=fmt, ms=4,
                     c=C["L1 pixel"], mfc=mfc, lw=1.4, label=lab)
    ax2.axhline(1, c="#b0aea6", lw=0.8)
    ax2.set_ylim(0.8, 6 if col == 0 else 2.6)
    ax1.set_ylim(0, 105)
    ax1.set_ylabel("kept by L1 [%]" if col == 0 else "")
    ax2.set_ylabel("ratio" if col == 0 else "")
    ax2.set_xlabel(xlab)
    for ax in (ax0, ax1, ax2):
        ax.set_xlim(edges[0], edges[-1])
    ax0.tick_params(labelbottom=False); ax1.tick_params(labelbottom=False)
    if col == 0:
        h1, l1_ = ax1.get_legend_handles_labels()
        h2, l2_ = ax2.get_legend_handles_labels()
fig.legend(h1 + h2, l1_ + l2_, loc="lower center", ncol=4, fontsize=8.3, bbox_to_anchor=(0.5, -0.07))
fig.suptitle(f"Which events the seeds add: soft (low offline H$_T$) and well b-tagged offline (SM HH→4b, odd events; seeds at +{ADD} kHz)",
             fontsize=10.5, color=INK, x=0.01, ha="left")
fig.savefig(f"{OUT}/offline_eff.png", dpi=150, bbox_inches="tight")
plt.close(fig)


# ---------- 11. thesis-style seed plane: HT vs sum of 4 jet b scores, iso-rate contours (seed_plane.py) ----------
if os.path.exists(inp("seed_plane.npz")):
    sp = dict(np.load(inp("seed_plane.npz")))
    wmb = 2760 * 11.245 / 1999360
    s_edges, h_edges = np.linspace(0, 4, 201), np.arange(100, 705, 5)
    rate_levels = (2.0, 5.0, 10.0, 20.0)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.8), sharey=True)
    for ax, (key, lab) in zip(axs, (("nn", "today's L1 NN"), ("l1", "L1 tracks + pixel hits"))):
        # rate(s, h) for "sum > s and HT > h": reverse cumulative 2D histogram of minimum bias
        hm = np.histogram2d(np.clip(sp[f"mb_{key}"], 0, 3.999), np.clip(sp["mb_ht"], 100, 704), [s_edges, h_edges])[0]
        hs = np.histogram2d(np.clip(sp[f"hh_{key}"], 0, 3.999), np.clip(sp["hh_ht"], 100, 704), [s_edges, h_edges])[0]
        cum = lambda h: h[::-1, ::-1].cumsum(0).cumsum(1)[::-1, ::-1]
        rate2d, eff2d = cum(hm) * wmb, cum(hs) / len(sp["hh_ht"])
        S, H = np.meshgrid(s_edges[:-1], h_edges[:-1], indexing="ij")
        hd, se_, he_ = np.histogram2d(np.clip(sp[f"hh_{key}"], 0, 3.999), np.clip(sp["hh_ht"], 100, 704), [np.linspace(0, 4, 41), np.arange(100, 710, 20)])
        ax.pcolormesh(se_, he_, (hd / hd.max()).T, cmap="Greys", vmin=0, vmax=1.6, shading="flat")
        notes = []
        cols_ = ["#f2b8a0", "#eb8c62", "#d9622b", "#a8431a"] if key != "nn" else ["#a9c9ef", "#6fa3e4", "#2a78d6", "#1a4f93"]
        for lvl, cc in zip(rate_levels, cols_):
            ax.contour(S, H, rate2d, levels=[lvl], colors=[cc], linewidths=1.8)
            ok = (rate2d <= lvl) & (H >= 150)
            if ok.any():
                i = np.argmax(np.where(ok, eff2d, -1))
                ax.plot(S.flat[i], H.flat[i], marker="*", ms=12, c=cc, mec="white", mew=0.6)
                notes.append((cc, f"{lvl:>4g} kHz: {100 * eff2d.flat[i]:.0f}%  (H$_T$ > {H.flat[i]:.0f}, Σ > {S.flat[i]:.2f})"))
        for j, (cc, t) in enumerate(notes):
            ax.text(3.95, 585 - 26 * j, t, ha="right", va="top", fontsize=8.6, color=INK,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=cc, lw=1.2))
        ax.axhspan(100, 150, color="#ecebe7", alpha=0.9, lw=0)
        ax.text(0.05, 125, "minimum bias incomplete below 150 GeV", fontsize=7.5, color=INK2, va="center")
        ax.set_xlim(0, 4)
        ax.set_ylim(100, 600)
        ax.set_xlabel("Σ of the 4 leading jets' L1 b scores")
        ax.set_title(f"b score from {lab}", loc="left", fontsize=10, color=INK)
    axs[0].set_ylabel("L1 H$_T$ [GeV]")
    fig.suptitle("The (b-score sum, H$_T$) seed alone: lines of equal minimum-bias rate (2 / 5 / 10 / 20 kHz); star and box: best share of\n"
                 "all SM HH→4b events kept on each line (grey: where HH→4b events sit)", fontsize=10.5, color=INK, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(f"{OUT}/seed_plane.png", dpi=150)
    plt.close(fig)

    # ---------- 12. thesis-style jet efficiency vs pT and eta at fixed light mistag ----------
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    tags = (("nn", C["NN"], "today's L1 NN"), ("hlt", C["HLT pixel"], "+ HLT pixel tracks"), ("l1", C["L1 pixel"], "+ L1 tracks with pixel hits"))
    for ax, (var, edges, xl) in zip(axs, (("pt", np.array([15, 20, 25, 30, 40, 50, 60, 80, 100, 150, 250]), "L1 jet p$_T$ [GeV]"),
                                          ("eta", np.linspace(-2.4, 2.4, 13), "L1 jet η"))):
        x = 0.5 * (edges[1:] + edges[:-1])
        for key, c, lab in tags:
            cut = np.quantile(sp[f"jet_light_{key}"], 0.9)  # 10% inclusive light mistag (QCD light jets)
            for tag, fmt, mfc, nm in (("b", "o", c, "b jets (HH→4b)"), ("light", "s", "white", "light jets (QCD)")):
                v = sp[f"jet_{tag}_{var}"]
                n = np.histogram(v, edges)[0]
                k = np.histogram(v, edges, weights=(sp[f"jet_{tag}_{key}"] > cut).astype(float))[0]
                e = k / np.maximum(n, 1)
                ax.errorbar(x, 100 * e, yerr=100 * np.sqrt(e * (1 - e) / np.maximum(n, 1)), xerr=0.5 * np.diff(edges), fmt=fmt, ms=4.5,
                            c=c, mfc=mfc, lw=1.6 if tag == "b" else 1.0, label=f"{lab}: {nm}")
        ax.set_xlabel(xl)
        ax.set_ylim(0, 100)
        if var == "pt":
            ax.set_xscale("log"); ax.set_xticks([15, 20, 30, 50, 100, 200]); ax.set_xticklabels(["15", "20", "30", "50", "100", "200"])
    axs[0].set_ylabel("tagged at 10% inclusive light mistag [%]")
    h_, l_ = axs[0].get_legend_handles_labels()
    fig.legend(h_, l_, loc="lower center", ncol=3, fontsize=8.3, bbox_to_anchor=(0.5, -0.1))
    fig.suptitle("Per-jet b efficiency (filled) and light mistag (open) at a fixed 10% light-mistag cut, odd events (out of sample)",
                 fontsize=10.5, color=INK, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(f"{OUT}/jet_eff.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# ---------- 13. kappa_lambda-weighted efficiency vs added rate, today's offline vs the softest one (offline_scenarios.npz) ----------
if os.path.exists("offline_scenarios.npz"):
    scn = np.load("offline_scenarios.npz")
    sp_ = {(l, e): i for i, (l, e) in enumerate(zip(scn["lumi"], scn["event"]))}
    si_ = np.array([sp_[(l, e)] for l, e in zip(fl["lumi"], fl["event"])])
    rates = [float(k.split("|")[2]) for k in fl if k.startswith("NN|menu|")]
    rates = sorted(rates)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.3), sharey=True)
    for ax, (scen, title) in zip(axs, (("today", "Today's offline selection"),
                                       ("soft_wide", "Softer offline selection"))):
        sel = odd & scn[scen][si_] & (mhh < 400)
        klw = lambda f: 100 * f[sel].mean()
        ax.axhline(klw(fl["menu"]), c=C["menu"], lw=1.5, ls="--", label="Run-3-style menu alone")
        ax.text(0.43, klw(fl["menu"]) + 1, f"Run-3-style menu alone: {klw(fl['menu']):.0f}%", fontsize=8.5, color=INK2)
        for tag, c, lab in (("NN", C["NN"], "today's L1 NN"), ("L1 pixel", C["L1 pixel"], "L1 tracks + pixel hits"),
                            ("perfect", C["perfect"], "perfect b tag")):
            y = [klw(fl[f"{tag}|menu|{r:g}"]) for r in rates]
            ax.plot(rates, y, "o-", c=c, lw=2.2 if tag != "perfect" else 1.2, ms=4.5, ls="-" if tag != "perfect" else "--",
                    label=f"+ seed with {lab}")
        ax.set_xscale("log"); ax.set_xticks([0.5, 1, 2.5, 5, 10]); ax.set_xticklabels(["0.5", "1", "2.5", "5", "10"])
        ax.set_xlim(0.4, 16)
        ax.set_xlabel("added L1 rate on top of the menu [kHz]")
        ax.set_title(title, loc="left", fontsize=10, color=INK)
    axs[0].set_ylabel("low-m$_{HH}$ events kept by L1 [%]")
    axs[0].set_ylim(30, 101)
    h_, l_ = axs[1].get_legend_handles_labels()
    fig.legend(h_[1:], l_[1:], loc="lower center", ncol=3, fontsize=8.5, bbox_to_anchor=(0.5, -0.06))
    fig.suptitle("Offline-selected SM HH→4b events with m$_{HH}$ < 400 GeV kept by L1, against the extra L1 rate spent on the seed",
                 fontsize=10.5, color=INK, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(f"{OUT}/klw_vs_rate.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    for scen in ("today", "soft_wide"):
        sel = odd & scn[scen][si_] & (mhh < 400)
        klw = lambda f: 100 * f[sel].mean()
        print(scen, "n", sel.sum(), "menu", round(klw(fl["menu"]), 1), "perfect2.5", round(klw(fl["perfect|menu|2.5"]), 1))
        print(scen, "NN:", [f"{r:g}:{klw(fl[f'NN|menu|{r:g}']):.0f}" for r in rates])
        print(scen, "pix:", [f"{r:g}:{klw(fl[f'L1 pixel|menu|{r:g}']):.0f}" for r in rates])

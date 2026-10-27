#!/usr/bin/env python3
"""New page figures for the reworked summary page (plots_page/):
  recovery.png          HH->4b kept by each trigger option (menu, lower HT, NN, pixel, perfect), trigger and analysis level
  menu_composition.png  the Phase-2 L1 menu (TDR table) by seed category, hadronic seeds highlighted
  rate_case.png         tagged HH->4b seeds vs the menu's HT seeds: efficiency vs rate, HT thresholds (rate_case.json)

    pixi run python make_story_plots.py [which ...]
Colours as make_page_plots.py: grey = planned menu, dark dotted = lower HT cuts, blue = today's NN, orange = pixel,
black dashed = perfect tag (flavour-aware rate, perfect_ceiling.py).
"""
import glob
import json
import os
import re
import sys

import matplotlib
import matplotlib.ticker
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = "plots_page"
C = {"menu": "#9a9890", "HT": "#52514e", "NN": "#2a78d6", "L1 pixel": "#eb6834", "perfect": "#0b0b0b", "missed": "#e34948"}
INK, INK2 = "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.grid": True, "grid.color": "#ecebe7", "grid.linewidth": 0.8,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False})
ADD = "2.5"
which = set(sys.argv[1:]) or {"recovery", "menu", "rate", "scout", "reach", "lowmass"}


def load_flags():
    fl = dict(np.load("curves_flags.npz"))
    pf = np.load("perfect_ceiling_flags.npz")
    pp = {(l, e): i for i, (l, e) in enumerate(zip(pf["lumi"], pf["event"]))}
    ix = np.array([pp[(l, e)] for l, e in zip(fl["lumi"], fl["event"])])
    for k in pf.files:
        if k.startswith("perfect|"):
            fl[k] = pf[k][ix]
    ctl = dict(np.load("ht_control_flags.npz"))
    cp = {(l, e): i for i, (l, e) in enumerate(zip(ctl["lumi"], ctl["event"]))}
    fl["HTlow"] = ctl[f"HTlow|menu|{ADD}"][np.array([cp[(l, e)] for l, e in zip(fl["lumi"], fl["event"])])]
    g = {k: np.concatenate([np.load(f)[k] for f in sorted(glob.glob("/scratch/submit/cms/novaka/l1pixels/genmhh/mhh_*.npz"))])
         for k in ("lumi", "event", "mhh")}
    gp = {(l, e): i for i, (l, e) in enumerate(zip(g["lumi"], g["event"]))}
    mhh = np.array([g["mhh"][gp[(l, e)]] for l, e in zip(fl["lumi"], fl["event"])])
    # kappa_lambda information weight per event near the SM (as make_page_plots.py section 9)
    nano = {}
    for f in sorted(glob.glob("klreweight/nano_mhh_kl*.npz")):
        m = np.load(f)["mhh"]
        nano[float(re.search(r"kl(\d+p\d+)", f).group(1).replace("p", "."))] = m[m > 0]
    bins = np.concatenate([np.arange(240, 600, 20), np.arange(600, 800, 50), [800, 1000, 1300, 5000]])
    dens = {kl: np.histogram(m, bins)[0] / len(m) for kl, m in nano.items()}
    XS = lambda k: (70.38 - 51.85 * k + 11.42 * k ** 2) / (70.38 - 51.85 + 11.42)
    ks = np.array([0.0, 1.0, 2.45])
    S3 = np.array([XS(k) * dens[k] for k in ks])
    cf = np.array([np.polyfit(ks, S3[:, i], 2) for i in range(S3.shape[1])])
    ds, s1 = 2 * cf[:, 0] + cf[:, 1], S3[1]
    ib = np.clip(np.digitize(mhh, bins) - 1, 0, len(bins) - 2)
    w_info = (ds / np.maximum(s1, 1e-12))[ib] ** 2
    return fl, mhh, w_info


def recovery():
    """One small panel per population (explicit denominators), one marker per trigger option."""
    fl, mhh, wi = load_flags()
    odd, off = fl["odd"].astype(bool), fl["offline_4b3b"].astype(bool)
    rows = [("Planned HT seeds (no b tag)", fl["menu"], C["menu"], "o"),
            (f"+ {ADD} kHz on lower HT cuts", fl["HTlow"], C["HT"], "o"),
            (f"+ {ADD} kHz seed, today's L1 NN", fl[f"NN|menu|{ADD}"], C["NN"], "o"),
            (f"+ {ADD} kHz seed, pixel hits (path A)", fl[f"L1 pixel|menu|{ADD}"], C["L1 pixel"], "o"),
            (f"+ {ADD} kHz seed, perfect b tag", fl[f"perfect|menu|{ADD}"], C["perfect"], "D")]
    pops = [("All SM HH→4b events", odd, None), ("m$_{HH}$ < 400 GeV", odd & (mhh < 400), None),
            ("Would pass offline 4b+3b,\nm$_{HH}$ < 400 GeV", odd & off & (mhh < 400), None),
            ("κλ information in offline-\nselectable events (signal only)", odd & off, wi)]
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.6), sharey=True)
    out = {}
    for ax, (title, den, w) in zip(axes, pops):
        w = np.ones(len(den)) if w is None else w
        for i, (lab, flag, c, mk) in enumerate(rows):
            v = 100 * (w * (flag.astype(bool) & den)).sum() / (w * den).sum()
            y = len(rows) - 1 - i
            ax.plot([0, v], [y, y], color=c, lw=1.2, alpha=0.4)
            ax.plot(v, y, mk, ms=8, color=c)
            ax.text(v + 3, y, f"{v:.0f}%", va="center", fontsize=8.5, color=INK2)
            out[f"{title.replace(chr(10), ' ')} | {lab}"] = round(float(v), 1)
        ax.set_xlim(0, 118)
        ax.set_xticks([0, 50, 100])
        ax.set_title(title, loc="left", fontsize=9.5, color=INK)
        ax.set_xlabel("kept by L1 [%]")
        ax.grid(axis="y", visible=False)
    axes[0].set_yticks(range(len(rows)), [r[0] for r in rows][::-1])
    fig.tight_layout()
    fig.savefig(f"{OUT}/recovery.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    json.dump(out, open(f"{OUT}/recovery.json", "w"), indent=1)
    print("recovery written")


def lowmass():
    """Is the mock offline selection killing the low-m_HH gain? Cutflow vs m_HH, and L1 on today's vs a low-mass-friendly selection."""
    r = json.load(open("/scratch/submit/cms/novaka/l1pixels/derived/offline_lowmass.json"))
    fl, mhh, wi = load_flags()
    odd = fl["odd"].astype(bool)
    lm = np.load("/scratch/submit/cms/novaka/l1pixels/derived/offline_lowmass_flags.npz")
    pos = {(l, e): i for i, (l, e) in enumerate(zip(lm["lumi"], lm["event"]))}
    ix = np.array([pos[(l, e)] for l, e in zip(fl["lumi"], fl["event"])])
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.5, 4.1), gridspec_kw={"width_ratios": [1.2, 1]})
    edges = np.array(r["edges"][:-1] + [1000.0])
    x = 0.5 * (edges[1:] + edges[:-1])
    steps = [("4 jets pT>30", "≥ 4 jets, p$_T$ > 30", "#c9c6bd", "-"), ("tags (4M or 3M+1L)", "+ 4b / 3b tags", "#9a9890", "-"),
             ("+ any pairing in window", "+ some pairing in the Higgs window", INK2, ":"), ("+ chosen pairing in window (today)", "+ today's pairing in the window", INK, "-")]
    for key, lab, c, ls in steps:
        a.plot(x, 100 * np.array(r["cutflow_today"][key]), ls=ls, marker="o", ms=4, color=c, lw=1.8, label=lab)
    best = "pt20_chi2_w30_today"
    a.plot(x, 100 * np.array(r["variants"][best]["eff_bins"]), marker="s", ms=5, color=C["L1 pixel"], lw=2.2,
           label="low-mass friendly: jets > 20 GeV, χ² pairing to (125, 125)")
    a.axvspan(250, 400, color="#eb6834", alpha=0.05, lw=0)
    a.set_xscale("log")
    a.set_xticks([300, 400, 500, 700, 1000], ["300", "400", "500", "700", ">800"])
    a.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    a.set_xlabel("generator m$_{HH}$ [GeV]")
    a.set_ylabel("offline selection efficiency [%] (no trigger)")
    a.set_ylim(0, 90)
    a.legend(fontsize=7.8, loc="upper left")
    a.set_title("Where the offline selection loses low-mass events", loc="left", fontsize=10, color=INK)
    levels = [("HT seeds", "menu", C["menu"]), ("+ NN", "NN|menu|2.5", C["NN"]), ("+ pixel", "L1 pixel|menu|2.5", C["L1 pixel"]),
              ("+ perfect", "perfect|menu|2.5", C["perfect"])]
    for k, (sel, lab) in enumerate((("pt30_mindiff_w30_today", "today's selection"), (best, "low-mass friendly"))):
        f = lm[sel][ix].astype(bool) & odd
        for j, (name, key, c) in enumerate(levels):
            v = (wi * fl[key].astype(bool) * f).sum()
            ref = (wi * fl["NN|menu|2.5"].astype(bool) * odd * lm["pt30_mindiff_w30_today"][ix].astype(bool)).sum()
            xx = k * 5.2 + j
            b.bar(xx, v / ref, color=c, width=0.8, alpha=1.0 if k else 0.6)
            b.text(xx, v / ref + 0.04, f"{v / ref:.2f}", ha="center", fontsize=8, color=INK2)
        b.text(k * 5.2 + 1.5, 2.95, lab, ha="center", fontsize=9.5, color=INK, weight="bold")
    b.set_xticks([j + k * 5.2 for k in range(2) for j in range(4)], ["HT", "NN", "pixel", "perfect"] * 2, fontsize=8.5)
    b.set_ylim(0, 3.15)
    b.set_ylabel("κλ information delivered\n(today's selection + NN seed = 1)")
    b.grid(axis="x", visible=False)
    b.set_title("A better selection doubles it; pixels keep their lead", loc="left", fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(f"{OUT}/lowmass_sel.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("lowmass written")


# Phase-2 L1 menu, CMS-TDR-021 (CERN-LHCC-2020-004) table, as reproduced in V. Rekovic, CEPC 2022, slide 21: rate per
# seed at PU 200 [kHz]. Seeds overlap, so category sums exceed the 346 kHz total (450 with the 30% margin).
TDR = {
    "Single / double jet": {"SinglePuppiJet 180": 70, "DoublePuppiJet 112,112": 71},
    "HT, quad-jet + HT": {"PuppiHT 450": 11, "QuadPuppiJets-PuppiHT": 9},
    "VBF": {"DoublePuppiJets (VBF)": 40},
    "E$_T^{miss}$": {"PuppiMET 200": 18},
    "Leptons": {"Single TkMuon": 12, "Double TkMuon": 1, "Triple TkMuon": 16, "Single TkElectron": 24,
                "Single TkIsoElectron": 28, "TkIsoElectron-StaEG": 36, "Double TkElectron": 4, "Single StaEG": 25,
                "Double StaEG": 5},
    "Photons": {"Single TkIsoPhoton": 43, "Double TkIsoPhoton": 50},
    "Taus": {"Single CaloTau": 21, "Double CaloTau": 25, "Double PuppiTau": 7},
    "Lepton + hadron": {"TkMuon-PuppiHT": 4, "TkMuon-DoublePuppiJet": 10, "TkMuon-PuppiJet-MET": 14,
                        "DoubleTkMuon-PuppiJet-MET": 4, "DoubleTkMuon-PuppiHT": 2, "DoubleTkElectron-PuppiHT": 0.9,
                        "TkIsoElectron-PuppiHT": 9, "TkElectron-PuppiJet": 34, "PuppiTau-PuppiMET": 4},
    "Cross lepton": {"TkMuon-TkIsoElectron": 1, "TkMuon-TkElectron": 3, "TkElectron-TkMuon": 1, "TkMuon-DoubleTkElectron": 0.1,
                     "DoubleTkMuon-TkElectron": 4, "PuppiTau-TkMuon": 2, "TkIsoElectron-PuppiTau": 13},
    "B physics (dimuon)": {"Double TkMuon (3 seeds)": 43, "Triple TkMuon (2 seeds)": 13},
}


def menu():
    cats = list(TDR)
    tot = [sum(TDR[c].values()) for c in cats]
    o = np.argsort(tot)
    hadr = {"Single / double jet", "HT, quad-jet + HT", "VBF"}
    fig, ax = plt.subplots(figsize=(9.5, 4.0))
    for k, i in enumerate(o):
        c = cats[i]
        col = INK2 if c == "HT, quad-jet + HT" else ("#9a9890" if c in hadr else "#dcd9d0")
        ax.barh(k, tot[i], color=col, height=0.62)
        detail = ", ".join(f"{n} {v:g}" for n, v in TDR[c].items()) if c in hadr else ""
        ax.text(tot[i] + 2, k, f"{tot[i]:g} kHz" + (f"   ({detail})" if detail else ""), va="center", fontsize=8.5, color=INK2)
    ax.set_yticks(range(len(cats)), [cats[i] for i in o])
    ax.set_xlim(0, 260)
    ax.set_xlabel("sum of seed rates at PU 200 [kHz] (seeds overlap: whole menu 346 kHz, 450 with margin, of 750)")
    ax.grid(axis="y", visible=False)
    ax.set_title("Phase-2 L1 menu (TDR) by category: seeds overlap, bars do not add up to 346 kHz; HT seeds dark", loc="left", fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(f"{OUT}/menu_composition.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("menu composition written; category sums", dict(zip(cats, tot)))


def rate():
    r = json.load(open("rate_case.json"))
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.0), gridspec_kw={"width_ratios": [1.35, 1]})
    styles = {"HT only": (C["HT"], ":", "s", "HT only (as the menu's HT seed)"), "NN": (C["NN"], "-", "o", "HT + today's NN b scores"),
              "pixel": (C["L1 pixel"], "-", "o", "HT + pixel b scores (path A)"), "perfect": (C["perfect"], "--", "D", "HT + perfect b tag (ceiling)")}
    for name, (c, ls, mk, lab) in styles.items():
        rows = sorted(r["standalone"][name], key=lambda x: x["rate_khz"])
        x = [q["rate_khz"] for q in rows]
        y = [100 * q["eff_all"] for q in rows]
        a.plot(x, y, ls=ls, marker=mk, color=c, ms=5, lw=2 if name in ("NN", "pixel") else 1.3, label=lab)
    m = r["menu"]
    a.plot(m["rate_khz"], 100 * m["eff_all"], "*", ms=15, color=C["menu"], mec=INK2, label="menu HT seeds (HT450 or QuadJet+HT400)")
    a.axvline(m["rate_khz"], color="#c3c2b7", lw=1)
    a.set_xscale("log")
    a.set_xticks([2, 3, 5, 10, 20, 40], ["2", "3", "5", "10", "20", "40"])
    a.set_xlabel("rate of the seed alone [kHz]")
    a.set_ylabel("SM HH→4b kept [%]")
    a.set_ylim(0, 100)
    a.legend(fontsize=8, loc="lower right")
    a.set_title("One HH→4b seed instead of the HT seeds", loc="left", fontsize=10, color=INK)
    # right: HT threshold each seed can afford at ~20 kHz, and the rate it needs for the menu's efficiency
    names = ["HT only", "NN", "pixel"]
    rate_eq = [r["standalone"][n + "_rate_for_menu_eff"] for n in names]
    cols = [styles[n][0] for n in names]
    b.barh(range(3)[::-1], rate_eq, color=cols, height=0.55)
    for k, (n, v) in enumerate(zip(names, rate_eq)):
        row20 = min(r["standalone"][n], key=lambda q: abs(q["rate_khz"] - m["rate_khz"]))
        b.text(v + 0.4, 2 - k, f"{v:.1f} kHz   (at {row20['rate_khz']:.0f} kHz: HT > {row20['ht_cut']:.0f}, keeps {100 * row20['eff_all']:.0f}%)",
               va="center", fontsize=8.5, color=INK2)
    b.axvline(m["rate_khz"], color=C["menu"], lw=1.5, ls="--")
    b.text(m["rate_khz"] + 0.4, -0.45, "menu HT seeds (19 kHz)", fontsize=8, color=INK2)
    b.set_yticks(range(3)[::-1], ["HT only", "HT + NN", "HT + pixel"])
    b.set_ylim(-0.6, 2.5)
    b.set_xlim(0, 40)
    b.set_xlabel(f"rate needed to keep the menu's {100 * m['eff_all']:.0f}% [kHz]")
    b.grid(axis="y", visible=False)
    b.set_title("Same efficiency, less rate", loc="left", fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(f"{OUT}/rate_case.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("rate case written")


def scout():
    """Why scouting cannot select HH->4b: per-jet tag quality at the working points, and what survives selection."""
    tc = json.load(open("tag_chain.json"))
    sc = json.load(open("scouting.json"))
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.1), gridspec_kw={"width_ratios": [1, 1.1], "wspace": 0.45})
    for name, c, lab in (("L1 NN", C["NN"], "L1 NN (today)"), ("L1 + pixel", C["L1 pixel"], "L1 + pixel (path A tag)"),
                         ("offline UParT", "#6250d6", "offline UParT")):
        r = tc[name]
        a.plot(100 * np.array(r["roc_mistag"]), 100 * np.array(r["roc_beff"]), color=c, lw=2, label=lab)
    pix = tc["L1 + pixel"]
    e5 = 100 * np.interp(0.05, pix["roc_mistag"], pix["roc_beff"])
    a.plot(5, e5, "o", ms=9, color=C["L1 pixel"], mec=INK)
    a.annotate(f"scouting: L1 tag at 5% mistag\n{e5:.0f}% per b jet, {e5 ** 4 / 1e6:.0f}% for four", (5, e5), (0.115, 27),
               fontsize=8.5, color=INK2, arrowprops=dict(arrowstyle="-", color="#9a9890"))
    a.plot(1, 84, "D", ms=8, color="#6250d6", mec=INK)
    a.annotate("triggered events: offline tag at 1%\n84% per b jet, 50% for four", (1, 84), (1.3, 93), fontsize=8.5, color=INK2)
    a.set_xscale("log")
    a.set_xlim(0.1, 50)
    a.set_ylim(0, 100)
    a.set_xticks([0.1, 1, 10], ["0.1", "1", "10"])
    a.set_xlabel("light-jet mistag [%]")
    a.set_ylabel("b-jet efficiency [%]")
    a.legend(fontsize=8, loc="center right")
    a.set_title("Scouted events only have L1 tags", loc="left", fontsize=10, color=INK)
    rows = [("menu + pixel seed (path A)\noffline tags on triggered events", sc["trig_l1"], C["L1 pixel"]),
            ("scouting alone\nL1 pixel tags, every crossing HT > 150", sc["scout_l1"], "#c9c6bd")]
    for k, (lab, r, c) in enumerate(rows):
        y = 1 - k
        b.barh(y + 0.18, r["S"], height=0.32, color=c)
        b.barh(y - 0.18, r["B"], height=0.32, color=c, alpha=0.45, hatch="//", edgecolor="white")
        b.text(r["S"] * 1.3, y + 0.18, f"signal {r['S']:.0f}", va="center", fontsize=8.5, color=INK2)
        b.text(r["B"] * 1.3, y - 0.18, f"background {r['B']:.1e}", va="center", fontsize=8.5, color=INK2)
        b.text(r["B"] * 1.3, y - 0.42, f"S/√B = {r['S'] / np.sqrt(r['B']):.2f} (shape fit Z = {r['Z_SM']:.2f})", fontsize=9, color=INK)
    b.set_xscale("log")
    b.set_xlim(1e3, 1e12)
    b.set_ylim(-0.7, 1.5)
    b.set_yticks([1, 0], [r[0] for r in rows], fontsize=8.5)
    b.set_xlabel("events in 3000 fb$^{-1}$ after the 4b / 3b selection (Higgs window)")
    b.grid(axis="y", visible=False)
    ratio = sc["scout_l1"]["B"] / sc["trig_l1"]["B"]
    b.set_title(f"Less signal and {ratio:.0f}× more background", loc="left", fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(f"{OUT}/scout_why.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("scout_why written", e5)


def reach():
    """Lower mass is not reachable by scouting: L1 HT of HH->4b events with four L1 jets in the Higgs window."""
    r = json.load(open("/scratch/submit/cms/novaka/l1pixels/derived/scouting/hh_ht_reach.json"))
    edges = np.array(r["ht_edges"][:-1] + [700.0])
    fig, ax = plt.subplots(figsize=(9, 3.8))
    for kl, c, lab in (("1.0", INK2, "SM (κλ = 1)"), ("2.45", C["NN"], "κλ = 2.45"), ("5.0", C["L1 pixel"], "κλ = 5")):
        y = np.array(r[kl]["yield_per_ht_bin"], float)
        y = y / y.sum() / np.diff(edges) * 100
        ax.stairs(y, edges, color=c, lw=2, label=f"{lab}: {100 * r[kl]['frac_below_150']:.1f}% below HT 150")
    ax.axvspan(0, 150, color=C["missed"], alpha=0.08, lw=0)
    for x, t in ((150, "scouting floor\n(re-simulated\nminimum bias)"), (170, "pixel seed\nHT cut"), (400, "menu HT seeds\n400 / 450")):
        ax.axvline(x, color="#9a9890", lw=1, ls="--")
        ax.text(x + 4, ax.get_ylim()[1] * 0.92 if x != 170 else ax.get_ylim()[1] * 0.62, t, fontsize=8, color=INK2, va="top")
    ax.set_xlim(0, 700)
    ax.set_xlabel("L1 H$_T$ [GeV] (last bin: > 400)")
    ax.set_ylabel("share per GeV [%]")
    ax.legend(fontsize=8.5, loc="upper right")
    ax.set_title("HH→4b with four L1 jets > 20 GeV in the Higgs window already sits above HT 150", loc="left", fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(f"{OUT}/scout_reach.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("scout_reach written")


if __name__ == "__main__":
    if "recovery" in which:
        recovery()
    if "menu" in which:
        menu()
    if "rate" in which and os.path.exists("rate_case.json"):
        rate()
    if "lowmass" in which:
        lowmass()
    if "scout" in which:
        scout()
    if "reach" in which:
        reach()

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
which = set(sys.argv[1:]) or {"recovery", "menu", "rate"}


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
    fl, mhh, wi = load_flags()
    odd, off = fl["odd"].astype(bool), fl["offline_4b3b"].astype(bool)
    rows = [("Planned menu (no L1 b tag)", fl["menu"], C["menu"], "o"),
            (f"+ {ADD} kHz on lower HT cuts", fl["HTlow"], C["HT"], "o"),
            (f"+ {ADD} kHz seed, today's L1 NN", fl[f"NN|menu|{ADD}"], C["NN"], "o"),
            (f"+ {ADD} kHz seed, pixel hits (path A)", fl[f"L1 pixel|menu|{ADD}"], C["L1 pixel"], "o"),
            (f"+ {ADD} kHz seed, perfect b tag (ceiling)", fl[f"perfect|menu|{ADD}"], C["perfect"], "D")]
    panels = [("Trigger level: all SM HH→4b", [("all events", odd, None), ("m$_{HH}$ < 400 GeV", odd & (mhh < 400), None)]),
              ("Analysis level: offline 4b + 3b selected", [("m$_{HH}$ < 400 GeV", odd & off & (mhh < 400), None),
                                                           ("κλ information", odd & off, wi)])]
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.9), sharey=True)
    out = {}
    for ax, (title, metrics) in zip(axes, panels):
        for j, (mlab, den, w) in enumerate(metrics):
            w = np.ones(len(den)) if w is None else w
            for i, (lab, flag, c, mk) in enumerate(rows):
                v = 100 * (w * (flag.astype(bool) & den)).sum() / (w * den).sum()
                y = len(rows) - 1 - i + (0.17 if j == 0 else -0.17)
                ax.plot([0, v], [y, y], color=c, lw=1.0, alpha=0.25 if j else 0.45)
                ax.plot(v, y, mk, ms=8 if j == 0 else 7.5, color=c, mfc=c if j == 0 else "white", mew=1.8)
                ax.text(v + 2.4, y, f"{v:.0f}%", va="center", fontsize=8.5, color=INK2)
                out[f"{title} | {mlab} | {lab}"] = round(float(v), 1)
        ax.set_xlim(0, 112)
        ax.set_title(title, loc="left", fontsize=10, color=INK)
        ax.set_xlabel("kept by L1 [%]")
        ax.grid(axis="y", visible=False)
        h = [plt.Line2D([], [], marker="o", ls="", color=INK2, ms=7, mfc=INK2, label=f"filled: {metrics[0][0]}"),
             plt.Line2D([], [], marker="o", ls="", color=INK2, ms=7, mfc="white", mew=1.6, label=f"open: {metrics[1][0]}")]
        ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, fontsize=8.5)
    axes[0].set_yticks(range(len(rows)), [r[0] for r in rows][::-1])
    fig.tight_layout()
    fig.savefig(f"{OUT}/recovery.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    json.dump(out, open(f"{OUT}/recovery.json", "w"), indent=1)
    print("recovery:", json.dumps(out, indent=0))


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
    ax.set_title("Phase-2 L1 menu (TDR): no seed uses a b tag; HH→4b relies on the HT seeds (dark)", loc="left", fontsize=10, color=INK)
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


if __name__ == "__main__":
    if "recovery" in which:
        recovery()
    if "menu" in which:
        menu()
    if "rate" in which and os.path.exists("rate_case.json"):
        rate()

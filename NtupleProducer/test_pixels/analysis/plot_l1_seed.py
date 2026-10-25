#!/usr/bin/env python3
"""Plots from l1_seed.json:  python3 plot_l1_seed.py l1seed_full/l1_seed.json OUTDIR"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

s = json.load(open(sys.argv[1]))
out = sys.argv[2]
os.makedirs(out, exist_ok=True)
SURF, INK, MUTED, GRID = "#fcfcfb", "#1f1f1e", "#6b6a64", "#e4e3de"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
RAMP = {0.5: "#86b6ef", 0.7: "#2a78d6", 0.9: "#104281"}
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK, "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.8, "lines.linewidth": 2})
scan = s["scan"]
pick = lambda t, r: next(x for x in scan if x["tagger"] == t and x["target_khz"] == r)
n_acc = s["n_sig_in_acceptance"]

# 1) efficiency at 14 kHz vs per-jet mistag, for a flat tagger
fig, ax = plt.subplots(figsize=(7, 4.6))
ems = sorted({x["eps_mis"] for x in scan if x["tagger"] == "parametric" and x["eps_mis"] > 0})
for eb, c in RAMP.items():
    pts = [pick_ for pick_ in scan if pick_["tagger"] == "parametric" and pick_["target_khz"] == 14.0 and pick_["eps_b"] == eb and pick_["eps_mis"] > 0]
    pts.sort(key=lambda x: x["eps_mis"])
    ax.plot([p["eps_mis"] for p in pts], [p["eff"] for p in pts], "-o", color=c, ms=6, mec=SURF, mew=1.5)
    ax.plot([], [], "-o", color=c, ms=6, label=f"ε_b = {eb}")
for t, lab in [("HT only", "HT only"), ("HT + L1 NN tagger", "HT + L1 NN (today)"), ("HT + perfect b-tag", "perfect b-tag")]:
    e = pick(t, 14.0)["eff"]
    ax.axhline(e, color=MUTED, lw=1.2, ls="--" if t != "HT + L1 NN tagger" else "-", zorder=0)
    ax.text(0.0011, e + 0.004, f"{lab}  {e:.0%}", va="bottom", ha="left", color=MUTED, fontsize=9.5)
ax.axvspan(0.1, 0.2, color=GRID, alpha=0.6, lw=0, zorder=0)
ax.text(0.14, 0.615, "L1 NN\nhard-jet\nmistag", ha="center", color=MUTED, fontsize=8.5)
ax.set_xscale("log"); ax.set_xlim(0.001, 0.3); ax.legend(frameon=False, loc="center left", bbox_to_anchor=(0.0, 0.66), fontsize=9.5); ax.set_ylim(0.6, 1.01)
ax.set_xlabel("per-jet mistag rate ε_mis (≥1 tag among 4 leading L1 jets)")
ax.set_ylabel("HH→4b seed efficiency")
ax.set_title(f"HH→4b L1 seed at 14 kHz vs b-tag quality ({n_acc} HH→4b events)", fontsize=11, loc="left")
fig.tight_layout(); fig.savefig(f"{out}/eff_vs_mistag_14kHz.png", dpi=150); plt.close(fig)

# 2) efficiency vs rate
fig, ax = plt.subplots(figsize=(7, 4.6))
rates = sorted({x["target_khz"] for x in scan})
series = [("HT only", lambda r: pick("HT only", r)),
          ("HT + L1 NN (today)", lambda r: pick("HT + L1 NN tagger", r)),
          ("ε_b 0.7, ε_mis 1%", lambda r: next(x for x in scan if x["tagger"] == "parametric" and x["target_khz"] == r and x["eps_b"] == 0.7 and x["eps_mis"] == 0.01)),
          ("perfect b-tag", lambda r: pick("HT + perfect b-tag", r))]
for (lab, f), c in zip(series, CAT):
    pts = [f(r) for r in rates]
    ax.plot(rates, [p["eff"] for p in pts], "-o", color=c, ms=7, mec=SURF, mew=1.5, label=lab)
    ax.annotate(f"{lab}", (rates[-1], pts[-1]["eff"]), xytext=(8, 0), textcoords="offset points", va="center", color=INK, fontsize=9.5)
    for r, p in zip(rates, pts):
        if r == 14.0 and lab != "perfect b-tag":
            ax.annotate(f"HT>{p['ht_cut']:.0f}", (r, p["eff"]), xytext=(0, -14), textcoords="offset points", ha="center", color=MUTED, fontsize=8.5)
ax.set_xlim(3, 42); ax.set_ylim(0.4, 1.02)
ax.set_xlabel("L1 rate budget [kHz]"); ax.set_ylabel("HH→4b seed efficiency")
ax.legend(frameon=False, loc="lower right", fontsize=9)
ax.set_title("HH→4b L1 seed efficiency vs rate (HT cut re-optimised per point)", fontsize=11, loc="left")
fig.tight_layout(); fig.savefig(f"{out}/eff_vs_rate.png", dpi=150); plt.close(fig)

# 3) HH->4b HT spectrum: efficiency of the HT cut alone, with the cuts each tagger allows at 14 kHz
fig, ax = plt.subplots(figsize=(7, 4.2))
h = {int(k): v for k, v in s["sig_ht_eff"].items()}
ax.plot(list(h), list(h.values()), color=CAT[0])
for (lab, ht), c in zip([("HT only", pick("HT only", 14.0)["ht_cut"]), ("L1 NN", pick("HT + L1 NN tagger", 14.0)["ht_cut"]),
                         ("ε_mis 1%", 140.0)], [MUTED, MUTED, MUTED]):
    e = max(v for k, v in h.items() if k <= ht) if ht > 0 else 1.0
    ax.axvline(ht, color=c, lw=1, ls="--", zorder=0)
    ax.text(ht + 4, 0.45, f"{lab}\nHT>{ht:.0f}", color=MUTED, fontsize=9)
ax.set_xlabel("HT cut [GeV] (L1 jets pT>30, |η|<2.4)"); ax.set_ylabel("fraction of HH→4b kept")
ax.set_title("HH→4b sits low in HT: what each 14 kHz HT cut costs", fontsize=11, loc="left")
ax.set_ylim(0.4, 1.02)
fig.tight_layout(); fig.savefig(f"{out}/hh4b_ht_cut_eff.png", dpi=150); plt.close(fig)
print("wrote", out)

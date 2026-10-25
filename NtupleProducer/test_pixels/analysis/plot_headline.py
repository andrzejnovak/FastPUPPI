#!/usr/bin/env python3
"""Headline plot: equivalent HL-LHC luminosity for HH->4b vs L1 rate allocated to the seed.

    python3 plot_headline.py OUT.png headline_5kHz.json headline_10kHz.json headline_14kHz.json headline_30kHz.json
Bands span conservative (eff ratio) to optimistic (ratio squared); relative to today's L1 NN seed at the same rate.
"""
import json
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

out, files = sys.argv[1], sys.argv[2:]
rates = [float(re.search(r"headline_(\d+)kHz", f).group(1)) for f in files]
data = [json.load(open(f)) for f in files]
order = sorted(range(len(rates)), key=lambda i: rates[i])
rates = [rates[i] for i in order]
data = [data[i] for i in order]
SURF, INK, MUTED, GRID = "#fcfcfb", "#1f1f1e", "#6b6a64", "#e4e3de"
BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK, "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID})
fig, axs = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
for ax, kl, title in [(axs[0], "1.0", "SM (κλ = 1)"), (axs[1], "5.0", "κλ = 5")]:
    ax.axvspan(6.6, 11, color=GRID, alpha=0.8, lw=0)
    ax.text(8.8, 2.95, "Phase-2 menu\nallocation", ha="center", va="top", fontsize=9, color=MUTED)
    ax.axhline(1, color=MUTED, lw=1)
    for name, col, lab in [("pixel tagger (realistic proxy)", BLUE, "pixel tagger (measured fakes)"),
                           ("ideal tagger (eps_b 0.7, 1%)", ORANGE, "ideal tagger (ceiling)")]:
        lo = [d[kl][name]["Leq_conservative"] for d in data]
        hi = [d[kl][name]["Leq_optimistic"] for d in data]
        ax.fill_between(rates, lo, hi, color=col, alpha=0.25, lw=0)
        ax.plot(rates, lo, "-o", color=col, ms=5, lw=2, label=f"{lab}")
        ax.plot(rates, hi, "--", color=col, lw=1.2)
    ax.set_title(title, loc="left")
    ax.set_xlabel("L1 rate given to the HH→4b seed [kHz]")
    ax.set_xlim(4, 31)
axs[0].set_ylabel("equivalent HL-LHC luminosity\n(relative to today's L1 NN seed)")
axs[0].set_ylim(0.9, 3.0)
axs[0].legend(frameon=False, loc="upper right", fontsize=9.5, bbox_to_anchor=(1.0, 0.78))
fig.text(0.01, 0.005, "Solid: conservative (background gains like the signal). Dashed: optimistic (background unchanged). "
         "Generator fiducial proxy; same rate for both seeds.", fontsize=8.5, color=MUTED)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(out, dpi=150)
print("wrote", out)

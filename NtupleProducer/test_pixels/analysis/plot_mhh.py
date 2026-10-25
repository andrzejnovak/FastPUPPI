#!/usr/bin/env python3
"""Gen m_HH: what the L1 HH->4b seed captures today vs what a better b-tag could recover.

    python3 plot_mhh.py seed_flags_14kHz.npz OUTDIR
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

d = np.load(sys.argv[1])
out = sys.argv[2]
os.makedirs(out, exist_ok=True)
SURF, INK, MUTED, GRID = "#fcfcfb", "#1f1f1e", "#6b6a64", "#e4e3de"
BLUE, ORANGE, AQUA, LOST = "#2a78d6", "#eb6834", "#1baf7a", "#d9d8d2"
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK, "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.8, "lines.linewidth": 2})
rate = float(d["rate_khz"])
sel = d["acc"] & (d["mhh"] > 0)
m = d["mhh"][sel]
nn, ht, better = d["nn"][sel], d["ht_only"][sel], d["param_eb0.7_em0.01"][sel]
bins = np.arange(250, 1010, 20)
w = 1.0 / (len(m) * np.diff(bins)[0])
H = lambda mask: np.histogram(m[mask], bins)[0] * w
both, gain, lost = nn & better, better & ~nn, nn & ~better
h_tot, h_both, h_gain, h_lost = H(np.ones_like(nn)), H(both), H(gain), H(lost)
f_nn, f_better = nn.mean(), better.mean()

fig, (ax, ax2) = plt.subplots(2, 1, figsize=(7.5, 7), sharex=True, gridspec_kw={"height_ratios": [2.2, 1], "hspace": 0.08})
edges = np.repeat(bins, 2)[1:-1]
step = lambda h: np.repeat(h, 2)
c0, c1, c2 = step(h_both), step(h_both + h_gain), step(h_both + h_gain + h_lost)
ax.fill_between(edges, 0, c0, color=BLUE, alpha=0.85, lw=0, label=f"kept by both seeds  ({both.mean():.0%})")
ax.fill_between(edges, c0, c1, color=AQUA, alpha=0.85, lw=0, label=f"gained by ε_b 0.7, ε_mis 1% tagger  (+{gain.mean():.0%})")
ax.fill_between(edges, c1, c2, facecolor="none", edgecolor=ORANGE, hatch="////", lw=0, label=f"lost when switching (pass today only)  (−{lost.mean():.0%})")
ax.fill_between(edges, c2, step(h_tot), color=LOST, lw=0, label=f"missed by both  ({1 - (nn | better).mean():.0%})")
ax.text(0.99, 0.62, f"today (HT + L1 NN): {f_nn:.0%}\nbetter tagger alone: {f_better:.0%}", transform=ax.transAxes, ha="right", va="top", fontsize=10)
ax.plot(edges, step(h_tot), color=INK, lw=1.5)
ax.plot(edges, step(H(ht)), color=INK, lw=1.2, ls=":", label=f"HT only  ({ht.mean():.0%})")
ax.set_ylabel("dN/dm_HH (a.u., normalised)")
ax.set_ylim(0, h_tot.max() * 1.45)
ax.legend(frameon=False, loc="upper right", fontsize=9.5)
ax.set_title(f"HH→4b (SM, 14 TeV, PU200) L1 seed at {rate:.0f} kHz vs generator-level m_HH", fontsize=11, loc="left")
ax.text(0.99, 0.44, f"{len(m)} events, generator fiducial proxy:\n4 gen b jets pT > 30 GeV, |η| < 2.4", transform=ax.transAxes, ha="right",
        va="top", color=MUTED, fontsize=9)

c = 0.5 * (bins[1:] + bins[:-1])
n_tot = np.histogram(m, bins)[0]
for mask, col, lab, ls in [(better, AQUA, "ε_b 0.7, ε_mis 1%", "-"), (nn, BLUE, "HT + L1 NN", "-"), (ht, ORANGE, "HT only", "--")]:
    e = np.histogram(m[mask], bins)[0] / np.maximum(n_tot, 1)
    ok = n_tot >= 30
    ax2.plot(c[ok], e[ok], color=col, ls=ls, label=lab)
ax2.set_ylim(0, 1.05); ax2.set_ylabel("seed efficiency")
ax2.set_xlabel("generator-level m_HH [GeV]")
ax2.legend(frameon=False, loc="lower right", fontsize=9, ncol=3)
ax2.set_xlim(250, 1000)
fig.savefig(f"{out}/mhh_captured_vs_recoverable_{rate:.0f}kHz.png", dpi=150, bbox_inches="tight")
for lo, hi in [(250, 350), (350, 450), (450, 600), (600, 2000)]:
    b = (m >= lo) & (m < hi)
    print(f"m_HH {lo}-{hi}: frac {b.mean():.2f}  HT {ht[b].mean():.2f}  NN {nn[b].mean():.2f}  better {better[b].mean():.2f}")
print("wrote", out)

#!/usr/bin/env python3
"""Page tab 1 figure: the gap. SM HH->4b events kept and missed by the planned L1 menu (no L1 b tag), per generator
m_HH, as expected events at 3000/fb; trigger level (all events) and among offline-selectable events (4b + 3b).
Top strip: where the kappa_lambda information lives (as make_page_plots.py section 9).

    pixi run python plot_gap.py [plots_page/gap_mhh.png]
Inputs: curves_flags.npz (menu flag, odd events, offline_4b3b), genmhh dumps, klreweight/nano_mhh_kl*.npz.
Prints the numbers quoted on the page.
"""
import glob
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

out = sys.argv[1] if len(sys.argv) > 1 else "plots_page/gap_mhh.png"
KEPT, MISSED, INK, INK2 = "#9a9890", "#e34948", "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.grid": True, "grid.color": "#ecebe7", "grid.linewidth": 0.8,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False})
N_SM = 3000 * 36.69 * 0.5824 ** 2  # SM ggF HH -> 4b events produced in 3000/fb

fl = dict(np.load("curves_flags.npz"))
odd, menu = fl["odd"], fl["menu"].astype(bool)
g = {k: np.concatenate([np.load(f)[k] for f in sorted(glob.glob("/scratch/submit/cms/novaka/l1pixels/genmhh/mhh_*.npz"))])
     for k in ("lumi", "event", "mhh")}
pos = {(l, e): i for i, (l, e) in enumerate(zip(g["lumi"], g["event"]))}
mhh = np.array([g["mhh"][pos[(l, e)]] for l, e in zip(fl["lumi"], fl["event"])])
# kappa_lambda information near the SM (as make_page_plots.py section 9)
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
info = np.where(s1 > 0, ds ** 2 / np.maximum(s1, 1e-12), 0.0)
ib = np.clip(np.digitize(mhh, bins) - 1, 0, len(bins) - 2)
w_info = (ds / np.maximum(s1, 1e-12))[ib] ** 2

w = odd * N_SM / odd.sum()
edges = np.array([250, 300, 350, 400, 450, 500, 550, 600, 700, 800, 1000])  # last bin includes m_HH > 1 TeV
x = np.clip(mhh, edges[0], edges[-1] - 1)
fig = plt.figure(figsize=(11, 5.6))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 3.2], hspace=0.08, wspace=0.2)
for col, (title, den) in enumerate((("Trigger level: all SM HH→4b events", np.ones(len(mhh), bool)),
                                    ("Analysis level: events an offline 4b + 3b selection would keep", fl["offline_4b3b"].astype(bool)))):
    a0, a1 = fig.add_subplot(gs[0, col]), fig.add_subplot(gs[1, col])
    centers = 0.5 * (bins[1:] + bins[:-1])
    share = np.histogram(np.clip(centers, edges[0], edges[-1] - 1), edges, weights=info)[0] / info.sum()
    a0.bar(edges[:-1], 100 * share, width=np.diff(edges), align="edge", color="#d9d6cc", edgecolor="white", lw=2)
    a0.set_ylabel("κλ info [%]", fontsize=8.5)
    a0.set_title(title, loc="left", fontsize=10, color=INK)
    per50 = np.diff(edges) / 50.0  # events per 50 GeV, so wider bins do not look larger
    kept = np.histogram(x[den], edges, weights=(w * menu)[den])[0] / per50
    missed = np.histogram(x[den], edges, weights=(w * ~menu)[den])[0] / per50
    a1.bar(edges[:-1], kept, width=np.diff(edges), align="edge", color=KEPT, edgecolor="white", lw=2, label="kept by the planned menu")
    a1.bar(edges[:-1], missed, bottom=kept, width=np.diff(edges), align="edge", color=MISSED, alpha=0.85, edgecolor="white", lw=2,
           label="missed (no L1 b tag)")
    for xl, k, m in zip(0.5 * (edges[1:] + edges[:-1]), kept, missed):
        if k + m > 0.04 * (kept + missed).max():
            a1.text(xl, k + m, f"{100 * m / (k + m):.0f}%", ha="center", va="bottom", fontsize=8, color=MISSED)
    a1.set_ylabel("events in 3000 fb$^{-1}$ per 50 GeV")
    a1.set_xlabel("generator m$_{HH}$ [GeV]")
    for ax in (a0, a1):
        ax.set_xlim(edges[0], edges[-1])
        ax.axvspan(edges[0], 400, color="#eb6834", alpha=0.05, lw=0)
    a0.tick_params(labelbottom=False)
    if col == 0:
        a1.legend(loc="upper right", fontsize=8.5)
    a1.set_ylim(0, (kept + missed).max() * 1.15)
    lo = den & odd & (mhh < 400)
    tot = den & odd
    print(f"{title}: events {(w * den).sum():.0f}, missed {100 * (~menu & tot).sum() / tot.sum():.1f}%; m_HH < 400: "
          f"{(w * (den & (mhh < 400))).sum():.0f} events, missed {100 * (~menu & lo).sum() / lo.sum():.1f}%; "
          f"kappa_lambda information missed {100 * (w_info * (~menu & tot)).sum() / (w_info * tot).sum():.1f}%")
fig.suptitle("The gap: what the planned Phase-2 L1 menu (no L1 b tag, 19 kHz of HT + quad-jet seeds) misses in SM HH→4b; "
             "red labels: share missed per bin", fontsize=10, color=INK, x=0.01, ha="left")
fig.savefig(out, dpi=150, bbox_inches="tight")
print("wrote", out)

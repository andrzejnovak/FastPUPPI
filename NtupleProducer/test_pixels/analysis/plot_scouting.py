#!/usr/bin/env python3
"""Page figure for the kappa_lambda / scouting prototype (scouting.py -> scouting.json).

    python3 plot_scouting.py [scouting.json] [plots_page/kl_scan.png]
Left: Asimov -2 Delta lnL vs kappa_lambda per stream; right: 68% / 95% intervals. Colours as make_page_plots.py.
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

src = sys.argv[1] if len(sys.argv) > 1 else "scouting.json"
out = sys.argv[2] if len(sys.argv) > 2 else "plots_page/kl_scan.png"
C = {"menu": "#9a9890", "NN": "#2a78d6", "L1 pixel": "#eb6834", "perfect": "#0b0b0b"}
INK2 = "#52514e"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.grid": True, "grid.color": "#ecebe7", "grid.linewidth": 0.8,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False})
d = json.load(open(src))
kl = np.array(d["curves"]["kl"])
FALLBACK, SCOUT = "#c2408f", "#0f8a5f"  # scouting variants get their own hues (validated with the page palette)
rows = [("trig_menu", "planned HT seeds", C["menu"], "-"), ("trig_nn", "+ NN seed (+2.5 kHz)", C["NN"], "-"),
        ("trig_l1", "+ pixel seed (+2.5 kHz)", C["L1 pixel"], "-"),
        ("comb_menu_l1", "HT seeds + pixel tags in scouting", FALLBACK, "--"),
        ("scout_l1", "scouting alone, L1 pixel tags", SCOUT, ":")]
d15 = json.load(open(src.replace(".json", "_15khz.json"))) if os.path.exists(src.replace(".json", "_15khz.json")) else None
INT = {"comb_menu_l1": "comb_menu+scout_l1"}  # curve key -> result key

fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.9), gridspec_kw={"width_ratios": [1.25, 1]})
for key, lab, col, ls in rows:
    a.plot(kl, d["curves"][key], color=col, lw=2, ls=ls, label=lab)
for lvl, txt in ((1.0, "68%"), (3.84, "95%")):
    a.axhline(lvl, color="#c3c2b7", lw=1)
    a.text(-2.9, lvl + 0.08, txt, ha="left", va="bottom", color=INK2, fontsize=9)
a.set(xlim=(-3, 8), ylim=(0, 6), xlabel=r"$\kappa_\lambda$", ylabel=r"$-2\,\Delta\ln L$ (Asimov, SM truth)")
fig.legend(*a.get_legend_handles_labels(), loc="lower center", ncol=3, fontsize=8.5, bbox_to_anchor=(0.5, -0.12))

def regions(q, lvl):
    """All kappa_lambda ranges with -2 dlnL below lvl (disconnected regions drawn separately)."""
    q = np.asarray(q)
    ok = q < lvl
    cross = lambda k: kl[k] + (lvl - q[k]) * (kl[k + 1] - kl[k]) / (q[k + 1] - q[k])  # linear crossing in [k, k+1]
    out, start = [], None
    for k, o in enumerate(ok):
        if o and start is None:
            start = cross(k - 1) if k > 0 else kl[0]
        if (not o or k == len(ok) - 1) and start is not None:
            out.append((start, cross(k - 1) if not o else kl[k]))
            start = None
    return out


irows = [(key, lab, col, ls, d) for key, lab, col, ls in rows]
if d15 is not None:  # the same seeds at +15 kHz (CMS's b-tag NN seed rate), interval panel only
    irows[3:3] = [("trig_nn", "+ NN seed (+15 kHz)", C["NN"], "15", d15), ("trig_l1", "+ pixel seed (+15 kHz)", C["L1 pixel"], "15", d15)]
for i, (key, lab, col, ls, dd) in enumerate(irows):
    q = dd["curves"][key]
    y = len(irows) - 1 - i
    for lo, hi in regions(q, 3.84):
        b.plot([lo, hi], [y, y], color=col, lw=2, solid_capstyle="round", alpha=0.45 if ls != "-" else 0.6)
    regs = regions(q, 1.0)
    for lo, hi in regs:
        b.plot([lo, hi], [y, y], color=col, lw=7, solid_capstyle="round", alpha=0.45 if ls == "15" else 0.9)
    txt = "  ∪  ".join(f"[{lo:+.1f}, {hi:+.1f}]" for lo, hi in regs)
    b.text(8.2, y, txt, va="center", ha="left", fontsize=8.5, color=INK2)
b.axvline(1.0, color="#c3c2b7", lw=1)
b.set_yticks(range(len(irows)), [r[1] for r in irows][::-1], fontsize=8.5)
b.set(xlim=(-4, 8), xlabel=r"allowed $\kappa_\lambda$ (thick 68%, thin 95%; every region drawn)")
b.grid(axis="y", visible=False)
fig.suptitle(r"HH$\to$4b, 3000 fb$^{-1}$, stat. only, L1-jet resolution; background: minimum bias $\times$ QCD 4b fractions by seed score",
             fontsize=9.5, color=INK2)
fig.tight_layout()
fig.savefig(out, dpi=150, bbox_inches="tight")
print("wrote", out)

#!/usr/bin/env python3
"""Page figure for the kappa_lambda / scouting prototype (scouting.py -> scouting.json).

    python3 plot_scouting.py [scouting.json] [plots_page/kl_scan.png]
Left: Asimov -2 Delta lnL vs kappa_lambda per stream; right: 68% / 95% intervals. Colours as make_page_plots.py.
"""
import json
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
rows = [("trig_menu", "planned menu", C["menu"], "-"), ("trig_nn", "+ NN seed (2.5 kHz)", C["NN"], "-"),
        ("trig_l1", "+ pixel seed (2.5 kHz)", C["L1 pixel"], "-"), ("trig_perfect", "+ perfect-tag seed", C["perfect"], ":"),
        ("scout_l1", "scouting, L1 pixel tags only", C["L1 pixel"], "--")]

fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.9), gridspec_kw={"width_ratios": [1.25, 1]})
for key, lab, col, ls in rows:
    a.plot(kl, d["curves"][key], color=col, lw=2, ls=ls, label=lab)
for lvl, txt in ((1.0, "68%"), (3.84, "95%")):
    a.axhline(lvl, color="#c3c2b7", lw=1)
    a.text(-2.9, lvl + 0.08, txt, ha="left", va="bottom", color=INK2, fontsize=9)
a.set(xlim=(-3, 8), ylim=(0, 6), xlabel=r"$\kappa_\lambda$", ylabel=r"$-2\,\Delta\ln L$ (Asimov, SM truth)")
fig.legend(*a.get_legend_handles_labels(), loc="lower center", ncol=5, fontsize=8.5, bbox_to_anchor=(0.5, -0.07))

for i, (key, lab, col, ls) in enumerate(rows):
    r = d[key]
    y = len(rows) - 1 - i
    lo95, hi95 = r["kl_95"]
    lo68, hi68 = r["kl_68"]
    b.plot([lo95, hi95], [y, y], color=col, lw=2, solid_capstyle="round", alpha=0.45 if ls != "-" else 0.6)
    b.plot([lo68, hi68], [y, y], color=col, lw=7, solid_capstyle="round", alpha=0.9)
    note = "  + 2nd minimum" if r["second_region_68"] else ""
    b.text(8.2, y, f"[{lo68:+.2f}, {hi68:+.2f}]{note}", va="center", ha="left", fontsize=8.5, color=INK2)
b.axvline(1.0, color="#c3c2b7", lw=1)
b.set_yticks(range(len(rows)), [lab for _, lab, _, _ in rows][::-1], fontsize=8.5)
b.set(xlim=(-4, 8), xlabel=r"$\kappa_\lambda$ interval (thick 68%, thin 95%)")
b.grid(axis="y", visible=False)
fig.suptitle(r"HH$\to$4b, 3000 fb$^{-1}$, statistical only, L1-jet resolution; background = minimum bias, QCD 4b/3b tag fractions",
             fontsize=9.5, color=INK2)
fig.tight_layout()
fig.savefig(out, dpi=150, bbox_inches="tight")
print("wrote", out)

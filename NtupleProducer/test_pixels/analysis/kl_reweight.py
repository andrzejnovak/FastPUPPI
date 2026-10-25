#!/usr/bin/env python3
"""Reweight the Phase-2 SM HH->4b sample to other kappa_lambda with gen-m_HH shape ratios from Run-3 POWHEG samples.

    python3 kl_reweight.py seed_flags_14kHz.npz "klreweight/nano_mhh_kl*.npz" OUTDIR

w_kl(m) = p_kl(m) / p_1(m), both from the 13.6 TeV POWHEG samples (shape only; 13.6 vs 14 TeV changes the ratio negligibly).
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

d = np.load(sys.argv[1])
out = sys.argv[3]
os.makedirs(out, exist_ok=True)
nano = {}
for f in sorted(glob.glob(sys.argv[2])):
    kl = float(re.search(r"kl(\d+p\d+)", f).group(1).replace("p", "."))
    m = np.load(f)["mhh"]
    nano[kl] = m[m > 0]
bins = np.concatenate([np.arange(240, 600, 20), np.arange(600, 800, 50), [800, 1000, 1300, 5000]])
dens = {kl: np.histogram(m, bins)[0] / len(m) for kl, m in nano.items()}
m = d["mhh"]
ib = np.clip(np.digitize(m, bins) - 1, 0, len(bins) - 2)
ok = m > 0
weights = {}
for kl in sorted(nano):
    r = np.where(dens[1.0] > 0, dens[kl] / np.maximum(dens[1.0], 1e-12), 0.0)
    weights[kl] = np.where(ok, r[ib], 0.0)
    if kl == 1.0:
        weights[kl] = ok.astype(float)  # SM: no reweighting

acc = d["acc"]
better = d["param_eb0.7_em0.01"]
seeds = {"HT only": d["ht_only"], "HT + L1 NN": d["nn"], "eps_b 0.7, eps_mis 3%": d["param_eb0.7_em0.03"],
         "eps_b 0.7, eps_mis 1%": better}
res = {}
for kl, w in weights.items():
    neff = w.sum() ** 2 / (w ** 2).sum()
    r = {"acceptance": float((w * acc).sum() / w.sum()), "n_eff": float(neff), "max_w": float(w.max())}
    for name, p in seeds.items():
        r[name] = {"acc": float((w * acc * p).sum() / (w * acc).sum()), "all": float((w * p).sum() / w.sum())}
    res[kl] = r
    print(f"kl={kl:4.2f} acc={r['acceptance']:.3f} n_eff={neff:7.0f} max_w={w.max():5.1f} | " +
          " | ".join(f"{n}: {v['acc']:.2f}/{v['all']:.2f}" for n, v in r.items() if isinstance(v, dict)))
json.dump(res, open(f"{out}/kl_reweight.json", "w"), indent=1)

# small multiples: captured today / recoverable / still lost, per kappa_lambda (events in acceptance)
SURF, INK, MUTED, GRID = "#fcfcfb", "#1f1f1e", "#6b6a64", "#e4e3de"
BLUE, ORANGE, AQUA, LOST = "#2a78d6", "#eb6834", "#1baf7a", "#d9d8d2"
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK, "font.size": 10.5,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.8})
pb = np.arange(250, 1010, 25)
fig, axs = plt.subplots(2, 2, figsize=(10.5, 7.6), sharex=True)
nn = d["nn"]
for ax, kl in zip(axs.flat, sorted(weights)):
    w = weights[kl] * acc
    norm = w.sum() * np.diff(pb)[0]
    H = lambda mask: np.histogram(m[mask], pb, weights=w[mask])[0] / norm
    h_tot, h_both, h_gain, h_lost = H(ok), H(ok & nn & better), H(ok & better & ~nn), H(ok & nn & ~better)
    e = np.repeat(pb, 2)[1:-1]
    s = lambda h: np.repeat(h, 2)
    r = res[kl]
    f_nn, f_b = r["HT + L1 NN"]["acc"], r["eps_b 0.7, eps_mis 1%"]["acc"]
    c0, c1, c2 = s(h_both), s(h_both + h_gain), s(h_both + h_gain + h_lost)
    ax.fill_between(e, 0, c0, color=BLUE, alpha=0.85, lw=0, label="kept by both seeds")
    ax.fill_between(e, c0, c1, color=AQUA, alpha=0.85, lw=0, label="gained: ε_b 0.7, ε_mis 1% tagger")
    ax.fill_between(e, c1, c2, facecolor="none", edgecolor=ORANGE, hatch="////", lw=0, label="lost when switching")
    ax.fill_between(e, c2, s(h_tot), color=LOST, lw=0, label="missed by both")
    ax.plot(e, s(h_tot), color=INK, lw=1.3)
    ax.plot(e, s(H(ok & d["ht_only"])), color=INK, lw=1.2, ls=":", label="HT only")
    ax.set_title(f"κλ = {kl:g}{'  (SM)' if kl == 1 else ''}", loc="left", fontsize=11)
    ax.text(0.98, 0.95, f"today {f_nn:.0%}\nbetter tagger {f_b:.0%}", transform=ax.transAxes, ha="right", va="top",
            fontsize=10, color=INK)
    ax.set_ylim(0, h_tot.max() * 1.25)
for ax in axs[1]:
    ax.set_xlabel("generator-level m_HH [GeV]")
for ax in axs[:, 0]:
    ax.set_ylabel("dN/dm_HH (a.u.)")
axs[0, 0].set_xlim(250, 1000)
h, l = axs[0, 0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=4, frameon=False, fontsize=9.5, bbox_to_anchor=(0.5, -0.01))
fig.suptitle(f"HH→4b L1 seed at {float(d['rate_khz']):.0f} kHz vs κλ (Phase-2 SM sample reweighted in gen m_HH; generator fiducial proxy)",
             x=0.01, ha="left", fontsize=11.5)
fig.tight_layout(rect=(0, 0.04, 1, 0.97))
fig.savefig(f"{out}/mhh_kl_small_multiples_14kHz.png", dpi=150)

# sanity: Phase-2 SM (14 TeV) vs POWHEG kl=1 (13.6 TeV) gen m_HH shapes
fig, ax = plt.subplots(figsize=(6.5, 4))
c = 0.5 * (bins[1:] + bins[:-1])
p2 = np.histogram(m[ok], bins)[0] / ok.sum()
sel = bins[1:] <= 1000
ax.step(c[sel], (p2 / np.diff(bins))[sel], where="mid", color=BLUE, label="Phase-2 SM, 14 TeV (reco sample)")
ax.step(c[sel], (dens[1.0] / np.diff(bins))[sel], where="mid", color=ORANGE, ls="--", label="POWHEG κλ=1, 13.6 TeV")
ax.set_xlabel("generator-level m_HH [GeV]"); ax.set_ylabel("density [1/GeV]"); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(f"{out}/mhh_sm_shape_check.png", dpi=150)
print("wrote", out)

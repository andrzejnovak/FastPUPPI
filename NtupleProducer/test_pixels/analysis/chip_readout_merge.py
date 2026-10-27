#!/usr/bin/env python3
"""Readout volume of the regional pixel request with whole-chip readout: calibration, summary JSON, page figure.

    python3 chip_readout_merge.py chip_geom.npz "parts/part_*.npz" ITLINKS_DIR OUT.json OUT.png
Bits per chip: the CROC payload of CMSSW's Phase2ITQCoreProducer emulation (itlinks/bits_*.npz: 20 PU 200 crossings,
bits per detId and chip; payload only, no headers or link framing) calibrated against the ntuple clusters:
  b_g = sum over modules of group g of (emulated mean bits) / (ntuple mean clusters),
groups = (layer or disk, ring along z / r), modules fully inside the cluster tables' |eta| < 2.5. A chip in a crossing
then carries b_g * (its clusters) + (1 - acceptance) * (emulated mean bits per chip of its module) for the part of
the chip outside the cluster tables. Readout time: each touched chip sends its payload on one 1.28 Gb/s e-link.
"""
import glob
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import chipgeo as CG

geo_path, parts_glob, itlinks, out_json, out_png = sys.argv[1:6]
RATES = {140: 367e3, 200: 123e3}  # pre-selection rates [Hz] (bits_budget / HANDOFF)
ELINK = 1.28e9
B_COMPACT, B_TAGGER_JET = 36, 64
WHOLE_DET = None  # filled from the emulation

G = CG.Geometry(geo_path)
nchip_mod = G.n_long * G.n_short
FULLMOD = (G.accept.sum(1) >= nchip_mod - 1e-9)

# ---- ntuple parts
parts = sorted(glob.glob(parts_glob))
P = [np.load(p) for p in parts]
n_ev_all = sum(int(p["n_events"]) for p in P)
mean_clus = sum(p["sum_clus"] for p in P).reshape(-1, 4) / n_ev_all
hist = sum(p["hist"] for p in P)
regions = P[0]["regions"]
rows = np.concatenate([p["rows"] for p in P])
cols = list(P[0]["row_cols"])
R = {c: rows[:, i] for i, c in enumerate(cols)}
evs = []  # per crossing: (mods, mask, nclus, nwin)
for p in P:
    off = p["offsets"]
    for i in range(len(off) - 1):
        s = slice(off[i], off[i + 1])
        evs.append((p["mod"][s], p["mask"][s], p["nclus"][s], p["nwin"][s]))
qa = {"crossings_processed": n_ev_all, "crossings_ht140": len(evs),
      "clusters_outside_any_module_frac": sum(int(p["n_unassigned"]) for p in P) / sum(int(p["n_clus_total"]) for p in P),
      "window_clusters_on_geometrically_touched_chip_frac": sum(int(p["n_win_cl_in_geo"]) for p in P) / max(sum(int(p["n_win_cl"]) for p in P), 1)}

# ---- emulated chip bitstreams
emu = [np.load(f) for f in sorted(glob.glob(f"{itlinks}/bits_*.npz"))]
det = np.concatenate([e["detid"] for e in emu])
chip = np.concatenate([e["chip"] for e in emu])
bits = np.concatenate([e["bits"] for e in emu]).astype(float)
evt = np.concatenate([e["event"] + 1000 * i for i, e in enumerate(emu)])
# CHARGE_FIX=1: CMSSW's Phase2ITQCore::encodeQCore writes 4 ToT bits for all 16 pixels of a 4x4 quarter core, hit or
# not (Phase2ITQCore.cc:158); the CROC sends ToT only for hit pixels. Per module and crossing: quarter cores
# N_qc = bits / (64 + F), corrected bits = N_qc * F + 4 * (hit pixels), F = mean non-ToT bits per quarter core
# (address, flags, hit-map tree; QCORE_OVERHEAD, default 20, scanned 12-30).
CHARGE_FIX = os.environ.get("CHARGE_FIX", "0") == "1"
QC_F = float(os.environ.get("QCORE_OVERHEAD", "20"))
if CHARGE_FIX:
    nd = np.concatenate([e["ndigi_module"] for e in emu]).astype(float)
    key = evt * 10**10 + det
    uk, inv = np.unique(key, return_inverse=True)
    bm = np.bincount(inv, bits)
    ndm = np.bincount(inv, nd) / np.bincount(inv)  # the module's hit pixels (repeated per chip row)
    nqc = bm / (64 + QC_F)
    scale = np.where(bm > 0, np.minimum((nqc * QC_F + 4 * ndm) / np.maximum(bm, 1e-9), 1.0), 1.0)
    bits = bits * scale[inv]
    print(f"charge-bit fix (F = {QC_F:g}): payload x{bits.sum() / (bm.sum()):.3f}", flush=True)
n_emu = len(np.unique(evt))
WHOLE_DET = bits.sum() / n_emu
m_emu = np.searchsorted(G.detid, det)
known = (m_emu < G.nmod) & (G.detid[np.minimum(m_emu, G.nmod - 1)] == det)
emu_mod = np.zeros(G.nmod)
np.add.at(emu_mod, m_emu[known], bits[known] / n_emu)
emu_frac_in_geom = bits[known].sum() / bits.sum()
mc = np.minimum(m_emu, G.nmod - 1)

# ---- calibration groups: (|lid|, ring)
alid = abs(G.lid)
rc = np.hypot(G.c[:, 0], G.c[:, 1])
ring = np.where(alid < 10, np.floor(abs(G.c[:, 2]) / G.L_long), np.floor(rc / 2.5)).astype(int)
gkey = alid * 100 + ring
clus_mod = mean_clus.sum(1)
use = FULLMOD & (clus_mod > 0) & (emu_mod > 0)
b_mod = np.zeros(G.nmod)
calib = {}
no_full = []
for reg in np.unique(alid):
    sr = use & (alid == reg)
    if sr.sum() < 3:  # no module fully inside the cluster tables (outer TFPX disks): b from the nearest disk below
        no_full.append(reg)
        continue
    b_reg = emu_mod[sr].sum() / clus_mod[sr].sum()
    for g in np.unique(gkey[alid == reg]):
        sg = use & (gkey == g)
        b_mod[gkey == g] = emu_mod[sg].sum() / clus_mod[sg].sum() if sg.sum() >= 3 else b_reg
    # validation at module level with the region-wide b (the ring dependence is then a test, not a fit)
    pred = b_reg * clus_mod[sr]
    x, y = clus_mod[sr], emu_mod[sr]
    slope, icpt = np.polyfit(x, y, 1) if sr.sum() > 2 else (np.nan, np.nan)
    calib[f"{'TBPX L' if reg < 10 else 'TFPX D'}{reg if reg < 10 else reg - 10}"] = {
        "modules_used": int(sr.sum()), "bits_per_cluster": float(b_reg),
        "module_mean_clusters_ntuple": float(x.mean()) if sr.any() else None,
        "module_mean_bits_emulated": float(y.mean()) if sr.any() else None,
        "pearson_r_module_bits_vs_clusters": float(np.corrcoef(x, y)[0, 1]) if sr.sum() > 2 else None,
        "linear_fit_bits_per_cluster": float(slope), "linear_fit_intercept_bits": float(icpt),
        "rms_emulated_over_predicted": float(np.std(y / pred)) if sr.any() else None,
        "chips_in_geometry": int(nchip_mod[alid == reg].sum()),
        "chips_with_bits_in_emulation": int(len(np.unique((det * 4 + chip)[known & (bits > 0) & (alid[mc] == reg)]))),
        "b_ring_groups": {int(g % 100): float(b_mod[gkey == g][0]) for g in np.unique(gkey[alid == reg])}}
    # chip-level occupancy distributions: emulated bits per chip per crossing vs b_reg x clusters per chip per crossing
    se = known & np.isin(m_emu, np.where((alid == reg) & FULLMOD)[0]) & (chip < 4)
    se &= ((chip & 1) == 0) | (G.n_long[np.minimum(m_emu, G.nmod - 1)] == 2)
    se &= ((chip >> 1) == 0) | (G.n_short[np.minimum(m_emu, G.nmod - 1)] == 2)
    h = hist[list(regions).index(reg)]
    cdf = np.cumsum(h) / h.sum()
    q = lambda f: float(b_reg * np.searchsorted(cdf, f))
    calib_key = list(calib)[-1]
    calib[calib_key]["chip_bits_per_crossing"] = {
        "emulated": {"median": float(np.median(bits[se])), "p90": float(np.percentile(bits[se], 90)),
                     "p99": float(np.percentile(bits[se], 99)), "mean": float(bits[se].mean())},
        "predicted": {"median": q(0.5), "p90": q(0.9), "p99": q(0.99),
                      "mean": float(b_reg * (h * np.arange(len(h))).sum() / h.sum())}}
for reg in no_full:
    ref = max(r for r in np.unique(alid) if r < reg and r not in no_full and (r < 10) == (reg < 10))
    b_mod[alid == reg] = calib[f"{'TBPX L' if ref < 10 else 'TFPX D'}{ref if ref < 10 else ref - 10}"]["bits_per_cluster"]
E_chip = np.where(nchip_mod > 0, emu_mod / nchip_mod, 0)  # emulated mean bits per chip, for the missing acceptance

# ---- per crossing
B = b_mod[:, None]
# uplinks (1.28 Gb/s) per module, CMS IT system data flow (hstd13 Phase-2 IT talk): TBPX L1-L4 6/2/2/1, TFPX rings
# 1-4 3/3/2/2 (rings assigned per disk by module radius, innermost first)
upl = np.ones(G.nmod)
for l, u in {1: 6, 2: 2, 3: 2, 4: 1}.items():
    upl[alid == l] = u
for dsk in np.unique(alid[alid > 10]):
    m = np.where(alid == dsk)[0]
    r = np.round(rc[m], 1)
    ur = np.unique(r)
    gaps = np.argsort(np.diff(ur))[::-1][:3]
    cuts = np.sort(ur[gaps + 1])
    rg = np.searchsorted(cuts, r, side="right")
    upl[m] = np.array([3, 3, 2, 2])[np.clip(rg, 0, 3)]
recs = []
req_mods, req_bits = [], []  # per crossing: modules the request reads and their bits (QUEUE_DUMP)
for mods, mask, ncl, nwin in evs:
    bit = (mask[:, None] >> np.arange(4)) & 1
    acc = G.accept[mods]
    cb = B[mods] * ncl + (1 - acc) * E_chip[mods][:, None] * (acc > 0)
    tb = cb * bit
    req_mods.append(mods[bit.sum(1) > 0])
    req_bits.append(tb.sum(1)[bit.sum(1) > 0])
    hb = cb * (nwin > 0)
    modsum = (cb * (acc > 0)).sum(1)
    recs.append({
        "chips": int(bit.sum()), "modules": int((bit.sum(1) > 0).sum()), "bits_full": float(tb.sum()),
        "bits_extrap": float(((1 - acc) * E_chip[mods][:, None] * (acc > 0) * bit).sum()),
        "chips_partial_acc": int((bit * (acc < 1)).sum()),
        "t_chip_us": float(tb.max() / ELINK * 1e6) if bit.any() else 0.0,
        "slowest_lid": int(abs(G.lid[mods[np.unravel_index(np.argmax(tb), tb.shape)[0]]])) if bit.any() else 0,
        "t_chip_noL1_us": float((tb * (abs(G.lid[mods]) != 1)[:, None]).max() / ELINK * 1e6) if bit.any() else 0.0,
        "t_module_us": float(modsum[bit.sum(1) > 0].max() / ELINK * 1e6) if bit.any() else 0.0,
        "t_mod_upl_us": float((tb.sum(1) / (upl[mods] * ELINK)).max() * 1e6) if bit.any() else 0.0,
        "t_mod_upl_noL1_us": float((tb.sum(1) / (upl[mods] * ELINK) * (abs(G.lid[mods]) != 1)).max() * 1e6) if bit.any() else 0.0,
        "slowest_lid_upl": int(abs(G.lid[mods[np.argmax(tb.sum(1) / upl[mods])]])) if bit.any() else 0,
        "chips_hit": int((nwin > 0).sum()), "bits_hitchips": float(hb.sum()),
        "clus_touched": float((ncl * bit).sum()),
        "bits_win_chip": float((B[mods] * nwin).sum()), "nwin": float(nwin.sum())})
K = {k: np.array([r[k] for r in recs]) for k in recs[0]}
ht = R["ht"]
if os.environ.get("QUEUE_DUMP"):  # inputs of readout_queue.py: normal-readout and request load per module
    E = np.zeros((n_emu, G.nmod))
    ue = np.unique(evt)
    np.add.at(E, (np.searchsorted(ue, evt[known]), m_emu[known]), bits[known])
    np.savez_compressed(os.environ["QUEUE_DUMP"], upl=upl, lid=G.lid, emu_bits=E.astype(np.float32), ht=ht,
                        req_off=np.cumsum([0] + [len(m) for m in req_mods]), req_mod=np.concatenate(req_mods),
                        req_bits=np.concatenate(req_bits).astype(np.float32), charge_fix=CHARGE_FIX, qc_f=QC_F)
K["bits_tagger"] = B_TAGGER_JET * R["njet"]
K["bits_win_compact"] = B_COMPACT * R["nwin_sum"]
K["bits_win_130"] = 130 * R["nwin_sum"]


def stats(a):
    return {"mean": float(a.mean()), "median": float(np.median(a)), "p90": float(np.percentile(a, 90)),
            "p99": float(np.percentile(a, 99))}


summary = {}
for cut, rate in RATES.items():
    s = ht > cut
    d = {"crossings": int(s.sum()), "rate_kHz": rate / 1e3,
         "requesting_tracks": float(R["ntrk_req"][s].mean()), "l1_jets": float(R["njet"][s].mean()),
         "window_clusters_sum_over_tracks": float(R["nwin_sum"][s].mean()),
         "window_clusters_distinct": float(R["nwin_union"][s].mean()),
         "chips_touched": stats(K["chips"][s]), "modules_touched": stats(K["modules"][s]),
         "chips_with_window_clusters": stats(K["chips_hit"][s]),
         "clusters_in_touched_chips": stats(K["clus_touched"][s]),
         "bits": {k: stats(K[f"bits_{k}"][s]) for k in ("tagger", "win_compact", "win_chip", "win_130", "hitchips", "full")},
         "Gbps": {k: float(K[f"bits_{k}"][s].mean() * rate / 1e9) for k in ("tagger", "win_compact", "win_chip", "win_130", "hitchips", "full")},
         "readout_time_us_chip_elink": stats(K["t_chip_us"][s]) | {
             "frac_above_2p5us": float((K["t_chip_us"][s] > 2.5).mean()), "frac_above_3us": float((K["t_chip_us"][s] > 3.0).mean())},
         "readout_time_us_chip_4lanes": stats(K["t_chip_us"][s] / 4) | {
             "frac_above_2p5us": float((K["t_chip_us"][s] / 4 > 2.5).mean()), "frac_above_3us": float((K["t_chip_us"][s] / 4 > 3.0).mean())},
         "readout_time_us_chip_elink_without_TBPX_L1": stats(K["t_chip_noL1_us"][s]) | {
             "frac_above_2p5us": float((K["t_chip_noL1_us"][s] > 2.5).mean())},
         "readout_time_us_module_real_uplinks": stats(K["t_mod_upl_us"][s]) | {
             "frac_above_1p5us": float((K["t_mod_upl_us"][s] > 1.5).mean()), "frac_above_2p5us": float((K["t_mod_upl_us"][s] > 2.5).mean()),
             "slowest_region_frac": {str(l): float((K["slowest_lid_upl"][s] == l).mean()) for l in np.unique(K["slowest_lid_upl"][s])}},
         "readout_time_us_module_real_uplinks_without_TBPX_L1": stats(K["t_mod_upl_noL1_us"][s]) | {
             "frac_above_1p5us": float((K["t_mod_upl_noL1_us"][s] > 1.5).mean()), "frac_above_2p5us": float((K["t_mod_upl_noL1_us"][s] > 2.5).mean())},
         "charge_fix": CHARGE_FIX, "qcore_overhead_bits": QC_F,
         "readout_time_us_chip_4lanes_without_TBPX_L1": stats(K["t_chip_noL1_us"][s] / 4) | {
             "frac_above_1p5us": float((K["t_chip_noL1_us"][s] / 4 > 1.5).mean()),
             "frac_above_2p5us": float((K["t_chip_noL1_us"][s] / 4 > 2.5).mean())},
         "readout_time_us_chip_2lanes_without_TBPX_L1": stats(K["t_chip_noL1_us"][s] / 2) | {
             "frac_above_2p5us": float((K["t_chip_noL1_us"][s] / 2 > 2.5).mean())},
         "slowest_chip_layer_frac": {str(l): float((K["slowest_lid"][s] == l).mean()) for l in np.unique(K["slowest_lid"][s])},
         "readout_time_us_module_elink": stats(K["t_module_us"][s]) | {
             "frac_above_2p5us": float((K["t_module_us"][s] > 2.5).mean()), "frac_above_3us": float((K["t_module_us"][s] > 3.0).mean())},
         "bits_from_acceptance_extrapolation_frac": float(K["bits_extrap"][s].sum() / K["bits_full"][s].sum()),
         "touched_chips_partial_acceptance_frac": float(K["chips_partial_acc"][s].sum() / K["chips"][s].sum()),
         "whole_detector_bits_per_crossing": WHOLE_DET, "full_chips_over_whole_detector": float(K["bits_full"][s].mean() / WHOLE_DET),
         "full_chips_over_window_chip_encoding": float(K["bits_full"][s].mean() / K["bits_win_chip"][s].mean()),
         "full_chips_over_tagger": float(K["bits_full"][s].mean() / K["bits_tagger"][s].mean())}
    summary[f"ht>{cut}"] = d

res = {"method": __doc__.strip().splitlines()[2:], "inputs": {"parts": len(parts), "ntuples": "local_mbsel_ext (MinBiasSel, stored L1 HT > 90)",
                                                              "emulated_crossings": n_emu},
       "qa": qa, "geometry_validation": json.load(open(geo_path.replace(".npz", "_val.json"))) if glob.glob(geo_path.replace(".npz", "_val.json")) else None,
       "emulation": {"whole_detector_bits_per_crossing": WHOLE_DET, "frac_bits_in_learned_modules": float(emu_frac_in_geom),
                     "frac_bits_in_modules_fully_in_cluster_tables": float(emu_mod[FULLMOD].sum() / WHOLE_DET),
                     "mean_bits_per_cluster_all_full_modules": float(emu_mod[use].sum() / clus_mod[use].sum())},
       "calibration": calib, "summary": summary}
json.dump(res, open(out_json, "w"), indent=1)
print(json.dumps({"qa": qa, "summary": summary}, indent=1))

# ---- figure (page style as make_page_plots.py)
C = {"menu": "#9a9890", "NN": "#2a78d6", "L1 pixel": "#eb6834", "HLT pixel": "#1baf7a", "perfect": "#0b0b0b",
     "OT only": "#eda100", "offline": "#6250d6", "missed": "#e34948"}
INK, INK2 = "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.grid": True, "grid.color": "#ecebe7", "grid.linewidth": 0.8,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False})
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw={"width_ratios": [1.1, 1]})
ax.set_axisbelow(True)
sci = lambda v: f"{v / 10 ** np.floor(np.log10(v)):.1f}e{int(np.floor(np.log10(v)))}"
s140, s200 = summary["ht>140"], summary["ht>200"]
cats = [("into the tagger (64 b per jet)", "tagger", C["HLT pixel"]),
        (f"window hits, compact ({B_COMPACT} b/cluster)", "win_compact", C["OT only"]),
        ("window hits, chip encoding", "win_chip", C["L1 pixel"]),
        ("full chips the windows touch", "full", C["missed"]),
        ("whole detector, per L1 accept", None, C["menu"])]
y = np.arange(len(cats))[::-1]
for yi, (lab, k, col) in zip(y, cats):
    for dy, sm, alpha, cut in ((0.19, s140, 1.0, 140), (-0.19, s200, 0.45, 200)):
        v = sm["bits"][k]["mean"] if k else WHOLE_DET
        ax.barh(yi + dy, v, height=0.36, color=col, alpha=alpha, lw=0)
        txt = f"{sci(v)} b" + (f" → {v * RATES[cut] / 1e9:.3g} Gb/s" if k else (" (18 Tb/s at 750 kHz)" if dy > 0 else ""))
        ax.text(v * 1.2, yi + dy, txt, va="center", fontsize=8, color=INK2)
ax.set_xscale("log")
ax.set_xlim(30, 3e9)
ax.set_yticks(y)
ax.set_yticklabels([c[0] for c in cats], color=INK)
ax.grid(axis="y", visible=False)
ax.set_xlabel("bits per crossing (mean)")
ax.set_title(f"HT > 140 ({RATES[140] / 1e3:.0f} kHz, solid) / HT > 200 ({RATES[200] / 1e3:.0f} kHz, light)",
             fontsize=10, color=INK, loc="left")
TMAX = 15
bins = np.linspace(0, TMAX, 65)
s = ht > 140
for t, col, ls, lab in ((K["t_chip_us"][s], C["missed"], "-", "all chips (slowest in TBPX L1)"),
                        (K["t_chip_noL1_us"][s], C["L1 pixel"], "--", "TBPX L1 not read"),
                        (K["t_chip_us"][s] / 4, C["NN"], ":", "all, 4 lanes per chip")):
    ax2.hist(np.minimum(t, bins[-1] - 1e-6), bins=bins, histtype="step", lw=1.6, color=col, ls=ls, density=True,
             label=f"{lab}\nmedian {np.median(t):.1f} µs, {(t > 2.5).mean():.0%} above 2.5 µs")
ax2.set_ylim(0, ax2.get_ylim()[1] * 1.9)
ax2.axvspan(2.5, 3.0, color=C["menu"], alpha=0.3, lw=0)
ax2.text(3.1, ax2.get_ylim()[1] * 0.5, "latency budget\n2.5–3 µs", ha="left", va="center", fontsize=8, color=INK2)
ax2.set_xlabel("readout time per crossing [µs] (HT > 140)")
ax2.set_ylabel("crossings (normalised)")
ax2.set_xlim(0, TMAX)
ax2.legend(loc="upper right", fontsize=7.5, labelspacing=0.8)
ax2.set_title("Slowest touched chip, 1.28 Gb/s per e-link", fontsize=10, color=INK, loc="left")
fig.suptitle(f"A chip returns everything it holds: the request reads ~{s140['chips_touched']['mean']:.0f} whole chips per crossing "
             f"(minimum bias, PU 200)", fontsize=10.5, color=INK, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(out_png, dpi=150)
print("wrote", out_json, out_png)

#!/usr/bin/env python3
"""Is the mock offline HH->4b selection killing low-m_HH signal? Cutflow vs generator m_HH and low-mass-friendly variants.

    pixi run python offline_lowmass_w.py OUT.json "HH4B_GLOB" "QCD_GLOB" GENMHH_GLOB KL_GLOB "QCDW_GLOB"
(offline_lowmass.py with a real background: QCDW_GLOB = dump_offline.py files of the pT-binned QCD samples, with
generator cross-sections; QCD_GLOB still sets the UParT working points.)
Same jets, UParT working points, b-response correction as offline_sel.py. Per HH event (generator m_HH):
  cutflow of today's selection: >= 4 good jets (pT > 30) -> the 4 highest-b jets are all true b -> tags (4 M or 3 M + 1 L)
  -> pairing + 30 GeV window; plus an oracle: does ANY pairing of the 4 jets fall in the window?
  variants: jet pT 20 / 25 / 30, pairing by smallest |m1 - m2| (today) or smallest chi2 to (125, 125), window radius
  30 / 40 / 50 GeV, tags today (4 M or 3 M + 1 L) or loose (>= 3 M, or 4 L).
Each variant: signal efficiency per m_HH bin and kappa_lambda-information-weighted, and a QCD proxy: the same kinematic
selection on QCDFlat offline jets (unweighted pT-hat, HT 150-800), with truth-tag probabilities of the tag requirement
for the 4 chosen jets (closure of the 3-tag rate in qcd_tagfrac.py). Writes per-event flags for the best variants.
Background here: pT-binned QCD (pT-hat 30-470) weighted to 3000/fb with each bin's generator cross-section, the same
selection with the real UParT tags of the chosen jets (and, for comparison, the truth-tag probabilities above); per
variant the effective number of QCD events; for sculpting, the reconstructed m_4j of QCD passing the tags vs passing
exactly 2 medium tags (the usual data-driven control) in the same mass window. No pT-hat < 30, no ttbar.
"""
import glob
import json
import os
import re
import sys

import numpy as np

out, hh_glob, qcd_glob, gen_glob, kl_glob, qcdw_glob = sys.argv[1:7]
LUMI_PB = 3.0e6
HERE = os.path.dirname(os.path.abspath(__file__))
PAIRINGS = [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]
EDGES = np.array([250, 300, 350, 400, 450, 500, 600, 800, 5000])
PTS, PAIRS, WINS, TAGS = (20, 25, 30), ("mindiff", "chi2"), (30, 40, 50), ("today", "loose")
P_M = {5: 0.84, 4: 0.12, 0: 0.01}  # per-jet tag probabilities at UParT medium (b, c, light)
P_L = {5: 0.94, 4: 0.35, 0: 0.10}  # loose (10% light); c from typical DeepJet-like ratios (assumption)


def load(pat):
    parts = [dict(np.load(f)) for f in sorted(glob.glob(pat))]
    ev = {k: np.concatenate([p[k] for p in parts]) for k in ("lumi", "event", "njet")}
    jets = {k: np.concatenate([p[k] for p in parts]) for k in parts[0] if k not in ev}
    return ev, jets


def good(j, ptmin):
    return (j["pt"] > ptmin) & (abs(j["eta"]) < 2.5) & (j["nconst"] > 1) & (j["nhf"] < 0.9) & (j["nemf"] < 0.9)


resp = json.load(open(os.path.join(HERE, "b_response.json")))
resp_pt = np.array([np.sqrt(lo * min(hi, 400.0)) for lo, hi, _, _ in resp])
resp_val = np.array([r for _, _, r, _ in resp])
b_corr = lambda pt: 1 / np.interp(np.log(pt), np.log(resp_pt), resp_val)


def p4(pt, eta, phi, m):
    px, py, pz = pt * np.cos(phi), pt * np.sin(phi), pt * np.sinh(eta)
    return np.array([np.sqrt(px**2 + py**2 + pz**2 + m**2), px, py, pz])


def mass(a, b):
    s = a + b
    return np.sqrt(max(s[0] ** 2 - s[1] ** 2 - s[2] ** 2 - s[3] ** 2, 0.0))


def evaluate(j, wp):
    """Per event and jet threshold: tag counts, true-b count of the chosen 4, distances for each pairing rule."""
    res = {}
    for ptmin in PTS:
        g = good(j, ptmin)
        if g.sum() < 4:
            continue
        b = j["upart"][g]
        top = np.argsort(-b)[:4]
        sel = {k: j[k][g][top] for k in ("pt", "eta", "phi", "mass", "flav")}
        c = b_corr(sel["pt"])
        v = [p4(sel["pt"][k] * c[k], sel["eta"][k], sel["phi"][k], sel["mass"][k] * c[k]) for k in range(4)]
        dists = {}
        for rule in PAIRS:
            if rule == "mindiff":
                best = min(PAIRINGS, key=lambda pr: abs(mass(v[pr[0][0]], v[pr[0][1]]) - mass(v[pr[1][0]], v[pr[1][1]])))
            else:
                best = min(PAIRINGS, key=lambda pr: (mass(v[pr[0][0]], v[pr[0][1]]) - 125) ** 2 + (mass(v[pr[1][0]], v[pr[1][1]]) - 125) ** 2)
            h = sorted([best[0], best[1]], key=lambda pr: -(v[pr[0]] + v[pr[1]])[1:3].dot((v[pr[0]] + v[pr[1]])[1:3]))
            dists[rule] = float(np.hypot(mass(v[h[0][0]], v[h[0][1]]) - 125, mass(v[h[1][0]], v[h[1][1]]) - 120))
        any_d = min(np.hypot(mass(v[a[0]], v[a[1]]) - 125, mass(v[bb[0]], v[bb[1]]) - 120) for pr in PAIRINGS for a, bb in (pr, pr[::-1]))
        fl = np.where(np.isin(sel["flav"], [4, 5]), sel["flav"], 0)
        s4 = v[0] + v[1] + v[2] + v[3]
        m4j = float(np.sqrt(max(s4[0] ** 2 - s4[1] ** 2 - s4[2] ** 2 - s4[3] ** 2, 0.0)))
        res[ptmin] = {"nm": int((b[top] > wp["M"]).sum()), "nl": int((b[top] > wp["L"]).sum()), "nb_true": int((sel["flav"] == 5).sum()),
                      "d": dists, "d_any": float(any_d), "flav": fl, "m4j": m4j}
    return res


def tag_ok(r, tags):
    nm, nl = r["nm"], r["nl"]
    return ((nm == 4) | ((nm == 3) & (nl == 4))) if tags == "today" else ((nm >= 3) | (nl == 4))


def tag_prob(fl, tags):
    """Truth-tag probability of the tag requirement for 4 jets of flavours fl."""
    pm = np.array([P_M[int(f)] for f in fl]); pl = np.array([P_L[int(f)] for f in fl])
    # enumerate per-jet states: 2 = M, 1 = L not M, 0 = fail
    from itertools import product
    tot = 0.0
    for st in product((0, 1, 2), repeat=4):
        p = np.prod([pm[k] if s == 2 else (pl[k] - pm[k]) if s == 1 else (1 - pl[k]) for k, s in enumerate(st)])
        nm, nl = sum(s == 2 for s in st), sum(s >= 1 for s in st)
        ok = ((nm == 4) or (nm == 3 and nl == 4)) if tags == "today" else ((nm >= 3) or (nl == 4))
        tot += p * ok
    return tot


# working points (as offline_sel.py)
_, qj = load(qcd_glob)
light = good(qj, 30) & (qj["flav"] == 0)
wp = {name: float(np.quantile(qj["upart"][light], 1 - mis)) for name, mis in (("L", 0.1), ("M", 0.01))}

# signal
ev, jj = load(hh_glob)
g = {k: np.concatenate([np.load(f)[k] for f in sorted(glob.glob(gen_glob))]) for k in ("lumi", "event", "mhh")}
gp = {(l, e): i for i, (l, e) in enumerate(zip(g["lumi"], g["event"]))}
has = np.array([(l, e) in gp for l, e in zip(ev["lumi"], ev["event"])])
mhh = np.array([g["mhh"][gp[(l, e)]] if (l, e) in gp else -1 for l, e in zip(ev["lumi"], ev["event"])])
# kappa_lambda information weight per event (as make_page_plots.py section 9)
nano = {}
for f in sorted(glob.glob(kl_glob)):
    m = np.load(f)["mhh"]
    nano[float(re.search(r"kl(\d+p\d+)", f).group(1).replace("p", "."))] = m[m > 0]
bins = np.concatenate([np.arange(240, 600, 20), np.arange(600, 800, 50), [800, 1000, 1300, 5000]])
dens = {kl: np.histogram(m, bins)[0] / len(m) for kl, m in nano.items()}
XS = lambda k: (70.38 - 51.85 * k + 11.42 * k ** 2) / (70.38 - 51.85 + 11.42)
ks = np.array([0.0, 1.0, 2.45])
S3 = np.array([XS(k) * dens[k] for k in ks])
cf = np.array([np.polyfit(ks, S3[:, i], 2) for i in range(S3.shape[1])])
ds, s1 = 2 * cf[:, 0] + cf[:, 1], S3[1]
w_info = np.where(has, (ds / np.maximum(s1, 1e-12))[np.clip(np.digitize(mhh, bins) - 1, 0, len(bins) - 2)] ** 2, 0.0)

offs = np.concatenate([[0], np.cumsum(ev["njet"])])
n = len(ev["lumi"])
evals = [evaluate({k: v[offs[i]:offs[i + 1]] for k, v in jj.items()}, wp) for i in range(n)]
print(f"HH: {n} events, {has.mean():.3f} with generator m_HH", flush=True)

ib = np.clip(np.digitize(mhh, EDGES) - 1, 0, len(EDGES) - 2)
per_bin = lambda f: [float(f[has & (ib == b)].mean()) if (has & (ib == b)).any() else 0.0 for b in range(len(EDGES) - 1)]
res = {"edges": EDGES.tolist(), "n_hh": int(has.sum()), "wp": wp, "events_per_bin": [int((has & (ib == b)).sum()) for b in range(len(EDGES) - 1)]}

# cutflow of today's selection
r30 = [e.get(30) for e in evals]
step = {"4 jets pT>30": np.array([r is not None for r in r30])}
step["top-4 b-score jets are true b"] = step["4 jets pT>30"] & np.array([r is not None and r["nb_true"] == 4 for r in r30])
step["tags (4M or 3M+1L)"] = np.array([r is not None and tag_ok(r, "today") for r in r30])
step["+ any pairing in window"] = step["tags (4M or 3M+1L)"] & np.array([r is not None and r["d_any"] < 30 for r in r30])
step["+ chosen pairing in window (today)"] = step["tags (4M or 3M+1L)"] & np.array([r is not None and r["d"]["mindiff"] < 30 for r in r30])
res["cutflow_today"] = {k: per_bin(v) for k, v in step.items()}
for k, v in res["cutflow_today"].items():
    print(f"  {k:38s}", " ".join(f"{x:.3f}" for x in v), flush=True)

# variants
var = {}
flags = {}
for pt in PTS:
    for pr in PAIRS:
        for w in WINS:
            for tg in TAGS:
                name = f"pt{pt}_{pr}_w{w}_{tg}"
                f = np.array([(e.get(pt) is not None) and tag_ok(e[pt], tg) and e[pt]["d"][pr] < w for e in evals]) & has
                var[name] = {"eff_bins": per_bin(f), "eff_all": float(f[has].mean()), "eff_lt400": float(f[has & (mhh < 400)].mean()),
                             "info_frac": float((w_info * f).sum() / w_info.sum())}
                flags[name] = f

# QCD background: pT-binned samples, cross-section weights, real tags (and truth-tag probabilities for comparison)
qfiles = sorted(f for f in glob.glob(qcdw_glob) if "QCDFlat" not in os.path.basename(f))
samples = sorted({os.path.basename(f).rsplit("_", 1)[0] for f in qfiles})
res["qcd_samples"] = {}
qevals, qw, qsamp = [], [], []
for smp in samples:
    fs = [f for f in qfiles if os.path.basename(f).rsplit("_", 1)[0] == smp]
    xs = [float(np.load(f)["xsec"][0]) for f in fs]
    xs = np.mean([x for x in xs if x > 0])
    qev, qj2 = load(os.path.dirname(fs[0]) + f"/{smp}_*.npz")
    w = xs * LUMI_PB / len(qev["lumi"])
    res["qcd_samples"][smp] = {"files": len(fs), "events": int(len(qev["lumi"])), "xsec_pb": float(xs), "weight": float(w)}
    qoffs = np.concatenate([[0], np.cumsum(qev["njet"])])
    for i in range(len(qev["lumi"])):
        j = {k: v[qoffs[i]:qoffs[i + 1]] for k, v in qj2.items()}
        if (j["pt"] > 20).sum() < 4:
            continue
        ht = j["pt"][(j["pt"] > 30) & (abs(j["eta"]) < 2.5)].sum()
        if not 150 < ht < 800:
            continue
        qevals.append(evaluate(j, wp))
        qw.append(w)
        qsamp.append(smp)
    print(f"QCD {smp}: {len(fs)} files, {len(qev['lumi'])} events, xsec {xs:.4g} pb, weight {w:.4g}", flush=True)
qw = np.array(qw)
print(f"QCD: {len(qevals)} events with >= 4 jets and HT 150-800", flush=True)
for name in var:
    pt, pr, w, tg = name.split("_")[0][2:], name.split("_")[1], name.split("_")[2][1:], name.split("_")[3]
    pt, w = int(pt), int(w)
    kin = np.array([e.get(pt) is not None and e[pt]["d"][pr] < w for e in qevals])
    real = kin & np.array([e.get(pt) is not None and bool(tag_ok(e[pt], tg)) for e in qevals])
    prob = np.array([tag_prob(e[pt]["flav"], tg) if k else 0.0 for e, k in zip(qevals, kin)])
    var[name]["qcd_events"] = float((qw * real).sum())
    var[name]["qcd_events_truthprob"] = float((qw * prob).sum())
    var[name]["qcd_neff"] = float((qw * real).sum() ** 2 / max((qw ** 2 * real).sum(), 1e-30))
    var[name]["qcd_nraw"] = int(real.sum())
    var[name]["qcd_frac"] = var[name]["qcd_events"]  # absolute events at 3000/fb (ratios below)
    if name in ("pt30_mindiff_w30_today", "pt20_chi2_w30_today", "pt20_chi2_w40_today"):
        two = kin & np.array([e.get(pt) is not None and e[pt]["nm"] == 2 for e in qevals])
        m4 = np.array([e[pt]["m4j"] if e.get(pt) is not None else 0.0 for e in qevals])
        medges = np.array([200, 250, 300, 350, 400, 450, 500, 600, 800, 1500])
        h4, h2 = np.histogram(m4[real], medges, weights=qw[real])[0], np.histogram(m4[two], medges, weights=qw[two])[0]
        e4 = np.sqrt(np.histogram(m4[real], medges, weights=qw[real] ** 2)[0])
        var[name]["sculpting"] = {"m4j_edges": medges.tolist(), "tagged": h4.tolist(), "tagged_err": e4.tolist(),
                                  "two_medium_tags": h2.tolist(),
                                  "tagged_shape": (h4 / max(h4.sum(), 1e-30)).tolist(), "two_tag_shape": (h2 / max(h2.sum(), 1e-30)).tolist()}
ref = var["pt30_mindiff_w30_today"]
for name, v in var.items():
    v["info_rel"] = v["info_frac"] / ref["info_frac"]
    v["qcd_rel"] = v["qcd_frac"] / max(ref["qcd_frac"], 1e-300)
    v["fom_rel"] = v["info_rel"] / np.sqrt(max(v["qcd_rel"], 1e-300))  # information-weighted S / sqrt(B), relative to today
    v["qcd_rel_truthprob"] = v["qcd_events_truthprob"] / max(ref["qcd_events_truthprob"], 1e-300)
    v["fom_rel_truthprob"] = v["info_rel"] / np.sqrt(max(v["qcd_rel_truthprob"], 1e-300))
    v["qcd_rel_err"] = v["qcd_rel"] * np.sqrt(1 / max(v["qcd_neff"], 1e-9) + 1 / max(ref["qcd_neff"], 1e-9))
res["variants"] = var
top = sorted(var, key=lambda k: -var[k]["fom_rel"])[:8]
print("variants by information-weighted S/sqrt(B) relative to today:", flush=True)
for name in ["pt30_mindiff_w30_today"] + top:
    v = var[name]
    print(f"  {name:28s} all {v['eff_all']:.3f}  m<400 {v['eff_lt400']:.3f}  info {v['info_frac']:.3f} (x{v['info_rel']:.2f})  "
          f"QCD x{v['qcd_rel']:.2f} +- {v['qcd_rel_err']:.2f} (truth-prob x{v['qcd_rel_truthprob']:.2f}, n_eff {v['qcd_neff']:.0f})  FOM x{v['fom_rel']:.2f}", flush=True)
res["best_by_fom"] = top
json.dump(res, open(out, "w"), indent=1)
keep = ["pt30_mindiff_w30_today"] + top[:3] + ["pt20_chi2_w40_today", "pt25_chi2_w40_today", "pt20_mindiff_w40_loose"]
np.savez(out.replace(".json", "_flags.npz"), lumi=ev["lumi"], event=ev["event"], **{k: flags[k] for k in dict.fromkeys(keep)})
print("wrote", out)

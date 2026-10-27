#!/usr/bin/env python3
"""Pixel scouting where pixels exist: an HLT scouting stream for L1-accepted crossings. How much low-m_HH HH->4b does
the HLT output bandwidth cost?

    python3 hlt_scouting.py OUT.json SEED_PLANE.npz "HH_OFFLINE_GLOB" GENMHH_GLOB KL_GLOB LOWMASS_FLAGS.npz QCDPT_DIR OFFLINE_W_DIR
Pixel data are read out only for L1-accepted crossings (750 kHz); a 40 MHz pixel scouting stream cannot exist with the
CROC. What remains is HLT scouting: reduced HLT objects (jets, b-tags from pixel / full tracks) written at a higher
rate than the normal HLT output. This script asks whether that buys HH->4b acceptance:
  L1 streams: the planned HT seeds (menu), and menu + the NN b-tag seed at +2.5 / +15 kHz (thresholds from minimum
              bias, even events, as scouting.py).
  HLT proxy: offline AK4 PUPPI jets (Phase-2 HLT runs near-offline reconstruction) and a b tagger (UParT; PNet and
              DeepJet as weaker stand-ins); selection grid: >= 4 jets above pT_min, HT (jets > 30) above HT_min,
              >= k tags at the loose (10%) or medium (1%) light-jet working point.
  Signal: SM HH->4b, final acceptance = L1 stream x HLT selection x analysis selection (offline_lowmass flags:
              today's and the low-mass-optimised one); kappa_lambda-information-weighted and below m_HH 400.
  Background rate: pT-binned QCD (pT-hat 30-470) with generator cross-sections at 7.5e34 (0.075 / pb / s), through
              the same L1 streams (its own L1 objects) and HLT selection. Not included: pT-hat < 30 (irrelevant after
              these L1 seeds; check: the QCD menu rate vs the minimum-bias 19 kHz), ttbar (<= 74 Hz in total).
Output: per L1 stream, the best HLT selection under each output budget (Pareto front of rate vs information).
"""
import glob
import json
import os
import re
import sys

import numpy as np

os.environ.setdefault("HT_MIN", "150")
os.environ.setdefault("MB_TOTAL", "1999360")
import direct_rate as D  # noqa: E402

L_PB_S = 0.075  # 7.5e34 cm^-2 s^-1 in pb^-1 s^-1
MB_TOTAL = int(os.environ["MB_TOTAL"])
TAGGERS = ("upart", "pnet", "deepjet")
PTS, HTS, NTAGS, WPS = (20, 25, 30), (0, 150, 200, 250, 300, 350, 400), (2, 3, 4), ("L", "M")
BUDGETS_KHZ = (0.05, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0)
ANALYSES = ("pt30_mindiff_w30_today", "pt20_chi2_w30_today")


def good(j, ptmin):
    return (j["pt"] > ptmin) & (abs(j["eta"]) < 2.5) & (j["nconst"] > 1) & (j["nhf"] < 0.9) & (j["nemf"] < 0.9)


def hlt_features(files, keys, wp):
    """Per event (lumi, event): HT (jets > 30), number of good jets and tag counts per (pT_min, tagger, WP)."""
    out = {}
    for f in files:
        d = np.load(f)
        off = np.concatenate([[0], np.cumsum(d["njet"])])
        for i in range(len(d["njet"])):
            k = (int(d["lumi"][i]), int(d["event"][i]))
            if keys is not None and k not in keys:
                continue
            j = {c: d[c][off[i]:off[i + 1]] for c in ("pt", "eta", "nconst", "nhf", "nemf") + TAGGERS}
            r = {"ht": float(j["pt"][good(j, 30)].sum())}
            for pt in PTS:
                g = good(j, pt)
                r[f"n{pt}"] = int(g.sum())
                for t in TAGGERS:
                    for w in WPS:
                        r[f"t{pt}_{t}_{w}"] = int((j[t][g] > wp[t][w]).sum())
            out[k] = r
    return out


def table(keys, feats):
    cols = list(next(iter(feats.values())).keys())
    miss = {c: -1 for c in cols}
    return {c: np.array([feats.get(k, miss)[c] for k in keys]) for c in cols}, np.array([k in feats for k in keys])


def passes(T, pt, ht, nt, tagger, wp):
    return (T[f"n{pt}"] >= 4) & (T["ht"] > ht) & (T[f"t{pt}_{tagger}_{wp}"] >= nt)


def main():
    out, sp_path, hh_off, gen_glob, kl_glob, lm_flags, qdir, owdir = sys.argv[1:9]
    # working points on QCDFlat light jets > 30 (as offline_sel.py)
    q = [np.load(f) for f in sorted(glob.glob("/scratch/submit/cms/novaka/l1pixels/offline/QCDFlat_*.npz"))]
    wp = {}
    for t in TAGGERS:
        s = np.concatenate([x[t][(x["pt"] > 30) & (abs(x["eta"]) < 2.5) & (x["flav"] == 0)] for x in q])
        wp[t] = {"L": float(np.quantile(s, 0.9)), "M": float(np.quantile(s, 0.99))}

    # L1 streams from the seed plane (HH, minimum bias); thresholds on even events
    sp = np.load(sp_path)
    ev_hh, ev_mb = sp["hh_event"] % 2 == 0, sp["mb_event"] % 2 == 0
    w_fold = len(sp["mb_ht"]) / MB_TOTAL * D.BX_KHZ / ev_mb.sum()
    streams = {"menu": None}
    thr = {}
    for khz in (2.5, 15.0):
        e, h, s = D.best(sp["hh_nn"][ev_hh], sp["hh_ht"][ev_hh], np.ones(ev_hh.sum(), bool), sp["mb_nn"][ev_mb], sp["mb_ht"][ev_mb],
                         np.full(ev_mb.sum(), w_fold), khz, sp["hh_menu"][ev_hh].astype(bool), sp["mb_menu"][ev_mb].astype(bool))
        thr[f"menu+NN {khz:g} kHz"] = (h, s)
    l1 = lambda ht, menu, nn, name: menu.astype(bool) if name == "menu" else (menu.astype(bool) | ((ht > thr[name][0]) & (nn > thr[name][1])))
    names = ["menu"] + list(thr)
    mb_rate = {n: float(l1(sp["mb_ht"], sp["mb_menu"], sp["mb_nn"], n).sum() * D.BX_KHZ / MB_TOTAL) for n in names}
    res = {"wp": wp, "l1_thresholds": {k: list(map(float, v)) for k, v in thr.items()}, "l1_rate_mb_khz": mb_rate}
    print("L1 stream rates (minimum bias):", mb_rate, flush=True)

    # signal: odd HH events with offline jets, gen m_HH, kappa_lambda information weight, analysis flags
    keys = [(int(l), int(e)) for l, e in zip(sp["hh_lumi"], sp["hh_event"])]
    hf = hlt_features(sorted(glob.glob(hh_off)), set(keys), wp)
    TH, has_off = table(keys, hf)
    g = {k: np.concatenate([np.load(f)[k] for f in sorted(glob.glob(gen_glob))]) for k in ("lumi", "event", "mhh")}
    gpos = {(int(l), int(e)): i for i, (l, e) in enumerate(zip(g["lumi"], g["event"]))}
    mhh = np.array([g["mhh"][gpos[k]] if k in gpos else -1.0 for k in keys])
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
    info_bin = ((2 * cf[:, 0] + cf[:, 1]) / np.maximum(S3[1], 1e-12)) ** 2
    w_info = np.where(mhh > 0, info_bin[np.clip(np.digitize(mhh, bins) - 1, 0, len(bins) - 2)], 0.0)
    lf = np.load(lm_flags)
    lpos = {(int(l), int(e)): i for i, (l, e) in enumerate(zip(lf["lumi"], lf["event"]))}
    li = np.array([lpos.get(k, -1) for k in keys])
    use = (~ev_hh) & has_off & (mhh > 0) & (li >= 0)
    print(f"HH: {use.sum()} odd events with offline jets, gen m_HH and analysis flags", flush=True)

    # QCD: L1 objects from the pixel ntuples, offline jets from offline_w, cross-section weights
    qT, qw, ql1 = [], [], {n: [] for n in names}
    res["qcd_bins"] = {}
    for f_bin in sorted({os.path.basename(f).split("_")[1] for f in glob.glob(f"{qdir}/perfNano_QCDPt*_*.root")}, key=lambda s: int(s[5:])):
        files = sorted(glob.glob(f"{qdir}/perfNano_{f_bin}_*.root"))
        owf = sorted(glob.glob(f"{owdir}/{f_bin}_*.npz"))
        xs = np.mean([float(np.load(f)["xsec"][0]) for f in owf if float(np.load(f)["xsec"][0]) > 0])
        qe = D.events(",".join(files))
        qk = [(int(l), int(e)) for l, e in zip(qe["lumi"], qe["event"])]
        T, ok = table(qk, hlt_features(owf, set(qk), wp))
        w = xs / len(qk) * L_PB_S  # Hz per event
        for n in names:
            ql1[n].append(l1(qe["ht"], qe["menu"], qe["nn_sum"], n) & ok)
        qT.append(T)
        qw.append(np.full(len(qk), w))
        res["qcd_bins"][f_bin] = {"events": len(qk), "xsec_pb": float(xs), "offline_matched": float(ok.mean()),
                                  "menu_rate_khz": float((ql1["menu"][-1]).sum() * w / 1e3)}
        print(f"{f_bin}: {len(qk)} events, xsec {xs:.4g} pb, offline matched {ok.mean():.3f}, menu rate "
              f"{res['qcd_bins'][f_bin]['menu_rate_khz']:.2f} kHz", flush=True)
    QT = {c: np.concatenate([t[c] for t in qT]) for c in qT[0]}
    QW = np.concatenate(qw)
    QL1 = {n: np.concatenate(v) for n, v in ql1.items()}
    res["l1_rate_qcd_khz"] = {n: float((QW * QL1[n]).sum() / 1e3) for n in names}
    print("L1 stream rates (QCD, pT-hat > 30):", res["l1_rate_qcd_khz"], flush=True)

    # scan
    res["streams"] = {}
    for n in names:
        a_h = l1(sp["hh_ht"], sp["hh_menu"], sp["hh_nn"], n) & use
        rs = res["streams"][n] = {"l1_rate_khz_mb": mb_rate[n]}
        for ana in ANALYSES:
            af = np.where(li >= 0, lf[ana][np.maximum(li, 0)], False) & use
            den_info, den_low = (w_info * af).sum(), (af & (mhh < 400)).sum()
            base = {"info": float((w_info * af * a_h).sum() / den_info), "low": float((af & a_h & (mhh < 400)).sum() / den_low),
                    "all": float((af & a_h).sum() / af.sum())}
            pts = []
            for t in TAGGERS:
                for pt in PTS:
                    for ht in HTS:
                        for nt in NTAGS:
                            for wpn in WPS:
                                ph = passes(TH, pt, ht, nt, t, wpn)
                                pq = passes(QT, pt, ht, nt, t, wpn) & QL1[n]
                                rate = float((QW * pq).sum() / 1e3)
                                pts.append({"sel": f"{t} pt{pt} ht{ht} {nt}{wpn}", "tagger": t, "rate_khz": rate,
                                            "rate_err_khz": float(np.sqrt((QW ** 2 * pq).sum()) / 1e3),
                                            "info": float((w_info * af * a_h * ph).sum() / den_info),
                                            "low": float((af & a_h & ph & (mhh < 400)).sum() / den_low),
                                            "all": float((af & a_h & ph).sum() / af.sum())})
            front = {}
            for t in TAGGERS + ("any",):
                for bud in BUDGETS_KHZ:
                    c = [p for p in pts if p["rate_khz"] <= bud and (t == "any" or p["tagger"] == t)]
                    best = max(c, key=lambda p: p["info"]) if c else None
                    front[f"{t}@{bud:g}"] = best
            rs[ana] = {"l1_only": base, "front": front, "points": pts}
            print(f"[{n} | analysis {ana}] L1 alone keeps info {base['info']:.3f}, m_HH<400 {base['low']:.3f}", flush=True)
            for bud in BUDGETS_KHZ:
                b = front[f"upart@{bud:g}"]
                if b:
                    print(f"    HLT budget {bud:5g} kHz: info {b['info']:.3f} (x{b['info'] / max(base['info'], 1e-9):.2f} of L1), "
                          f"m_HH<400 {b['low']:.3f}, rate {b['rate_khz']:.3g} +- {b['rate_err_khz']:.2g} kHz  [{b['sel']}]", flush=True)
    json.dump(res, open(out, "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()

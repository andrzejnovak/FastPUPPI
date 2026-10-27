#!/usr/bin/env python3
"""kappa_lambda at L1-object level with a QCD multijet background that carries flavour: closure against minimum bias,
then NN vs pixel seeds with propagated finite-sample uncertainty.

    python3 kl_qcdbkg.py OUT.json HH4B_GLOB MB_GLOBS L1EXT_LISTS(hh:qcd:mb1:mb2) SEED_PLANE.npz GENMHH_GLOB KL_GLOB \
        QCDPT_DIR QCDPT_LISTS_DIR(lists_l1ext_<bin>.npz) OFFLINE_W_DIR
Same event selection, Higgs window, signal templates, seeds (thresholds from minimum bias on even events, SEED_KHZ added
rate) and likelihood as scouting.py. Background: the pT-binned QCD samples (pT-hat 30-470, PU 200, pixel ntuples),
each event weighted by sigma_bin x 3000/fb / N_bin (generator cross-section from dump_offline.py), passed through the
same L1 seeds; offline 4-tag / 3-tag probabilities from its own offline jets (truth-tagged b 0.84, c 0.12, light 0.01,
as scouting.py; real UParT tags as a check). Unlike the minimum bias, these events have generator flavour for every
jet, so the background of the seed-added events needs no transfer from another sample.
Validation: yields per stream and HT bin, QCD vs minimum bias (QCD lacks pT-hat < 30 and non-QCD processes);
finite sample: Poisson bootstrap of the QCD events (N_BOOT replicas) -> spread of Z_SM, 68% width and the pixel - NN
difference. Statistical only otherwise.
"""
import glob
import json
import os
import sys

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

os.environ.setdefault("HT_MIN", "150")
os.environ.setdefault("MB_TOTAL", "1999360")
import direct_rate as D  # noqa: E402
import scouting as SC  # noqa: E402
from train_sets import jet_features, kin_weights, load, pixel_summary  # noqa: E402

LUMI_PB = 3.0e6
N_BOOT = int(os.environ.get("N_BOOT", "40"))
N_MIN_Q = int(os.environ.get("N_MIN_Q", "20"))  # unweighted QCD events per score category
HT_EDGES = np.array([150, 200, 250, 300, 360, 450, 600, 1e9])
UPART_M = None  # medium working point (1% light mistag on QCDFlat jets > 30), set in main


def classifier(fh, fq):
    """The L1 pixel tagger of seed_plane.tagger (same training sets and settings), returned as a model."""
    lh, lq = load(fh), load(fq)
    b = {k: v[(lh["flav"] == 5) & (lh["event"] % 2 == 0)] for k, v in lh.items()}
    l = {k: v[(lq["flav"] == 0) & (lq["event"] % 2 == 0)] for k, v in lq.items()}
    tr = {k: np.concatenate([b[k], l[k]]) for k in b}
    y = np.concatenate([np.ones(len(b["pt"])), np.zeros(len(l["pt"]))])
    w = np.concatenate([np.ones(len(b["pt"])), kin_weights(b, l)])
    w[y == 0] *= y.sum() / w[y == 0].sum()
    feats = lambda d: np.column_stack([jet_features(d), pixel_summary(d, True)])
    clf = HistGradientBoostingClassifier(max_iter=300, max_leaf_nodes=31, random_state=1).fit(feats(tr), y, sample_weight=w)
    return lambda d: clf.predict_proba(feats(d))[:, 1]


def offline_tags(ev, files):
    """Per event: truth-tag P(4), P(exactly 3) of the 4 leading offline jets (pT > 25, |eta| < 2.5), and the real UParT
    medium-tag count of the same jets; coverage flag."""
    rows = {}
    for f in files:
        d = np.load(f)
        off = np.concatenate([[0], np.cumsum(d["njet"])])
        for i in range(len(d["njet"])):
            sl = slice(off[i], off[i + 1])
            pt, eta, fl, up = d["pt"][sl], d["eta"][sl], d["flav"][sl], d["upart"][sl]
            m = (pt > 25) & (abs(eta) < 2.5)
            if m.sum() < 4:
                rows[(int(d["lumi"][i]), int(d["event"][i]))] = (0.0, 0.0, 0)
                continue
            o = np.argsort(-pt[m])[:4]
            p = np.select([fl[m][o] == 5, fl[m][o] == 4], [SC.OFFLINE_P[5], SC.OFFLINE_P[4]], SC.OFFLINE_P[0])[None, :]
            p4, p3 = SC.tag_probs(p)
            rows[(int(d["lumi"][i]), int(d["event"][i]))] = (p4[0], p3[0], int((up[m][o] > UPART_M).sum()))
    got = [rows.get((int(l), int(e))) for l, e in zip(ev["lumi"], ev["event"])]
    cov = np.array([g is not None for g in got])
    got = [g if g is not None else (0.0, 0.0, 0) for g in got]
    return np.array([g[0] for g in got]), np.array([g[1] for g in got]), np.array([g[2] for g in got]), cov


def main():
    global UPART_M
    out, hh_pat, mb_pat, l1lists, sp_path, gen_glob, kl_glob, qdir, qldir, owdir = sys.argv[1:11]
    fh, fq, fm1, fm2 = l1lists.split(":")
    qf = np.concatenate([np.load(f)["upart"][(np.load(f)["pt"] > 30) & (np.load(f)["flav"] == 0)]
                         for f in sorted(glob.glob("/scratch/submit/cms/novaka/l1pixels/offline/QCDFlat_*.npz"))])
    UPART_M = float(np.quantile(qf, 0.99))
    print("training the L1 pixel tagger", flush=True)
    score = classifier(fh, fq)
    lh = load(fh)
    hh, mb = SC.read(hh_pat), SC.read(mb_pat)
    SC.attach(hh, lh, score(lh))
    SC.kinematics(hh)
    lm1, lm2 = load(fm1), load(fm2)
    lm = {k: np.concatenate([lm1[k], lm2[k]]) for k in lm1}
    SC.attach(mb, lm, score(lm))
    SC.kinematics(mb)
    sp = np.load(sp_path)
    for ev, p in ((hh, "hh"), (mb, "mb")):
        pos = {(l, e): i for i, (l, e) in enumerate(zip(sp[f"{p}_lumi"], sp[f"{p}_event"]))}
        ix = np.array([pos[(l, e)] for l, e in zip(ev["lumi"], ev["event"])])
        for k in ("ht", "menu", "nn", "l1"):
            ev[f"sp_{k}"] = sp[f"{p}_{k}"][ix]

    # QCD pT bins: L1 objects, seed sums, flavour, offline tags, weights
    bins = sorted({os.path.basename(f).split("_")[1] for f in glob.glob(f"{qdir}/perfNano_QCDPt*_*.root")}, key=lambda s: int(s[5:]))
    qparts = []
    res = {"setup": {"seed_khz": SC.SEED_KHZ, "upart_medium": UPART_M, "qcd_bins": {}}}
    for bn in bins:
        files = sorted(glob.glob(f"{qdir}/perfNano_{bn}_*.root"))
        owf = sorted(glob.glob(f"{owdir}/{bn}_*.npz"))
        xs = np.mean([float(np.load(f)["xsec"][0]) for f in owf if float(np.load(f)["xsec"][0]) > 0])
        q = SC.read(",".join(files))
        ql = load(f"{qldir}/lists_l1ext_{bn}.npz")  # merge_lists.py output of the bin's per-file lists
        SC.attach(q, ql, score(ql))
        SC.kinematics(q)
        qe = D.events(",".join(files))
        q["sp_ht"], q["sp_menu"], q["sp_nn"] = qe["ht"], qe["menu"], qe["nn_sum"]
        q["sp_l1"] = D.jet_scores(qe, ql, score(ql))
        q["off4"], q["off3"], q["offn"], q["offcov"] = offline_tags(q, owf)
        q["w"] = np.full(len(q["ht"]), xs * LUMI_PB / len(q["ht"]))
        q["bin"] = np.full(len(q["ht"]), bn)
        res["setup"]["qcd_bins"][bn] = {"files": len(files), "events": int(len(q["ht"])), "xsec_pb": float(xs),
                                        "weight": float(q["w"][0]), "offline_coverage": float(q["offcov"].mean())}
        print(f"{bn}: {len(files)} files, {len(q['ht'])} events, xsec {xs:.4g} pb, weight {q['w'][0]:.3g}, "
              f"offline coverage {q['offcov'].mean():.3f}", flush=True)
        qparts.append(q)
    qcd = {k: np.concatenate([p[k] for p in qparts]) for k in qparts[0]}

    # seeds: thresholds from minimum bias (even events), as scouting.py
    ev_hh, ev_mb = hh["event"] % 2 == 0, mb["event"] % 2 == 0
    w_fold = len(mb["ht"]) / SC.MB_TOTAL * D.BX_KHZ / ev_mb.sum()
    fid = np.ones(len(hh["ht"]), bool)
    seeds = {"menu": (hh["sp_menu"].astype(bool), mb["sp_menu"].astype(bool), qcd["sp_menu"].astype(bool))}
    for tag in ("nn", "l1"):
        e, h, s = D.best(hh[f"sp_{tag}"][ev_hh], hh["sp_ht"][ev_hh], fid[ev_hh], mb[f"sp_{tag}"][ev_mb], mb["sp_ht"][ev_mb],
                         np.full(ev_mb.sum(), w_fold), SC.SEED_KHZ, hh["sp_menu"][ev_hh].astype(bool), mb["sp_menu"][ev_mb].astype(bool))
        seeds[tag] = tuple(((d["sp_ht"] > h) & (d[f"sp_{tag}"] > s)) | seeds["menu"][i] for i, d in enumerate((hh, mb, qcd)))
        res["setup"][f"seed_{tag}"] = {"ht": float(h), "sum": float(s)}
        print(f"seed menu + {tag}: HT > {h:.0f}, sum > {s:.2f}", flush=True)

    # window, signal weights (as scouting.py)
    base = lambda d: d["n4"] & (d["ht"] > SC.HT_CUT)
    t4 = base(hh) & (hh["flav"] == 5).all(1)
    c1, c2 = np.median(hh["m1"][t4]), np.median(hh["m2"][t4])
    r1, r2 = 1.4826 * np.median(abs(hh["m1"][t4] - c1)), 1.4826 * np.median(abs(hh["m2"][t4] - c2))
    win = lambda d: base(d) & (np.hypot((d["m1"] - c1) / r1, (d["m2"] - c2) / r2) < 1.6)
    hw, mw, qw = win(hh), win(mb), win(qcd)
    g = {k: np.concatenate([np.load(f)[k] for f in sorted(glob.glob(gen_glob))]) for k in ("lumi", "event", "mhh")}
    gpos = {(l, e): i for i, (l, e) in enumerate(zip(g["lumi"], g["event"]))}
    mhh = np.array([g["mhh"][gpos[(l, e)]] for l, e in zip(hh["lumi"], hh["event"])])
    import re
    nano = {}
    for f in sorted(glob.glob(kl_glob)):
        m = np.load(f)["mhh"]
        nano[float(re.search(r"kl(\d+p\d+)", f).group(1).replace("p", "."))] = m[m > 0]
    gb = np.concatenate([np.arange(240, 600, 20), np.arange(600, 800, 50), [800, 1000, 1300, 5000]])
    dens = {kl: np.histogram(m, gb)[0] / len(m) for kl, m in nano.items()}
    ib = np.clip(np.digitize(mhh, gb) - 1, 0, len(gb) - 2)
    odd = ~ev_hh
    w_sm = odd * SC.SIG_SM / odd.sum()
    w_kl = {kl: w_sm * SC.XS(kl) * np.where(dens[1.0] > 0, dens[kl] / np.maximum(dens[1.0], 1e-12), 0.0)[ib] for kl in nano}
    p_hh = np.select([hh["flav"] == 5, hh["flav"] == 4], [SC.OFFLINE_P[5], SC.OFFLINE_P[4]], SC.OFFLINE_P[0])
    h4, h3 = SC.tag_probs(p_hh)
    w_mb = SC.N_BX / SC.MB_TOTAL

    # ---- closure: yields at 3000/fb (no tags), QCD vs minimum bias, per stream and HT bin
    clo = {}
    for name, (am, aq) in {"HT>150, 4 jets": (base(mb), base(qcd)), "window": (mw, qw),
                           "window, menu": (mw & seeds["menu"][1], qw & seeds["menu"][2]),
                           "window, NN seed added": (mw & seeds["nn"][1] & ~seeds["menu"][1], qw & seeds["nn"][2] & ~seeds["menu"][2]),
                           "window, pixel seed added": (mw & seeds["l1"][1] & ~seeds["menu"][1], qw & seeds["l1"][2] & ~seeds["menu"][2])}.items():
        hm = np.histogram(mb["ht"][am], HT_EDGES)[0]
        hq = np.histogram(qcd["ht"][aq], HT_EDGES, weights=qcd["w"][aq])[0]
        hq2 = np.histogram(qcd["ht"][aq], HT_EDGES, weights=qcd["w"][aq] ** 2)[0]
        clo[name] = {"mb_events": hm.tolist(), "mb_yield": (hm * w_mb).tolist(), "qcd_yield": hq.tolist(),
                     "qcd_yield_err": np.sqrt(hq2).tolist(), "qcd_raw": np.histogram(qcd["ht"][aq], HT_EDGES)[0].tolist(),
                     "ratio_qcd_over_mb": [float(a / (b * w_mb)) if b > 0 else None for a, b in zip(hq, hm)],
                     "total_ratio": float(hq.sum() / max(hm.sum() * w_mb, 1e-300)),
                     "total_ratio_err": float(np.sqrt(hq2.sum() / max(hq.sum(), 1e-300) ** 2 + 1 / max(hm.sum(), 1)) * hq.sum() / max(hm.sum() * w_mb, 1e-300))
                     if hq.sum() > 0 else None}
        print(f"closure {name:26s} QCD/MB {clo[name]['total_ratio']:.2f} +- {clo[name]['total_ratio_err'] or 0:.2f}  "
              f"(MB {hm.sum()} events, QCD {int(clo[name]['qcd_raw'] and sum(clo[name]['qcd_raw']))} raw)  per HT bin "
              + " ".join("-" if r is None else f"{r:.2f}" for r in clo[name]["ratio_qcd_over_mb"]), flush=True)
    res["closure"] = {"ht_edges": HT_EDGES.tolist(), "streams": clo}
    # truth-tag vs real UParT tags on QCD (covered events)
    cv = qw & qcd["offcov"]
    res["closure_tags"] = {"P4_truth": float((qcd["w"] * cv * qcd["off4"]).sum()), "N4_real": float((qcd["w"] * cv * (qcd["offn"] == 4)).sum()),
                           "P3_truth": float((qcd["w"] * cv * qcd["off3"]).sum()), "N3_real": float((qcd["w"] * cv * (qcd["offn"] == 3)).sum()),
                           "n4_real_raw": int((cv & (qcd["offn"] == 4)).sum()), "n3_real_raw": int((cv & (qcd["offn"] == 3)).sum())}
    print("tags in the window, truth-tag vs real UParT:", res["closure_tags"], flush=True)

    # ---- fits: per seed, categories menu + seed-added score categories (edges from unweighted QCD quantiles)
    def build(sd, wq):
        ah, am_, aq = seeds[sd]
        cats_h, cats_q = [seeds["menu"][0]], [seeds["menu"][2]]
        if sd != "menu":
            key = f"sp_{sd}"
            added = qw & aq & ~seeds["menu"][2]
            ncat = int(np.clip(added.sum() // N_MIN_Q, 1, 8))
            edges = np.quantile(qcd[key][added], np.linspace(0, 1, ncat + 1)[1:-1]) if ncat > 1 else np.array([])
            for c in range(ncat):
                cats_h.append(ah & ~seeds["menu"][0] & (np.digitize(hh[key], edges) == c))
                cats_q.append(aq & ~seeds["menu"][2] & (np.digitize(qcd[key], edges) == c))
        coef = SC.templates(w_kl, [hw * cm * t for cm in cats_h for t in (h4, h3)], hh["m4j"])
        b, b2, n, thin = [], [], [], []
        for cq in cats_q:
            m = qw & cq & qcd["offcov"]
            thin.append(int(m.sum()))
            # factorised: the category's m_4j shape from all its QCD events x its mean tag probability
            hsh = np.histogram(qcd["m4j"], SC.M4J_BINS, weights=wq * m)[0]
            hn = np.histogram(qcd["m4j"], SC.M4J_BINS, weights=m.astype(float))[0]
            h2 = np.histogram(qcd["m4j"], SC.M4J_BINS, weights=(wq * m) ** 2)[0]
            for p in (qcd["off4"], qcd["off3"]):
                f = (wq * m * p).sum() / max((wq * m).sum(), 1e-300)
                b.append(hsh * f)
                b2.append(h2 * f ** 2)
                n.append(hn)
        return coef, np.concatenate(b), np.concatenate(b2), np.concatenate(n), thin

    def fit(coef, b, b2, n):
        coef, b, b2 = SC.merge(coef, b, b2, n)
        s1 = coef[0] + coef[1] + coef[2]
        ok = b > 0
        z = float(np.sqrt(2 * np.sum(np.where(ok, (s1 + b) * np.log1p(s1 / np.maximum(b, 1e-300)) - s1, 0))))
        q = SC.scan(coef, b)
        i68, w68, _ = SC.interval(q, 1.0)
        q5 = SC.scan(coef, b, truth=5.0)
        return {"Z_SM": z, "kl_68": i68, "width_68": w68, "Z_excl_SM_if_kl5": float(np.sqrt(max(np.interp(1.0, SC.KL_SCAN, q5), 0))),
                "S": float(s1.sum()), "B": float(b.sum()), "n_eff": float(b.sum() ** 2 / max(b2.sum(), 1e-300)), "bins": int(len(b))}

    res["fits"] = {}
    for sd in ("menu", "nn", "l1"):
        coef, b, b2, n, thin = build(sd, qcd["w"])
        r = fit(coef, b, b2, n)
        nc = len(thin)
        r["categories"], r["qcd_events_per_category"] = nc, thin
        r["reliable"] = bool(min(thin) >= N_MIN_Q)  # a category without QCD events has no background estimate
        res["fits"][sd] = r
        print(f"QCD background, seed {sd:5s}: {nc} categories (QCD events {thin}{'' if r['reliable'] else ', TOO FEW'})  S {r['S']:.1f} B {r['B']:.3g} (n_eff {r['n_eff']:.0f})  Z {r['Z_SM']:.2f}  "
              f"kl 68% [{r['kl_68'][0]:+.2f}, {r['kl_68'][1]:+.2f}]  kl=5: SM excluded {r['Z_excl_SM_if_kl5']:.2f} sigma", flush=True)
    # bootstrap of the QCD sample
    rng = np.random.default_rng(11)
    boot = {sd: [] for sd in ("menu", "nn", "l1")}
    for k in range(N_BOOT):
        wq = qcd["w"] * rng.poisson(1.0, len(qcd["w"]))
        for sd in boot:
            boot[sd].append(fit(*build(sd, wq)[:4]))
    res["bootstrap"] = {}
    for sd, rs in boot.items():
        arr = lambda key: np.array([r[key] for r in rs])
        res["bootstrap"][sd] = {k: {"mean": float(arr(k).mean()), "std": float(arr(k).std())} for k in ("Z_SM", "width_68", "Z_excl_SM_if_kl5")}
    d = {k: np.array([a[k] - b_[k] for a, b_ in zip(boot["l1"], boot["nn"])]) for k in ("Z_SM", "width_68", "Z_excl_SM_if_kl5")}
    res["bootstrap"]["pixel_minus_nn"] = {k: {"mean": float(v.mean()), "std": float(v.std()),
                                              "frac_pixel_better": float((v < 0).mean() if k == "width_68" else (v > 0).mean())} for k, v in d.items()}
    for sd, v in res["bootstrap"].items():
        print(f"bootstrap {sd:15s}", json.dumps(v), flush=True)
    json.dump(res, open(out, "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()

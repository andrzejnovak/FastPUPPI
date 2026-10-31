#!/usr/bin/env python3
"""40 MHz L1 scouting for HH->4b with a measured genuine-4b background (private 4b-enriched QCD sample).

    python3 scout4b.py OUT.json HH4B_GLOB L1EXT_HH_LISTS SEED_PLANE.npz GENMHH_GLOB KL_GLOB SCOUTING.json NORM_CHECK.json \
        QCDPT_DIR OFFLINE_W_DIR PRIV_DIR
Background per crossing class:
  - genuine 4b (the 4 leading L1 jets all matched to b generator jets): the private sample QCD4b (Pythia8 HardQCD,
    30 < pT-hat < 300, >= 4 b quarks pT > 15 |eta| < 2.6), weight sigma_before x w / sum w(all generated) x 3000/fb,
    sum w(all) = sum w(passed) x sigma_before / sigma_after per job (bias weights do not average to 1);
  - everything else: the pT-binned QCD (as scout_check.py) without its genuine-4b events, its yields below L1 HT 300
    scaled by minimum bias / QCD (norm_check.json: "one hard scatter + PU 200" double counts there).
BKG_MODE=factorised: per tag category, the m_4j shape of all its background events x its weighted tag fraction
(keeps the m_4j binning when few tagged events exist; default "direct"). Pileup b jets have no generator record anywhere: a lower bound on the b content. pT-hat < 30 is missing.
Tags: perfect (true b) and the L1 NN at weighted-QCD light-jet mistags (0.2%, 1%, 5%). Same signal, window, binning and
likelihood as scouting.py; scouting of all crossings and of the menu-rejected ones (+ triggered menu).
"""
import glob
import json
import os
import sys

import numpy as np

os.environ.setdefault("HT_MIN", "150")
os.environ.setdefault("MB_TOTAL", "1999360")
import direct_rate as D  # noqa: E402
import kl_qcdbkg as KQ  # noqa: E402
import scout_check as SCK  # noqa: E402
import scouting as SC  # noqa: E402
from train_sets import load  # noqa: E402

LUMI_PB = 3.0e6
CACHE = "/scratch/submit/cms/novaka/l1pixels/derived/scout4b_qcdpt_cache.npz"


def read_qcdpt(qdir, owdir):
    if os.path.exists(CACHE):
        return dict(np.load(CACHE))
    parts = []
    for bn in sorted({os.path.basename(f).split("_")[1] for f in glob.glob(f"{qdir}/perfNano_QCDPt*_*.root")}, key=lambda s: int(s[5:])):
        files = sorted(glob.glob(f"{qdir}/perfNano_{bn}_*.root"))
        owf = sorted(glob.glob(f"{owdir}/{bn}_*.npz"))
        xs = np.mean([float(np.load(f)["xsec"][0]) for f in owf if float(np.load(f)["xsec"][0]) > 0])
        q = SC.read(",".join(files))
        SC.kinematics(q)
        q["flav"] = SCK.gen_flavour(files, q)
        q["menu"] = D.events(",".join(files))["menu"].astype(bool)
        q["off4"], q["off3"], _, q["offcov"] = KQ.offline_tags(q, owf)
        q["w"] = np.full(len(q["ht"]), xs * LUMI_PB / len(q["ht"]))
        parts.append(q)
        print(bn, len(q["ht"]), flush=True)
    q = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
    np.savez(CACHE, **q)
    return q


def read_private(pdir):
    files = sorted(glob.glob(f"{pdir}/perfNano_QCD4b_*.root"))
    q = SC.read(",".join(files))
    SC.kinematics(q)
    q["flav"] = SCK.gen_flavour(files, q)
    q["menu"] = D.events(",".join(files))["menu"].astype(bool)
    # per-job normalisation from logs/genfilter_QCD4b.txt; per-event weights from genw_*.txt
    jobs = {}
    for line in open("/work/submit/novaka/l1pixels/privgen/logs/genfilter_QCD4b.txt"):
        f = dict(x.split("=") for x in line.split()[2:] if "=" in x)  # QCD4b idx ngen= xs=val err xs_after=val err npass=
        if "xs_after" not in f or not f["xs_after"]:
            continue
        t = line.split()
        xs_b, xs_a = float(f["xs"]), float(f["xs_after"])
        jobs[int(t[1])] = (int(f["ngen"]), xs_b, xs_a)
    gw = {}
    sum_all = 0.0
    used = set()
    for fn in files:
        idx = int(os.path.basename(fn)[:-5].split("_")[-1])
        if idx not in jobs:
            continue
        rows = np.loadtxt(fn.replace("perfNano_", "genw_").replace(".root", ".txt"), ndmin=2)
        n, xs_b, xs_a = jobs[idx]
        sum_all += rows[:, 2].sum() * xs_b / xs_a
        used.add(idx)
        for r in rows:
            gw[(int(r[0]), int(r[1]))] = (r[2], r[3])
    # jobs with no passing event still count their generated weight: sum w(all) = N x <w>, with <w> from the others
    n_used = sum(jobs[i][0] for i in used)
    n_all = sum(v[0] for v in jobs.values())
    sum_all *= n_all / max(n_used, 1)
    xs = np.mean([v[1] for v in jobs.values()])
    w = np.array([gw.get((int(l), int(e)), (0.0, -1))[0] for l, e in zip(q["lumi"], q["event"])])
    q["pthat"] = np.array([gw.get((int(l), int(e)), (0.0, -1))[1] for l, e in zip(q["lumi"], q["event"])])
    q["w"] = xs * LUMI_PB * w / sum_all
    info = {"files": len(files), "events": int(len(q["ht"])), "jobs": len(jobs), "generated": n_all, "xsec_before_pb": float(xs),
            "sum_w_all": float(sum_all), "events_with_weight": int((w > 0).sum())}
    return q, info


def main():
    out, hh_pat, fh, sp_path, gen_glob, kl_glob, sc_json, norm_json, qdir, owdir, pdir = sys.argv[1:12]
    sj = json.load(open(sc_json))
    c1, r1, c2, r2 = sj["setup"]["window"]
    win = lambda d: d["n4"] & (d["ht"] > SC.HT_CUT) & (np.hypot((d["m1"] - c1) / r1, (d["m2"] - c2) / r2) < 1.6)
    qf = np.concatenate([np.load(f)["upart"][(np.load(f)["pt"] > 30) & (np.load(f)["flav"] == 0)]
                         for f in sorted(glob.glob("/scratch/submit/cms/novaka/l1pixels/offline/QCDFlat_*.npz"))])
    KQ.UPART_M = float(np.quantile(qf, 0.99))

    # signal (as scout_check.py)
    import re
    hh = SC.read(hh_pat)
    SC.attach(hh, load(fh), np.zeros(len(load(fh)["pt"])))
    SC.kinematics(hh)
    sp = np.load(sp_path)
    pos = {(l, e): i for i, (l, e) in enumerate(zip(sp["hh_lumi"], sp["hh_event"]))}
    hh["menu"] = sp["hh_menu"][np.array([pos[(l, e)] for l, e in zip(hh["lumi"], hh["event"])])].astype(bool)
    g = {k: np.concatenate([np.load(f)[k] for f in sorted(glob.glob(gen_glob))]) for k in ("lumi", "event", "mhh")}
    gpos = {(l, e): i for i, (l, e) in enumerate(zip(g["lumi"], g["event"]))}
    mhh = np.array([g["mhh"][gpos[(l, e)]] for l, e in zip(hh["lumi"], hh["event"])])
    nano = {}
    for f in sorted(glob.glob(kl_glob)):
        m = np.load(f)["mhh"]
        nano[float(re.search(r"kl(\d+p\d+)", f).group(1).replace("p", "."))] = m[m > 0]
    gb = np.concatenate([np.arange(240, 600, 20), np.arange(600, 800, 50), [800, 1000, 1300, 5000]])
    dens = {kl: np.histogram(m, gb)[0] / len(m) for kl, m in nano.items()}
    ib = np.clip(np.digitize(mhh, gb) - 1, 0, len(gb) - 2)
    odd = hh["event"] % 2 == 1
    w_sm = odd * SC.SIG_SM / odd.sum()
    w_kl = {kl: w_sm * SC.XS(kl) * np.where(dens[1.0] > 0, dens[kl] / np.maximum(dens[1.0], 1e-12), 0.0)[ib] for kl in nano}
    hw = win(hh)
    p_hh = np.select([hh["flav"] == 5, hh["flav"] == 4], [SC.OFFLINE_P[5], SC.OFFLINE_P[4]], SC.OFFLINE_P[0])
    h4, h3 = SC.tag_probs(p_hh)

    # backgrounds
    q = read_qcdpt(qdir, owdir)
    nc = json.load(open(norm_json))
    edges = np.array(nc["ht_edges"])
    tot = np.sum([nc["qcd"][b]["window"] for b in nc["qcd"]], axis=0)
    corr = np.where((edges[:-1] < 300) & (tot > 0), np.array(nc["mb"]["window"]) / np.maximum(tot, 1e-300), 1.0)
    q["w"] = q["w"] * corr[np.clip(np.digitize(q["ht"], edges) - 1, 0, len(corr) - 1)]
    q4 = (q["flav"] == 5).sum(1) == 4
    pv, pinfo = read_private(pdir)
    pv = {k: v[pv["w"] > 0] for k, v in pv.items()}
    p4 = (pv["flav"] == 5).sum(1) == 4
    res = {"setup": {"window": [c1, r1, c2, r2], "ht_correction_below_300": corr.tolist(), "private": pinfo}}
    qw, pw = win(q), win(pv)
    res["genuine_4b_in_window"] = {"private_yield": float((pv["w"] * pw * p4).sum()), "private_raw": int((pw & p4).sum()),
                                   "private_neff": float((pv["w"] * pw * p4).sum() ** 2 / max((pv["w"] ** 2 * pw * p4).sum(), 1e-300)),
                                   "qcdpt_yield": float((q["w"] * qw * q4).sum()), "qcdpt_raw": int((qw & q4).sum()),
                                   "window_yield_all": float((q["w"] * qw).sum()),
                                   "private_pthat_quantiles": np.quantile(pv["pthat"][pw & p4], [0.1, 0.5, 0.9]).tolist() if (pw & p4).any() else []}
    print("genuine 4b in the window:", json.dumps(res["genuine_4b_in_window"]), flush=True)
    # combined background sample: pT-binned QCD without its genuine-4b events + the private 4b events
    keys = ("ht", "n4", "m1", "m2", "m4j", "nn", "flav", "menu", "w")
    keep = ~q4
    B = {k: np.concatenate([q[k][keep], pv[k][p4]]) for k in keys}
    bw = win(B)

    lj = (q["n4"] & (q["ht"] > SC.HT_CUT))[:, None] & (q["flav"] == 0)
    o = np.argsort(q["nn"][lj])
    cw = np.cumsum(np.broadcast_to(q["w"][:, None], q["nn"].shape)[lj][o])
    wps = {mis: float(q["nn"][lj][o][np.searchsorted(cw, (1 - mis) * cw[-1])]) for mis in (0.002, 0.01, 0.05)}
    res["nn_wp"] = wps

    mh, mq = hh["menu"], q["menu"]
    trig_coef = SC.templates(w_kl, [hw * mh * h4, hw * mh * h3], hh["m4j"])
    trig_b = SCK.bkg(q, [(qw & mq & q["offcov"], q["off4"]), (qw & mq & q["offcov"], q["off3"])], "factorised")
    res["fits"] = {"trig_menu": SCK.fit(trig_coef, *trig_b)}
    print(f"triggered menu: Z {res['fits']['trig_menu']['Z_SM']:.2f}", flush=True)
    tags = {"perfect": (hh["flav"] == 5, B["flav"] == 5)}
    for mis, thr in wps.items():
        tags[f"nn_{mis}"] = (hh["nn"] > thr, B["nn"] > thr)
    for name, (th, tb) in tags.items():
        nh, nb = th.sum(1), tb.sum(1)
        for scope, sh, sb in (("all crossings", np.ones(len(mh), bool), np.ones(len(B["ht"]), bool)), ("menu-rejected", ~mh, ~B["menu"])):
            coef = SC.templates(w_kl, [hw * sh * (nh == 4), hw * sh * (nh == 3)], hh["m4j"])
            b = SCK.bkg(B, [(bw & sb, (nb == 4).astype(float)), (bw & sb, (nb == 3).astype(float))], os.environ.get("BKG_MODE", "direct"))
            r = SCK.fit(coef, *b)
            r["B4"] = float((B["w"] * bw * sb * (nb == 4)).sum())
            r["B4_raw"] = int((bw & sb & (nb == 4)).sum())
            if scope == "menu-rejected":
                r["combined_with_trig_menu"] = SCK.fit(np.concatenate([trig_coef, coef], 1), *(np.concatenate([x, y]) for x, y in zip(trig_b, b)))
            res["fits"][f"scout_{name} | {scope}"] = r
            print(f"scout_{name:9s} | {scope:13s} S {r['S']:8.1f} B {r['B']:10.3g} (4-tag {r['B4']:.3g} from {r['B4_raw']} events, "
                  f"n_eff {r['n_eff']:.1f})  Z {r['Z_SM']:.2f}" + (f"   menu + this {r['combined_with_trig_menu']['Z_SM']:.2f}" if scope == "menu-rejected" else ""), flush=True)
    json.dump(res, open(out, "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()

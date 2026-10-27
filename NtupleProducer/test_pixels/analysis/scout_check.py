#!/usr/bin/env python3
"""Check of the 40 MHz L1 scouting result with a background that has flavour: weighted pT-binned QCD instead of
minimum bias x one QCDFlat tag fraction (whose 4-tag fraction for perfect tags is 0 and was replaced by a one-event
floor in scouting.background()).

    python3 scout_check.py OUT.json HH4B_GLOB L1EXT_HH_LISTS SEED_PLANE.npz GENMHH_GLOB KL_GLOB SCOUTING.json QCDPT_DIR OFFLINE_W_DIR
Same HH selection, Higgs window (from SCOUTING.json), m_4j binning, signal templates and likelihood as scouting.py.
Per QCD event (sigma_bin x 3000/fb / N_bin): flavour of the 4 leading L1 jets from the closest generator jet within
0.3 (pileup jets have no generator record: light), as the per-jet lists.
Scouting tags: perfect (true b), and the L1 NN at working points set on weighted QCD light jets (0.2%, 1%, 5%).
Background models per tag category: "direct" = weighted QCD events passing the tag requirement per m_4j bin;
"factorised" = the category's untagged QCD m_4j shape x its weighted tag fraction (smoother; assumes the tag rate does
not depend on m_4j). Also the triggered menu stream (offline truth-tag probabilities, factorised) and menu + scouting
of the events the menu rejects. Lower bound on the background: no pT-hat < 30 and no b jets from pileup collisions.
"""
import glob
import json
import os
import re
import sys

import numpy as np
import uproot

os.environ.setdefault("HT_MIN", "150")
os.environ.setdefault("MB_TOTAL", "1999360")
import direct_rate as D  # noqa: E402
import kl_qcdbkg as KQ  # noqa: E402
import scouting as SC  # noqa: E402
from train_sets import load  # noqa: E402

LUMI_PB = 3.0e6
DR_GEN = 0.3


def gen_flavour(files, ev):
    """Hadron flavour of each of the 4 leading L1 jets (closest generator jet within DR_GEN, else light)."""
    g = [uproot.open(f)["Events"].arrays(["GenJets_eta", "GenJets_phi", "GenJets_hadronFlavour"], library="ak") for f in files]
    import awkward as ak
    g = ak.concatenate(g)
    fl = np.zeros((len(ev["ht"]), 4), int)
    for i in range(len(ev["ht"])):
        ge, gp, gf = np.asarray(g.GenJets_eta[i]), np.asarray(g.GenJets_phi[i]), np.asarray(g.GenJets_hadronFlavour[i])
        if not len(ge):
            continue
        for j in range(4):
            if ev["jidx"][i, j] < 0:
                continue
            dr = np.hypot(ge - ev["eta"][i, j], (gp - ev["phi"][i, j] + np.pi) % (2 * np.pi) - np.pi)
            k = np.argmin(dr)
            fl[i, j] = gf[k] if dr[k] < DR_GEN else 0
    return np.where(np.isin(fl, [4, 5]), fl, 0)


def fit(coef, b, b2, n):
    coef, b, b2 = SC.merge(coef, b, b2, n)
    s1 = coef[0] + coef[1] + coef[2]
    z = float(np.sqrt(2 * np.sum(np.where(b > 0, (s1 + b) * np.log1p(s1 / np.maximum(b, 1e-300)) - s1, 0))))
    q = SC.scan(coef, b)
    q5 = SC.scan(coef, b, truth=5.0)
    return {"Z_SM": z, "kl_68": SC.interval(q, 1.0)[0], "Z_excl_SM_if_kl5": float(np.sqrt(max(np.interp(1.0, SC.KL_SCAN, q5), 0))),
            "S": float(s1.sum()), "B": float(b.sum()), "n_eff": float(b.sum() ** 2 / max(b2.sum(), 1e-300)),
            "zero_bkg_bins": int((b <= 0).sum()), "bins": int(len(b))}


def bkg(q, masks_probs, mode):
    """masks_probs: list of (event mask, per-event tag weight in [0,1]) -> b, b2, n concatenated per category."""
    b, b2, n = [], [], []
    for m, p in masks_probs:
        if mode == "direct":
            w = q["w"] * m * p
            b.append(np.histogram(q["m4j"], SC.M4J_BINS, weights=w)[0])
            b2.append(np.histogram(q["m4j"], SC.M4J_BINS, weights=w ** 2)[0])
            n.append(np.histogram(q["m4j"], SC.M4J_BINS, weights=(m & (p > 0)).astype(float))[0])
        else:
            f = (q["w"] * m * p).sum() / max((q["w"] * m).sum(), 1e-300)
            b.append(np.histogram(q["m4j"], SC.M4J_BINS, weights=q["w"] * m)[0] * f)
            b2.append(np.histogram(q["m4j"], SC.M4J_BINS, weights=(q["w"] * m) ** 2)[0] * f ** 2)
            n.append(np.histogram(q["m4j"], SC.M4J_BINS, weights=m.astype(float))[0])
    return np.concatenate(b), np.concatenate(b2), np.concatenate(n)


def main():
    out, hh_pat, fh, sp_path, gen_glob, kl_glob, sc_json, qdir, owdir = sys.argv[1:10]
    sj = json.load(open(sc_json))
    c1, r1, c2, r2 = sj["setup"]["window"]
    win = lambda d: d["n4"] & (d["ht"] > SC.HT_CUT) & (np.hypot((d["m1"] - c1) / r1, (d["m2"] - c2) / r2) < 1.6)
    # working point of the offline tag (as kl_qcdbkg)
    qf = np.concatenate([np.load(f)["upart"][(np.load(f)["pt"] > 30) & (np.load(f)["flav"] == 0)]
                         for f in sorted(glob.glob("/scratch/submit/cms/novaka/l1pixels/offline/QCDFlat_*.npz"))])
    KQ.UPART_M = float(np.quantile(qf, 0.99))

    hh = SC.read(hh_pat)
    lh = load(fh)
    SC.attach(hh, lh, np.zeros(len(lh["pt"])))
    SC.kinematics(hh)
    sp = np.load(sp_path)
    pos = {(l, e): i for i, (l, e) in enumerate(zip(sp["hh_lumi"], sp["hh_event"]))}
    hh["menu"] = sp["hh_menu"][np.array([pos[(l, e)] for l, e in zip(hh["lumi"], hh["event"])])].astype(bool)
    # signal templates (as scouting.py)
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

    # QCD
    parts = []
    res = {"setup": {"window": [c1, r1, c2, r2], "bins": {}}}
    for bn in sorted({os.path.basename(f).split("_")[1] for f in glob.glob(f"{qdir}/perfNano_QCDPt*_*.root")}, key=lambda s: int(s[5:])):
        files = sorted(glob.glob(f"{qdir}/perfNano_{bn}_*.root"))
        owf = sorted(glob.glob(f"{owdir}/{bn}_*.npz"))
        xs = np.mean([float(np.load(f)["xsec"][0]) for f in owf if float(np.load(f)["xsec"][0]) > 0])
        q = SC.read(",".join(files))
        SC.kinematics(q)
        q["flav"] = gen_flavour(files, q)
        q["menu"] = D.events(",".join(files))["menu"].astype(bool)
        q["off4"], q["off3"], _, q["offcov"] = KQ.offline_tags(q, owf)
        q["w"] = np.full(len(q["ht"]), xs * LUMI_PB / len(q["ht"]))
        nw = win(q)
        res["setup"]["bins"][bn] = {"events": int(len(q["ht"])), "xsec_pb": float(xs), "window_events": int(nw.sum()),
                                    "window_4b": int((nw & ((q["flav"] == 5).sum(1) == 4)).sum()),
                                    "window_3b": int((nw & ((q["flav"] == 5).sum(1) == 3)).sum())}
        print(bn, res["setup"]["bins"][bn], flush=True)
        parts.append(q)
    q = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
    qw = win(q)
    nb = (q["flav"] == 5).sum(1)
    w_mb = SC.N_BX / SC.MB_TOTAL
    res["normalisation"] = {"mb_window_yield": sj["setup"]["mb_base_events"] * w_mb, "qcd_window_yield": float((q["w"] * qw).sum()),
                            "qcd_window_4b": float((q["w"] * qw * (nb == 4)).sum()), "qcd_window_3b": float((q["w"] * qw * (nb == 3)).sum()),
                            "qcd_4b_fraction": float((q["w"] * qw * (nb == 4)).sum() / (q["w"] * qw).sum()),
                            "qcd_3b_fraction": float((q["w"] * qw * (nb == 3)).sum() / (q["w"] * qw).sum()),
                            "scouting_used_fractions_perfect": sj["setup"]["qcd_tagfrac_by_stream"]["scout_perfect"][:2],
                            "scouting_B_perfect": sj["scout_perfect"]["B"]}
    print("normalisation:", json.dumps(res["normalisation"]), flush=True)

    # NN working points on weighted QCD light jets in the base selection
    base = q["n4"] & (q["ht"] > SC.HT_CUT)
    lj = base[:, None] & (q["flav"] == 0)
    order = np.argsort(q["nn"][lj])
    cw = np.cumsum(np.broadcast_to(q["w"][:, None], q["nn"].shape)[lj][order])
    wps = {mis: float(q["nn"][lj][order][np.searchsorted(cw, (1 - mis) * cw[-1])]) for mis in (0.002, 0.01, 0.05)}
    res["nn_wp"] = wps

    res["fits"] = {}
    # triggered menu (offline truth-tag probabilities, factorised per category)
    mh, mq = hh["menu"], q["menu"]
    trig_coef = SC.templates(w_kl, [hw * mh * h4, hw * mh * h3], hh["m4j"])
    trig_b = bkg(q, [(qw & mq & q["offcov"], q["off4"]), (qw & mq & q["offcov"], q["off3"])], "factorised")
    res["fits"]["trig_menu"] = fit(trig_coef, *trig_b)
    tags = {"perfect": (hh["flav"] == 5, q["flav"] == 5)}
    for mis, thr in wps.items():
        tags[f"nn_{mis}"] = (hh["nn"] > thr, q["nn"] > thr)
    for name, (th, tq) in tags.items():
        nh, nq = th.sum(1), tq.sum(1)
        for scope, sh, sq in (("all crossings", np.ones(len(mh), bool), np.ones(len(mq), bool)), ("menu-rejected", ~mh, ~mq)):
            coef = SC.templates(w_kl, [hw * sh * (nh == 4), hw * sh * (nh == 3)], hh["m4j"])
            for mode in ("direct", "factorised"):
                b = bkg(q, [(qw & sq, (nq == 4).astype(float)), (qw & sq, (nq == 3).astype(float))], mode)
                r = fit(coef, *b)
                key = f"scout_{name} | {scope} | {mode}"
                if scope == "menu-rejected":  # disjoint from the triggered stream: add the likelihoods
                    rc = fit(np.concatenate([trig_coef, coef], 1), *(np.concatenate([x, y]) for x, y in zip(trig_b, b)))
                    r["combined_with_trig_menu"] = rc
                res["fits"][key] = r
                print(f"{key:48s} S {r['S']:8.1f} B {r['B']:10.3g} (n_eff {r['n_eff']:7.1f}, zero-B bins {r['zero_bkg_bins']})  Z {r['Z_SM']:.2f}"
                      + (f"   menu + this: Z {r['combined_with_trig_menu']['Z_SM']:.2f} (menu alone {res['fits']['trig_menu']['Z_SM']:.2f})"
                         if scope == "menu-rejected" else ""), flush=True)
    json.dump(res, open(out, "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()

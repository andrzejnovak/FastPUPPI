#!/usr/bin/env python3
"""Is 40 MHz HH->4b scouting limited by L1-jet resolution? Perfect b tags with offline-quality or generator-level jets.

    python3 scout_kin.py OUT.json SEED_PLANE.npz GENMHH_GLOB KL_GLOB NORM_CHECK.json HH_OFFLINE_GLOB HH_NTUPLE_GLOB \
        QCDPT_DIR OFFLINE_W_DIR PRIV_DIR
Same event logic as scouting.py / scout4b.py with other jets:
  offline: AK4 PUPPI jets (pT > 20, |eta| < 2.5, loose ID, b-jet response correction as offline_lowmass.py) and their
           hadron flavour as perfect tags. Background: the pT-binned QCD offline dumps (all events, cross-section
           weights); pileup jets included as reconstructed. No private 4b sample (it has no offline reconstruction).
  gen:     generator jets (pT > 20, |eta| < 2.4): perfect resolution and no pileup jets (an absolute ceiling).
           Background: pT-binned QCD ntuples without their genuine-4b events + the private QCD4b sample.
Base: >= 4 jets, HT (jets > 30) > 150; the 4 leading jets, pairing by the smallest |m1 - m2|; Higgs window from true-4b
signal in the same variant (median +- 1.4826 MAD, radius 1.6); m_4j binning and likelihood as scouting.py. Categories:
4 and 3 true b among the 4 leading jets. Scopes: all crossings, and crossings the HT seeds reject, combined with the
triggered menu stream analysed with the same jets and offline tags (truth-tag b 0.84, c 0.12, light 0.01), where the
menu flag exists (ntuple events). Below HT 300 the QCD yields
are scaled by minimum bias / QCD (norm_check.json, binned in L1 HT; for offline jets in offline HT, an approximation).
"""
import glob
import json
import os
import re
import sys

import awkward as ak
import numpy as np
import uproot

os.environ.setdefault("HT_MIN", "150")
os.environ.setdefault("MB_TOTAL", "1999360")
import direct_rate as D  # noqa: E402
import scout4b as S4  # noqa: E402
import scout_check as SCK  # noqa: E402
import scouting as SC  # noqa: E402

LUMI_PB = 3.0e6
resp = json.load(open("/work/submit/novaka/l1pixels/offline/b_response.json"))
resp_pt = np.array([np.sqrt(lo * min(hi, 400.0)) for lo, hi, _, _ in resp])
resp_val = np.array([r for _, _, r, _ in resp])


def kin(pt, eta, phi, mass, flav, bcorr):
    """Jagged jets (already selected) -> per event: ht, n4, m1, m2, m4j, number of true b among the 4 leading."""
    ht = ak.to_numpy(ak.sum(pt[pt > 30], axis=1))
    o = ak.argsort(pt, ascending=False)
    pt, eta, phi, mass, flav = pt[o], eta[o], phi[o], mass[o], flav[o]
    n4 = ak.to_numpy(ak.num(pt) >= 4)
    g = lambda x: ak.to_numpy(ak.fill_none(ak.pad_none(x[:, :4], 4, clip=True), 0.0)).astype(float)
    P, E, F, M, FL = g(pt), g(eta), g(phi), g(mass), g(flav)
    if bcorr:
        c = np.where(P > 0, 1 / np.interp(np.log(np.maximum(P, 1)), np.log(resp_pt), resp_val), 1.0)
        c = np.where(FL == 5, c, 1.0)
        P, M = P * c, M * c
    ev = {"pt": P, "eta": E, "phi": F, "mass": M}
    SC.kinematics(ev)
    p = np.select([FL == 5, FL == 4], [SC.OFFLINE_P[5], SC.OFFLINE_P[4]], SC.OFFLINE_P[0])
    p4, p3 = SC.tag_probs(p)
    return {"ht": ht, "n4": n4, "m1": ev["m1"], "m2": ev["m2"], "m4j": ev["m4j"], "nb": (FL == 5).sum(1), "p4": p4, "p3": p3}


def offline_events(files, idsel=True):
    parts = []
    for f in files:
        d = np.load(f)
        n = d["njet"]
        J = {k: ak.unflatten(d[k], n) for k in ("pt", "eta", "phi", "mass", "flav", "nconst", "nhf", "nemf")}
        m = (J["pt"] > 20) & (abs(J["eta"]) < 2.5) & (J["nconst"] > 1) & (J["nhf"] < 0.9) & (J["nemf"] < 0.9)
        k = kin(J["pt"][m], J["eta"][m], J["phi"][m], J["mass"][m], J["flav"][m], True)
        k["lumi"], k["event"] = d["lumi"], d["event"]
        parts.append(k)
    return {c: np.concatenate([p[c] for p in parts]) for c in parts[0]}


def gen_events(files):
    a = ak.concatenate([uproot.open(f)["Events"].arrays(["luminosityBlock", "event", "GenJets_pt", "GenJets_eta", "GenJets_phi",
                                                        "GenJets_mass", "GenJets_hadronFlavour"]) for f in files])
    m = (a.GenJets_pt > 20) & (abs(a.GenJets_eta) < 2.4)
    k = kin(a.GenJets_pt[m], a.GenJets_eta[m], a.GenJets_phi[m], a.GenJets_mass[m], a.GenJets_hadronFlavour[m], False)
    k["lumi"], k["event"] = ak.to_numpy(a.luminosityBlock), ak.to_numpy(a.event)
    return k


def main():
    out, sp_path, gen_glob, kl_glob, norm_json, hh_off, hh_nt, qdir, owdir, pdir = sys.argv[1:11]
    sp = np.load(sp_path)
    spos = {(int(l), int(e)): i for i, (l, e) in enumerate(zip(sp["hh_lumi"], sp["hh_event"]))}
    g = {k: np.concatenate([np.load(f)[k] for f in sorted(glob.glob(gen_glob))]) for k in ("lumi", "event", "mhh")}
    gpos = {(int(l), int(e)): i for i, (l, e) in enumerate(zip(g["lumi"], g["event"]))}
    nano = {}
    for f in sorted(glob.glob(kl_glob)):
        m = np.load(f)["mhh"]
        nano[float(re.search(r"kl(\d+p\d+)", f).group(1).replace("p", "."))] = m[m > 0]
    gb = np.concatenate([np.arange(240, 600, 20), np.arange(600, 800, 50), [800, 1000, 1300, 5000]])
    dens = {kl: np.histogram(m, gb)[0] / len(m) for kl, m in nano.items()}
    nc = json.load(open(norm_json))
    edges = np.array(nc["ht_edges"])
    tot = np.sum([nc["qcd"][b]["window"] for b in nc["qcd"]], axis=0)
    corr = np.where((edges[:-1] < 300) & (tot > 0), np.array(nc["mb"]["window"]) / np.maximum(tot, 1e-300), 1.0)
    cf = lambda ht: corr[np.clip(np.digitize(ht, edges) - 1, 0, len(corr) - 1)]
    res = {"variants": {}}

    # QCD bins: menu flags (ntuple events) and cross-sections
    bins = sorted({os.path.basename(f).split("_")[1] for f in glob.glob(f"{qdir}/perfNano_QCDPt*_*.root")}, key=lambda s: int(s[5:]))
    xs = {b: np.mean([float(np.load(f)["xsec"][0]) for f in glob.glob(f"{owdir}/{b}_*.npz") if float(np.load(f)["xsec"][0]) > 0]) for b in bins}
    menu_q, l1ht_q = {}, {}
    for b in bins:
        qe = D.events(",".join(sorted(glob.glob(f"{qdir}/perfNano_{b}_*.root"))))
        for l, e, mflag, h in zip(qe["lumi"], qe["event"], qe["menu"], qe["ht"]):
            menu_q[(b, int(l), int(e))] = bool(mflag)
            l1ht_q[(b, int(l), int(e))] = float(h)

    for variant in ("offline", "gen"):
        if variant == "offline":
            hh = offline_events(sorted(glob.glob(hh_off)))
            qs = []
            for b in bins:
                q = offline_events(sorted(glob.glob(f"{owdir}/{b}_*.npz")))
                q["w"] = np.full(len(q["ht"]), xs[b] * LUMI_PB / len(q["ht"])) * cf(q["ht"])
                keys = [(b, int(l), int(e)) for l, e in zip(q["lumi"], q["event"])]
                q["has_menu"] = np.array([k in menu_q for k in keys])
                q["menu"] = np.array([menu_q.get(k, False) for k in keys])
                q["w_menu"] = np.where(q["has_menu"], xs[b] * LUMI_PB / max(q["has_menu"].sum(), 1), 0.0) * cf(q["ht"])
                qs.append(q)
            Q = {c: np.concatenate([q[c] for q in qs]) for c in qs[0]}
        else:
            hh = gen_events(sorted(glob.glob(hh_nt)))
            qs = []
            for b in bins:
                files = sorted(glob.glob(f"{qdir}/perfNano_{b}_*.root"))
                q = gen_events(files)
                keys = [(b, int(l), int(e)) for l, e in zip(q["lumi"], q["event"])]
                l1h = np.array([l1ht_q[k] for k in keys])
                q["w"] = np.full(len(q["ht"]), xs[b] * LUMI_PB / len(q["ht"])) * cf(l1h)
                q["menu"] = np.array([menu_q[k] for k in keys])
                q["has_menu"] = np.ones(len(q["ht"]), bool)
                q["w_menu"] = q["w"]
                keep = ~(q["n4"] & (q["nb"] == 4))  # genuine 4b from the private sample instead
                qs.append({c: v[keep] for c, v in q.items()})
            pv, pinfo = S4.read_private(pdir)
            pfiles = sorted(glob.glob(f"{pdir}/perfNano_QCD4b_*.root"))
            pg = gen_events(pfiles)
            assert (pg["event"] == pv["event"]).all()
            sel = (pv["w"] > 0) & pg["n4"] & (pg["nb"] == 4)
            pg = {c: v[sel] for c, v in pg.items()}
            pg["w"] = pv["w"][sel]
            pg["menu"] = pv["menu"][sel]
            pg["has_menu"] = np.ones(sel.sum(), bool)
            pg["w_menu"] = pg["w"]
            qs.append(pg)
            Q = {c: np.concatenate([q[c] for q in qs]) for c in ("ht", "n4", "m1", "m2", "m4j", "nb", "p4", "p3", "w", "menu", "has_menu", "w_menu")}

        # signal: odd HH events with generator m_HH (and the menu flag where it exists)
        keys = [(int(l), int(e)) for l, e in zip(hh["lumi"], hh["event"])]
        has = np.array([k in gpos for k in keys])
        mhh = np.array([g["mhh"][gpos[k]] if k in gpos else -1.0 for k in keys])
        hmenu_has = np.array([k in spos for k in keys])
        hmenu = np.array([bool(sp["hh_menu"][spos[k]]) if k in spos else False for k in keys])
        odd = (hh["event"] % 2 == 1) & has
        ib = np.clip(np.digitize(mhh, gb) - 1, 0, len(gb) - 2)
        w_sm = odd * SC.SIG_SM / odd.sum()
        w_kl = {kl: w_sm * SC.XS(kl) * np.where(dens[1.0] > 0, dens[kl] / np.maximum(dens[1.0], 1e-12), 0.0)[ib] for kl in nano}
        # menu-split signal uses only events with the flag, rescaled to the same total
        msc = odd.sum() / max((odd & hmenu_has).sum(), 1)
        w_kl_m = {kl: v * hmenu_has * msc for kl, v in w_kl.items()}

        base = lambda d: d["n4"] & (d["ht"] > SC.HT_CUT)
        t4 = base(hh) & (hh["nb"] == 4)
        c1, c2 = np.median(hh["m1"][t4]), np.median(hh["m2"][t4])
        r1, r2 = 1.4826 * np.median(abs(hh["m1"][t4] - c1)), 1.4826 * np.median(abs(hh["m2"][t4] - c2))
        win = lambda d: base(d) & (np.hypot((d["m1"] - c1) / r1, (d["m2"] - c2) / r2) < 1.6)
        hw, qw = win(hh), win(Q)
        v = res["variants"][variant] = {"window": [float(c1), float(r1), float(c2), float(r2)],
                                         "signal_true4b_in_window": float((w_sm * hw * (hh["nb"] == 4)).sum()),
                                         "bkg_window_yield": float((Q["w"] * qw).sum()),
                                         "bkg_4b": float((Q["w"] * qw * (Q["nb"] == 4)).sum()), "bkg_4b_raw": int((qw & (Q["nb"] == 4)).sum()),
                                         "bkg_3b": float((Q["w"] * qw * (Q["nb"] == 3)).sum()), "bkg_3b_raw": int((qw & (Q["nb"] == 3)).sum())}
        print(f"[{variant}] window ({c1:.0f} +- {r1:.0f}, {c2:.0f} +- {r2:.0f}); signal true-4b in window {v['signal_true4b_in_window']:.0f}; "
              f"bkg window {v['bkg_window_yield']:.3g}, 4b {v['bkg_4b']:.3g} ({v['bkg_4b_raw']} events), 3b {v['bkg_3b']:.3g} ({v['bkg_3b_raw']})", flush=True)
        nh, nq = hh["nb"], Q["nb"]
        QM = dict(Q, w=Q["w_menu"])
        # triggered stream: menu-accepted events, offline tags (truth-tag probabilities), these kinematics
        trig_coef = SC.templates(w_kl_m, [hw * hmenu * hmenu_has * hh["p4"], hw * hmenu * hmenu_has * hh["p3"]], hh["m4j"])
        trig_b = SCK.bkg(QM, [(qw & Q["menu"] & Q["has_menu"], Q["p4"]), (qw & Q["menu"] & Q["has_menu"], Q["p3"])], "factorised")
        v["trig_menu"] = SCK.fit(trig_coef, *trig_b)
        print(f"   triggered menu (offline tags) Z {v['trig_menu']['Z_SM']:.2f}", flush=True)
        for scope in ("all crossings", "menu-rejected"):
            if scope == "all crossings":
                sh, wk, sq, QQ = np.ones(len(nh), bool), w_kl, np.ones(len(nq), bool), Q
            else:
                sh, wk, sq, QQ = ~hmenu & hmenu_has, w_kl_m, ~Q["menu"] & Q["has_menu"], QM
            coef = SC.templates(wk, [hw * sh * (nh == 4), hw * sh * (nh == 3)], hh["m4j"])
            b = SCK.bkg(QQ, [(qw & sq, (nq == 4).astype(float)), (qw & sq, (nq == 3).astype(float))], "direct")
            r = SCK.fit(coef, *b)
            r["B4"] = float((QQ["w"] * qw * sq * (nq == 4)).sum())
            r["B4_raw"] = int((qw & sq & (nq == 4)).sum())
            r["B3_raw"] = int((qw & sq & (nq == 3)).sum())
            if scope == "menu-rejected":  # disjoint from the triggered stream: one likelihood
                r["menu_plus_this"] = SCK.fit(np.concatenate([trig_coef, coef], 1), *(np.concatenate([x, y]) for x, y in zip(trig_b, b)))["Z_SM"]
            v[scope] = r
            print(f"   {scope:14s} S {r['S']:8.1f} B {r['B']:10.3g} (4-tag {r['B4']:.3g} from {r['B4_raw']}, 3-tag from {r['B3_raw']} events, "
                  f"n_eff {r['n_eff']:.1f}, zero-B bins {r['zero_bkg_bins']})  Z {r['Z_SM']:.2f}"
                  + (f"   menu {v['trig_menu']['Z_SM']:.2f} + this -> {r['menu_plus_this']:.2f}" if scope == "menu-rejected" else ""), flush=True)
    json.dump(res, open(out, "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()

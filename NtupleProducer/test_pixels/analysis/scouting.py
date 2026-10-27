#!/usr/bin/env python3
"""HH->4b at L1-object level with a minimum-bias background model: triggered stream, 40 MHz scouting stream, and
a kappa_lambda interval from the reconstructed m_4j shape.

    python3 scouting.py OUT.json HH4B_GLOB MB_GLOBS L1EXT_LISTS(hh:qcd:mb1:mb2) SEED_PLANE.npz GENMHH_GLOB KL_GLOB

Events: L1 NG jets with |eta| < 2.4, pT > 20; the 4 leading ones form two Higgs candidates (pairing with the smallest
|m1 - m2|), m_4j is the m_HH proxy. All streams require L1 HT > 150 GeV, where the re-simulated minimum bias is
complete (and where the pixel region-of-interest request would fire).
Background: the minimum bias itself (QCD multijet in its natural proportion; ttbar etc. not resolved with 2M
crossings). Each event stands for N_BX(3000/fb) / MB_TOTAL crossings, so tagged categories use per-jet tag
probabilities (flavour x pT maps, "truth tagging") instead of cuts; closure is checked against direct cuts. The
m_4j shape comes from all minimum-bias events in the Higgs window (see background()).
Streams:
  trig_<seed>   (BKG_MODEL=score, default: the seed-added events' 4b/3b fractions from QCD events binned in the same
                seed score; BKG_MODEL=strata: from the few QCD events the seed adds)
                L1 accept (menu, menu + 2.5 kHz NN / pixel / perfect seed, thresholds from seed_plane sums as in
                direct_rate.py, chosen on even events), then offline-like tags (UParT-like probabilities b 0.84,
                c 0.12, light 0.01 per jet, flavour from the lists) on the L1 jets. Background 4b / 3b fractions
                from QCD events passing the same L1 acceptance (offline jets truth-tagged, see offline_tagprob;
                a b-tagged seed accepts b-rich events), shape and normalisation from the accepted minimum bias.
                Scouting: the minimum-bias L1 tag maps applied to the QCD flavour content.
  scout_<tag>   no L1 accept: L1 tag scores (NN, L1 pixel, perfect); signal uses direct score cuts, background truth
                tagging. Working point = light-jet mistag on minimum-bias jets, best of a small scan.
  comb_<seed>   triggered stream for accepted events plus scouting (same tagger family) for the rest: disjoint,
                their likelihoods add.
Signal: odd HH events only (taggers and seed thresholds trained on even ones), SM ggF 36.69 fb x BR(4b) 0.339,
3000/fb; kappa_lambda templates from generator m_HH shapes (kl = 0, 1, 2.45, 5) and sigma(kl) (LHCHWG parabola),
a quadratic per bin. Interval: Asimov Poisson likelihood, statistical only.
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
from seed_plane import tagger  # noqa: E402

MB_TOTAL = int(os.environ["MB_TOTAL"])
LUMI = 3000.0  # fb^-1
N_BX = LUMI / (7.5e34 / (2760 * 11245) * 1e-39)  # crossings in 3000/fb at 7.5e34 (PU ~200)
SIG_SM = 36.69 * 0.5824 ** 2 * LUMI
XS = lambda k: (70.3874 - 50.4111 * k + 11.0595 * k ** 2) / 31.0358  # sigma(kl) / sigma(1), ggF
HT_CUT, JET_PT = 150.0, 20.0
SEED_KHZ = float(os.environ.get("SEED_KHZ", "2.5"))
N_CAT = int(os.environ.get("N_CAT", "0"))  # seed-score categories for the seed-added events (0: ~10 MB events each, 1-8)  # added rate of the tagged seeds on top of the HT seeds
OFFLINE_P = {5: 0.84, 4: 0.12, 0: 0.01}
MISTAGS = (0.002, 0.005, 0.01, 0.02, 0.05)
PT_BINS = np.array([20, 30, 40, 50, 65, 80, 100, 130, 170, 250, 1e9])
M4J_BINS = np.array([0, 250, 300, 350, 400, 450, 500, 575, 650, 800, 1000, 1e9])
KL_SCAN = np.linspace(-6, 14, 801)
N_MIN = 10
TRUTHS = (1.0, 2.45, 5.0)  # Asimov truths: SM first
LOW_M4J = 400.0
BR = ["luminosityBlock", "event", "L1NGJets_pt", "L1NGJets_eta", "L1NGJets_phi", "L1NGJets_mass",
      "L1NGJets_score_b", "L1NGJets_score_uds", "L1NGJets_score_g"]


def read(pat):
    files = [f for p in pat.split(",") for f in sorted(glob.glob(p))]
    a = ak.concatenate([uproot.open(f)["Events"].arrays(filter_name=BR) for f in files])
    pt, eta = a.L1NGJets_pt, a.L1NGJets_eta
    acc = abs(eta) < 2.4
    ht = ak.to_numpy(ak.sum(pt[acc & (pt > 30)], axis=1))
    idx = ak.local_index(pt)
    sel = acc & (pt > JET_PT)
    order = ak.argsort(pt[sel], ascending=False)
    n4 = ak.to_numpy(ak.num(idx[sel]) >= 4)
    get = lambda x, fill=0.0: ak.to_numpy(ak.fill_none(ak.pad_none(x[sel][order][:, :4], 4, clip=True), fill)).astype(np.float64)
    nn = a.L1NGJets_score_b / np.maximum(a.L1NGJets_score_b + a.L1NGJets_score_uds + a.L1NGJets_score_g, 1e-6)
    return {"lumi": ak.to_numpy(a.luminosityBlock), "event": ak.to_numpy(a.event), "ht": ht, "n4": n4,
            "jidx": get(idx, -1).astype(np.int64), "pt": get(pt), "eta": get(eta), "phi": get(a.L1NGJets_phi),
            "mass": get(a.L1NGJets_mass), "nn": get(nn)}


def attach(ev, lists, score):
    """Per leading jet: pixel score and generator flavour from the per-jet lists (missing jets: score 0, light)."""
    key = {(l, e, j): i for i, (l, e, j) in enumerate(zip(lists["lumi"], lists["event"], lists["jidx"]))}
    n = len(ev["ht"])
    pos = np.array([[key.get((l, e, j), -1) for j in js] for l, e, js in zip(ev["lumi"], ev["event"], ev["jidx"])],
                   dtype=np.int64).reshape(n, 4)
    ok = pos >= 0
    ev["l1"] = np.where(ok, score[np.maximum(pos, 0)], 0.0)
    fl = np.where(ok, lists["flav"][np.maximum(pos, 0)], 0)
    ev["flav"] = np.where(fl == 5, 5, np.where(fl == 4, 4, 0))
    ev["perfect"] = (ev["flav"] == 5).astype(float)
    print(f"  {ok[ev['n4']].mean():.3f} of leading jets found in the lists", flush=True)


def kinematics(ev):
    px, py = ev["pt"] * np.cos(ev["phi"]), ev["pt"] * np.sin(ev["phi"])
    pz = ev["pt"] * np.sinh(ev["eta"])
    e = np.sqrt(px ** 2 + py ** 2 + pz ** 2 + ev["mass"] ** 2)
    p4 = np.stack([e, px, py, pz], -1)
    m = lambda v: np.sqrt(np.maximum(v[..., 0] ** 2 - (v[..., 1:] ** 2).sum(-1), 0))
    best, m1, m2 = np.full(len(e), np.inf), np.zeros(len(e)), np.zeros(len(e))
    for (a, b), (c, d) in (((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))):
        ma, mb_ = m(p4[:, a] + p4[:, b]), m(p4[:, c] + p4[:, d])
        pa, pb = np.hypot(*(p4[:, a] + p4[:, b])[:, 1:3].T), np.hypot(*(p4[:, c] + p4[:, d])[:, 1:3].T)
        hi, lo = np.where(pa >= pb, ma, mb_), np.where(pa >= pb, mb_, ma)
        better = abs(ma - mb_) < best
        best, m1, m2 = np.where(better, abs(ma - mb_), best), np.where(better, hi, m1), np.where(better, lo, m2)
    ev["m1"], ev["m2"], ev["m4j"] = m1, m2, m(p4.sum(1))


def tag_probs(p):
    """p: (n, 4) per-jet tag probabilities -> P(4 tags), P(exactly 3 tags)."""
    p4 = p.prod(1)
    p3 = sum(np.prod(np.where(np.arange(4)[None, :] == k, 1 - p, p), 1) for k in range(4))
    return p4, p3


def offline_tagprob(ev):
    """Per event: offline P(4 tags), P(exactly 3) of the 4 leading offline jets (pT > 25, |eta| < 2.5), truth-tagged
    with OFFLINE_P on their flavour (closure in qcd_tagfrac.py); 0 without 4 offline jets. Also returns which events
    are in the offline dumps at all (they cover part of the QCD files)."""
    rows, seen = {}, set()
    for f in sorted(glob.glob(os.environ.get("QCD_OFFLINE", "/scratch/submit/cms/novaka/l1pixels/offline/QCDFlat_*.npz"))):
        d = np.load(f)
        off = np.concatenate([[0], np.cumsum(d["njet"])])
        for i in range(len(d["njet"])):
            seen.add((int(d["lumi"][i]), int(d["event"][i])))
            sl = slice(off[i], off[i + 1])
            pt, eta, fl = d["pt"][sl], d["eta"][sl], d["flav"][sl]
            m = (pt > 25) & (abs(eta) < 2.5)
            if m.sum() < 4:
                continue
            fl4 = fl[m][np.argsort(-pt[m])[:4]]
            p = np.select([fl4 == 5, fl4 == 4], [OFFLINE_P[5], OFFLINE_P[4]], OFFLINE_P[0])[None, :]
            p4, p3 = tag_probs(p)
            rows[(int(d["lumi"][i]), int(d["event"][i]))] = (p4[0], p3[0])
    got = [rows.get((int(l), int(e)), (0.0, 0.0)) for l, e in zip(ev["lumi"], ev["event"])]
    cov = np.array([(int(l), int(e)) in seen for l, e in zip(ev["lumi"], ev["event"])])
    print(f"  offline dumps cover {cov.mean():.3f} of QCD events", flush=True)
    return np.array([g[0] for g in got]), np.array([g[1] for g in got]), cov


def ge2(p):
    """P(at least 2 of the 4 jets tagged)."""
    p1 = sum(p[:, k] * np.prod(np.where(np.arange(4)[None, :] == k, 1, 1 - p), 1) for k in range(4))
    return 1 - np.prod(1 - p, 1) - p1


def eff_map(pt, flav, passed, w=None):
    """Tag efficiency per (flavour, pT bin)."""
    w = np.ones(len(pt)) if w is None else w
    ib = np.clip(np.digitize(pt, PT_BINS) - 1, 0, len(PT_BINS) - 2)
    out = {}
    for f in (0, 4, 5):
        m = flav == f
        num = np.bincount(ib[m], w[m] * passed[m], len(PT_BINS) - 1)
        den = np.bincount(ib[m], w[m], len(PT_BINS) - 1)
        tot = (w[m] * passed[m]).sum() / max(w[m].sum(), 1e-12)
        out[f] = np.where(den > 20, num / np.maximum(den, 1e-12), tot)
    return out


def apply_map(emap, pt, flav):
    ib = np.clip(np.digitize(pt, PT_BINS) - 1, 0, len(PT_BINS) - 2)
    return np.select([flav == 5, flav == 4], [emap[5][ib], emap[4][ib]], emap[0][ib])


def templates(w_by_kl, cat_masks, m4j):
    """Per category: yields per m_4j bin at each kl point -> quadratic coefficients per bin."""
    kls = np.array(sorted(w_by_kl))
    V = np.vander(kls, 3, increasing=True)
    out = []
    for cm in cat_masks:
        y = np.array([np.histogram(m4j, M4J_BINS, weights=w_by_kl[k] * cm)[0] for k in kls])
        out.append(np.linalg.lstsq(V, y, rcond=None)[0])  # (3, nbins): a + b kl + c kl^2
    return np.concatenate(out, axis=1)


def background(wb, acc, probs, m4j, fixed=None):
    """Per category: m_4j shape of ALL accepted minimum-bias events in the window, times the category's mean tag
    probability (tag rate assumed independent of m_4j; the per-bin truth-tagged yields have too few effective
    events). A category with no tagged weight gets a one-event floor. b2: per-bin sum of squared weights of the shape."""
    acc = acc.astype(float)
    n = np.histogram(m4j, M4J_BINS, weights=acc)[0]
    h = np.histogram(m4j, M4J_BINS, weights=wb * acc)[0]
    h2 = np.histogram(m4j, M4J_BINS, weights=(wb * acc) ** 2)[0]
    b, b2 = [], []
    for i, p in enumerate(probs):
        f = fixed[i] if fixed is not None else (wb * acc * p).sum() / max((wb * acc).sum(), 1e-300)
        f = f if f > 0 else 1.0 / max(acc.sum(), 1.0)  # nothing tagged: one accepted event
        b.append(h * f)
        b2.append(h2 * f ** 2)
    return np.concatenate(b), np.concatenate(b2), np.concatenate([n] * len(probs))


def merge(coef, b, b2, n):
    """Merge adjacent m_4j bins (within each category block) until each holds >= N_MIN unweighted minimum-bias
    events: empty background bins would otherwise claim infinite sensitivity."""
    nb = len(M4J_BINS) - 1
    groups, cur, cnt = [], [], 0
    for i in range(len(b)):
        cur.append(i)
        cnt += n[i]
        if cnt >= N_MIN or (i + 1) % nb == 0:
            if cnt < N_MIN and groups and groups[-1][0] // nb == i // nb:
                groups[-1] += cur  # leftover at the block end joins the previous group
            else:
                groups.append(cur)
            cur, cnt = [], 0
    agg = lambda x: np.array([x[..., g].sum(-1) for g in groups]).T
    return agg(coef), np.array([b[g].sum() for g in groups]), np.array([b2[g].sum() for g in groups])


def scan(coef, b, truth=1.0):
    s = lambda k: np.maximum(coef[0] + coef[1] * k + coef[2] * k ** 2, 0)
    n = s(truth) + b
    q = np.array([2 * np.sum(np.where(n > 0, (s(k) + b) - n + n * np.log(np.maximum(n, 1e-300) / np.maximum(s(k) + b, 1e-300)), 0))
                  for k in KL_SCAN])
    return q


def interval(q, lvl, center=1.0):
    ok = KL_SCAN[q < lvl]
    # report the connected interval around the true kl and whether a second region is allowed
    i1 = np.argmin(abs(KL_SCAN - center))
    lo = i1
    while lo > 0 and q[lo - 1] < lvl:
        lo -= 1
    hi = i1
    while hi < len(q) - 1 and q[hi + 1] < lvl:
        hi += 1
    return [float(KL_SCAN[lo]), float(KL_SCAN[hi])], float(ok.max() - ok.min()) if len(ok) else 0.0, bool(len(ok) > hi - lo + 1)


def summarize(name, coef, b, b2, n, res):
    nb = len(M4J_BINS) - 1
    low = np.tile(M4J_BINS[1:nb + 1] <= LOW_M4J, len(b) // nb)  # unmerged bins below LOW_M4J (all categories)
    s_at = lambda c, k: c[0] + c[1] * k + c[2] * k ** 2
    s_low = {k: float(s_at(coef, k)[low].sum()) for k in TRUTHS}
    coef, b, b2 = merge(coef, b, b2, n)
    q = scan(coef, b)
    s1 = coef[0] + coef[1] + coef[2]
    z = np.sqrt(2 * np.sum(np.where(b > 0, (s1 + b) * np.log1p(s1 / np.maximum(b, 1e-300)) - s1, 0)))
    i68, w68, two68 = interval(q, 1.0)
    i95, w95, two95 = interval(q, 3.84)
    neff = float(b.sum() ** 2 / max(b2.sum(), 1e-300))
    res[name] = {"S": float(s1.sum()), "B": float(b.sum()), "Z_SM": float(z), "kl_68": i68, "kl_95": i95,
                 "width_68_total": w68, "second_region_68": two68, "width_95_total": w95, "second_region_95": two95,
                 "mb_neff": neff, "S_bins": s1.tolist(), "B_bins": b.tolist(), "q": q[::8].tolist(),
                 "S_low_m4j": s_low, "bsm": {}}
    # BSM truth: kl = t generated; interval around t, and how strongly the SM is excluded
    for t in TRUTHS[1:]:
        qt = scan(coef, b, truth=t)
        st = s_at(coef, t)
        res[name]["bsm"][str(t)] = {"S": float(st.sum()), "S_low_m4j": s_low[t], "kl_68": interval(qt, 1.0, t)[0],
                                    "kl_95": interval(qt, 3.84, t)[0], "Z_exclude_SM": float(np.sqrt(max(np.interp(1.0, KL_SCAN, qt), 0))),
                                    "q": qt[::8].tolist()}
        r = res[name]["bsm"][str(t)]
        print(f"{'':22s} truth kl={t:g}: S {r['S']:8.1f} (m4j<{LOW_M4J:g}: {r['S_low_m4j']:7.1f})  kl 68% [{r['kl_68'][0]:+.2f}, {r['kl_68'][1]:+.2f}]"
              f"  SM excluded at {r['Z_exclude_SM']:.2f} sigma", flush=True)
    print(f"{name:22s} S {s1.sum():8.1f}  B {b.sum():10.3g} (MB n_eff {neff:7.1f})  Z {z:5.2f}  "
          f"kl 68% [{i68[0]:+.2f}, {i68[1]:+.2f}]{' +2nd' if two68 else ''}  95% [{i95[0]:+.2f}, {i95[1]:+.2f}]{' +2nd' if two95 else ''}",
          flush=True)
    return q


def main():
    out, hh_pat, mb_pat, l1lists, sp_path, gen_glob, kl_glob = sys.argv[1:8]
    fh, fq, fm1, fm2 = l1lists.split(":")
    print("training the L1 pixel tagger (as seed_plane.py)", flush=True)
    lh, lq, lm, (s_h, s_q, s_m) = tagger(fh, fq, f"{fm1},{fm2}", l1=True)
    hh, mb = read(hh_pat), read(mb_pat)
    qcd_pat = os.environ.get("QCD_GLOB", "/scratch/submit/cms/novaka/l1pixels/local_v3/perfNano_QCDFlat_*.root")
    qcd = read(qcd_pat)
    print(f"HH {len(hh['ht'])}, MB {len(mb['ht'])}, QCD {len(qcd['ht'])} events", flush=True)
    attach(hh, lh, s_h)
    attach(mb, lm, s_m)
    attach(qcd, lq, s_q)
    for ev in (hh, mb, qcd):
        kinematics(ev)
    # QCD: seed-plane sums (as seed_plane.py) and offline truth-tag probabilities, for the background tag fractions
    qe = D.events(qcd_pat)
    qcd["sp_ht"], qcd["sp_menu"], qcd["sp_nn"] = qe["ht"], qe["menu"], qe["nn_sum"]
    qcd["sp_l1"] = D.jet_scores(qe, lq, s_q)
    qcd["sp_perfect"] = D.jet_scores(qe, lq, (lq["flav"] == 5).astype(float))
    qcd["off4"], qcd["off3"], qcd["offcov"] = offline_tagprob(qcd)

    # --- L1 seeds from the seed-plane sums (identical taggers), thresholds on even events
    sp = np.load(sp_path)
    for ev, p in ((hh, "hh"), (mb, "mb")):
        pos = {(l, e): i for i, (l, e) in enumerate(zip(sp[f"{p}_lumi"], sp[f"{p}_event"]))}
        ix = np.array([pos[(l, e)] for l, e in zip(ev["lumi"], ev["event"])])
        for k in ("ht", "menu", "nn", "l1", "perfect"):
            ev[f"sp_{k}"] = sp[f"{p}_{k}"][ix]
    fid = np.ones(len(hh["ht"]), bool)  # thresholds maximise efficiency on all HH events
    ev_hh, ev_mb = hh["event"] % 2 == 0, mb["event"] % 2 == 0
    w_fold = len(mb["ht"]) / MB_TOTAL * D.BX_KHZ / ev_mb.sum()
    seeds = {"menu": (hh["sp_menu"].astype(bool), mb["sp_menu"].astype(bool))}
    qseeds = {"menu": qcd["sp_menu"].astype(bool)}
    for tag in ("nn", "l1", "perfect"):
        e, h, s = D.best(hh[f"sp_{tag}"][ev_hh], hh["sp_ht"][ev_hh], fid[ev_hh], mb[f"sp_{tag}"][ev_mb],
                         mb["sp_ht"][ev_mb], np.full(ev_mb.sum(), w_fold), SEED_KHZ,
                         hh["sp_menu"][ev_hh].astype(bool), mb["sp_menu"][ev_mb].astype(bool))
        seeds[tag] = (((hh["sp_ht"] > h) & (hh[f"sp_{tag}"] > s)) | seeds["menu"][0],
                      ((mb["sp_ht"] > h) & (mb[f"sp_{tag}"] > s)) | seeds["menu"][1])
        qseeds[tag] = ((qcd["sp_ht"] > h) & (qcd[f"sp_{tag}"] > s)) | qseeds["menu"]
        print(f"seed menu + {tag}: HT > {h:.0f}, sum > {s:.2f}, added rate "
              f"{(seeds[tag][1] & ~seeds['menu'][1]).sum() * D.BX_KHZ / MB_TOTAL:.2f} kHz", flush=True)

    # --- signal weights per kl (odd HH events), background weights
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
    odd = ~ev_hh
    w_sm = odd * SIG_SM / odd.sum()
    w_kl = {kl: w_sm * XS(kl) * np.where(dens[1.0] > 0, dens[kl] / np.maximum(dens[1.0], 1e-12), 0.0)[ib] for kl in nano}
    w_mb = np.full(len(mb["ht"]), N_BX / MB_TOTAL)

    base_hh = hh["n4"] & (hh["ht"] > HT_CUT)
    base_mb = mb["n4"] & (mb["ht"] > HT_CUT)
    base_q = qcd["n4"] & (qcd["ht"] > HT_CUT)
    # background tag fractions conditional on the stream's L1 acceptance: a b-tagged seed accepts b-rich events
    qfrac = lambda acc, p4, p3: (float(p4[base_q & acc].mean()), float(p3[base_q & acc].mean()), int((base_q & acc).sum()))
    allq = np.ones(len(qcd["ht"]), bool)
    qfrac_off = lambda acc: qfrac(acc & qcd["offcov"], qcd["off4"], qcd["off3"])  # offline tags: covered events only

    nb_q_all = np.minimum((qcd["flav"] == 5).sum(1), 3)
    cf4 = np.array([qcd["off4"][base_q & qcd["offcov"] & (nb_q_all == c)].mean() if (base_q & (nb_q_all == c)).any() else 0.0
                    for c in range(4)])
    print("  QCD offline P4 by number of true L1 b jets 0/1/2/3+:", np.array2string(cf4, precision=2), flush=True)

    def strata_bkg(strata, name, p4, p3):
        """Minimum-bias strata as separate analysis categories (blocks of 4-tag, 3-tag bins), each with the offline tag
        fractions of the QCD events in the same L1 class (the first stratum's fractions below 10 QCD events). Minimum-
        bias flavour labels are empty (pileup interactions carry no generator record), so the flavour content of the
        background comes from QCD only."""
        tot, first = None, None
        for k, entry in enumerate(strata):
            mb_mask, q_mask = entry[:2]
            key = entry[2] if len(entry) > 2 else None
            f4, f3, nq = qfrac_off(q_mask)
            if nq < 10 and first is not None:
                f4, f3 = first
            first = first or (f4, f3)
            nb_m, nb_q = (mb["flav"][mb_mask] == 5).sum(1), (qcd["flav"][base_q & q_mask] == 5).sum(1)
            # alternative: each MB event weighted by the QCD offline fractions of its own number of true L1 b jets
            alt4 = float((w_mb[mb_mask] * cf4[np.minimum(nb_m, 3)]).sum())
            res["setup"]["qcd_tagfrac_by_stream"][f"{name}_{k}"] = [f4, f3, nq]
            res["setup"].setdefault("bkg_diag", {})[f"{name}_{k}"] = {
                "mb_events": int(mb_mask.sum()), "qcd_events": nq, "mb_nb": np.bincount(np.minimum(nb_m, 3), minlength=4).tolist(),
                "qcd_nb": np.bincount(np.minimum(nb_q, 3), minlength=4).tolist(), "B4_strata": float((w_mb[mb_mask]).sum() * f4),
                "B4_by_nb": alt4}
            print(f"  {name} stratum {k}: QCD offline P4 {f4:.2e} P3 {f3:.2e} ({nq} QCD events, {int(mb_mask.sum())} MB events); "
                  f"true-b count 0/1/2/3+ MB {np.bincount(np.minimum(nb_m, 3), minlength=4).tolist()} QCD "
                  f"{np.bincount(np.minimum(nb_q, 3), minlength=4).tolist()}; B4 strata {(w_mb[mb_mask]).sum() * f4:.3g} by-nb {alt4:.3g}", flush=True)
            if key is not None and os.environ.get("BKG_MODEL", "score") == "score":
                # each minimum-bias event gets the offline 4b / 3b fraction of QCD events with a similar seed score
                # (score bins of ~650 QCD events), instead of the few QCD events the seed itself adds
                qs = qcd[key][base_q & qcd["offcov"]]
                edges = np.unique(np.quantile(qs, np.linspace(0, 1, 11)))
                iq = np.clip(np.digitize(qs, edges[1:-1]), 0, len(edges) - 2)
                f4b = np.array([qcd["off4"][base_q & qcd["offcov"]][iq == c].mean() for c in range(len(edges) - 1)])
                f3b = np.array([qcd["off3"][base_q & qcd["offcov"]][iq == c].mean() for c in range(len(edges) - 1)])
                im = np.clip(np.digitize(mb[key], edges[1:-1]), 0, len(edges) - 2)
                e4, e3 = f4b[im], f3b[im]
                print(f"  {name} stratum {k}: score-binned QCD P4 per {key} decile " + " ".join(f"{x:.1e}" for x in f4b)
                      + f"; mean over these MB events {(w_mb * mb_mask * e4).sum() / max((w_mb * mb_mask).sum(), 1e-300):.2e}", flush=True)
                res["setup"].setdefault("score_binned", {})[f"{name}_{k}"] = {"key": key, "edges": edges.tolist(), "P4": f4b.tolist(), "P3": f3b.tolist()}
                part = background(w_mb, mb_mask, [e4, e3], mb["m4j"])
            else:
                part = background(w_mb, mb_mask, [p4, p3], mb["m4j"], fixed=(f4, f3))
            tot = part if tot is None else tuple(np.concatenate([x, y]) for x, y in zip(tot, part))
        return tot
    # Higgs-candidate window from true 4b signal events
    t4 = base_hh & (hh["flav"] == 5).all(1)
    c1, c2 = np.median(hh["m1"][t4]), np.median(hh["m2"][t4])
    r1, r2 = 1.4826 * np.median(abs(hh["m1"][t4] - c1)), 1.4826 * np.median(abs(hh["m2"][t4] - c2))
    win = lambda ev: np.hypot((ev["m1"] - c1) / r1, (ev["m2"] - c2) / r2) < 1.6
    print(f"H window: ({c1:.0f} +- {r1:.0f}, {c2:.0f} +- {r2:.0f}) GeV, radius 1.6", flush=True)
    hw, mw = base_hh & win(hh), base_mb & win(mb)
    res = {"setup": {"N_BX": N_BX, "w_mb": N_BX / MB_TOTAL, "S_SM_total": SIG_SM, "window": [c1, r1, c2, r2],
                     "m4j_bins": M4J_BINS.tolist(), "signal_base_eff": float((w_sm * hw).sum() / SIG_SM),
                     "mb_base_events": int(mw.sum())}}
    curves = {"kl": KL_SCAN[::8].tolist()}

    # --- triggered stream: L1 accept x offline-like tag probabilities
    p_off_hh, p_off_mb = (np.select([ev["flav"] == 5, ev["flav"] == 4], [OFFLINE_P[5], OFFLINE_P[4]], OFFLINE_P[0])
                          for ev in (hh, mb))
    (h4, h3), (m4, m3) = tag_probs(p_off_hh), tag_probs(p_off_mb)
    # the few hundred accepted minimum-bias events cannot resolve the flavour content of a 4-tag QCD sample: take the
    # 4b / 3b fractions from QCD offline jets (qcd_tagfrac.py: truth-tagged P4, measured P3)
    qf = json.load(open(os.environ.get("QCD_TAGFRAC", "qcd_tagfrac.json")))
    res["setup"]["qcd_tagfrac_inclusive"] = (qf["truth_P4"], qf["measured_P3"])
    res["setup"]["qcd_tagfrac_by_stream"] = {}
    res["setup"]["mb_own_tagfrac_menu"] = [float((w_mb * mw * seeds["menu"][1] * x).sum() / (w_mb * mw * seeds["menu"][1]).sum()) for x in (m4, m3)]
    trig = {}
    for sd, (ah, am) in seeds.items():
        mh = seeds["menu"][0]
        # categories: menu-accepted, and the seed-added events split into N_CAT bins of seed score (as an analysis
        # would; one lumped category lets low-purity added events dilute the good ones), each with its own QCD fractions
        cats_h, strata = [mh], [(mw & seeds["menu"][1], qseeds["menu"])]
        if sd in ("nn", "l1"):
            key = f"sp_{sd}"
            # edges from the seed-added minimum-bias events, so every category keeps its own background events
            n_added = int((mw & am & ~seeds["menu"][1]).sum())
            ncat = N_CAT if N_CAT > 0 else int(np.clip(n_added // 10, 1, 8))  # ~10 minimum-bias events per category
            edges = np.quantile(mb[key][mw & am & ~seeds["menu"][1]], np.linspace(0, 1, ncat + 1)[1:-1])
            print(f"  trig_{sd}: {n_added} seed-added minimum-bias events in the window -> {ncat} score categories", flush=True)
            cat = lambda x: np.digitize(x, edges)
            for c in range(ncat):
                cats_h.append(ah & ~mh & (cat(hh[key]) == c))
                strata.append((mw & am & ~seeds["menu"][1] & (cat(mb[key]) == c), qseeds[sd] & ~qseeds["menu"], key))
        else:
            cats_h.append(ah & ~mh)
            strata.append((mw & am & ~seeds["menu"][1], qseeds[sd] & ~qseeds["menu"]))
        coef = templates(w_kl, [hw * cm * t for cm in cats_h for t in (h4, h3)], hh["m4j"])
        b, b2, n = strata_bkg(strata, f"trig_{sd}", m4, m3)
        trig[sd] = (coef, b, b2, n)
        curves[f"trig_{sd}"] = summarize(f"trig_{sd}", coef, b, b2, n, res)[::8].tolist()

    # --- scouting stream: L1 tags, every crossing with HT > 150
    jets_mb = base_mb[:, None] & np.ones((1, 4), bool)
    flav_mb, pt_mb = mb["flav"][jets_mb], mb["pt"][jets_mb]
    closure, scout = {}, {}
    for tag in ("nn", "l1", "perfect"):
        best_ = None
        for mis in (MISTAGS if tag != "perfect" else (0.0,)):
            thr = 0.5 if tag == "perfect" else np.quantile(mb[tag][jets_mb][flav_mb == 0], 1 - mis)
            emap = eff_map(pt_mb, flav_mb, mb[tag][jets_mb] > thr)
            # b-jet efficiencies from HH (odd) b jets: minimum bias has few
            jh = (base_hh & odd)[:, None] & (hh["flav"] == 5)
            emap[5] = eff_map(hh["pt"][jh], hh["flav"][jh], hh[tag][jh] > thr)[5]
            pm = apply_map(emap, mb["pt"], mb["flav"])
            nt_h, nt_m = (hh[tag] > thr).sum(1), (mb[tag] > thr).sum(1)
            # tags are correlated within minimum-bias events: scale the non-b probabilities until the truth-tagged
            # >= 2-tag count matches the direct one (conservative for 3 and 4 tags), when it is measurable
            n2 = (base_mb & (nt_m >= 2)).sum()
            k = 1.0
            if tag != "perfect" and n2 >= 5:
                lo_, hi_ = 0.1, 50.0
                for _ in range(60):
                    k = np.sqrt(lo_ * hi_)
                    pk = np.where(mb["flav"] == 5, pm, np.minimum(pm * k, 1.0))
                    if (base_mb * ge2(pk)).sum() > n2:
                        hi_ = k
                    else:
                        lo_ = k
                pm = np.where(mb["flav"] == 5, pm, np.minimum(pm * k, 1.0))
            q4, q3 = tag_probs(pm)
            pq = apply_map(emap, qcd["pt"], qcd["flav"])
            pq = np.where(qcd["flav"] == 5, pq, np.minimum(pq * k, 1.0))
            qq4, qq3 = tag_probs(pq)  # the same L1 tag maps on QCD flavour content
            cats_h = [hw * (nt_h == 4), hw * (nt_h == 3)]
            coef = templates(w_kl, cats_h, hh["m4j"])
            f4, f3, _ = qfrac(np.ones(len(qcd["ht"]), bool), qq4, qq3)
            b, b2, n = background(w_mb, mw, [q4, q3], mb["m4j"], fixed=(f4, f3))
            q = scan(*merge(coef, b, b2, n)[:2])
            width = float(np.ptp(KL_SCAN[q < 1.0])) if (q < 1.0).any() else 99.0
            # closure on minimum bias: >= 2 tags, direct vs truth-tagged (base selection, no window)
            closure[f"{tag}_{mis}"] = {"ge2_direct": int(n2), "ge2_truth_raw": float((base_mb * ge2(apply_map(emap, mb["pt"], mb["flav"]))).sum()),
                                       "nonb_scale": float(k), "ge2_truth": float((base_mb * ge2(pm)).sum()),
                                       "ge3_direct": int((base_mb & (nt_m >= 3)).sum()), "ge3_truth": float((base_mb * (q4 + q3)).sum()),
                                       "eff_b_mean": float(emap[5].mean()), "thr": float(thr)}
            if best_ is None or width < best_[0]:
                best_ = (width, mis, thr, coef, b, b2, n, nt_h, q4, q3, qq4, qq3)
        width, mis, thr, coef, b, b2, n, nt_h, q4, q3, qq4, qq3 = best_
        print(f"scouting {tag}: best light mistag {mis} (threshold {thr:.3f})", flush=True)
        res.setdefault("scout_wp", {})[tag] = {"mistag": mis, "thr": float(thr)}
        scout[tag] = (nt_h, q4, q3, qq4, qq3)
        res["setup"]["qcd_tagfrac_by_stream"][f"scout_{tag}"] = list(qfrac(np.ones(len(qcd["ht"]), bool), qq4, qq3))
        curves[f"scout_{tag}"] = summarize(f"scout_{tag}", coef, b, b2, n, res)[::8].tolist()
    res["closure_mb"] = closure

    # --- ceiling for any scouting tagger: every crossing with HT > 150, offline-quality tag probabilities and QCD tag
    # fractions (as the triggered stream, without an L1 accept); L1-jet kinematics are kept
    mh = seeds["menu"][0]
    coef = templates(w_kl, [hw * mh * h4, hw * mh * h3, hw * ~mh * h4, hw * ~mh * h3], hh["m4j"])
    b, b2, n = strata_bkg([(mw & seeds["menu"][1], qseeds["menu"]), (mw & ~seeds["menu"][1], ~qseeds["menu"])], "scout_offtag", m4, m3)
    curves["scout_offtag"] = summarize("scout_offtag", coef, b, b2, n, res)[::8].tolist()

    # --- combined: triggered (offline tags) for accepted events, scouting (L1 tags) for the rest
    # ("menu", "l1") / ("nn", "l1"): fallback - no pixel tag in the real-time decision, pixel tags only in scouting
    for sd, tag in (("menu", "nn"), ("nn", "nn"), ("l1", "l1"), ("perfect", "perfect"), ("menu", "l1"), ("nn", "l1")):
        ah, am = seeds[sd]
        nt_h, q4, q3, qq4, qq3 = scout[tag]
        coef_t, b_t, b2_t, n_t = trig[sd]
        coef_s = templates(w_kl, [hw * ~ah * (nt_h == 4), hw * ~ah * (nt_h == 3)], hh["m4j"])
        f4, f3, _ = qfrac(~qseeds[sd], qq4, qq3)
        b_s, b2_s, n_s = background(w_mb, mw & ~am, [q4, q3], mb["m4j"], fixed=(f4, f3))
        coef, b, b2 = np.concatenate([coef_t, coef_s], 1), np.concatenate([b_t, b_s]), np.concatenate([b2_t, b2_s])
        curves[f"comb_{sd}_{tag}"] = summarize(f"comb_{sd}+scout_{tag}", coef, b, b2, np.concatenate([n_t, n_s]), res)[::8].tolist()
    res["curves"] = curves
    json.dump(res, open(out, "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()

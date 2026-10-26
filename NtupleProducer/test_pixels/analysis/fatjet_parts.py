#!/usr/bin/env python3
"""Per-file large-jet table for the boosted H -> cc / bb study: L1 R = 0.8 jets with a constituent mass, the
two-prong score and the R = 0.4 jets inside them (keys into the per-jet pixel lists).

    python3 fatjet_parts.py OUT.npz SAMPLE file1.root [file2.root ...]
Jets: sc8PuppiCorrJets with pT > PT8_MIN (default 100), |eta| < 2.4, up to 3 per event (by pT).
  mass      invariant mass of the L1 PUPPI candidates within dR < 0.8 of the jet axis, scaled by the jet's
            corrected / raw pT (the L1 jet mass is not filled)
  prong     score of the L1SC8ProngJets jet within dR < 0.2 (uncorrected jets, same seeds), -1 if none
  sub       indices of the two highest-pT L1NGJets (pT > 15, |eta| < 2.4) within dR < 0.8 (-1 if fewer)
Per event: generator Higgs proxy as in fatjet_first.py (vector sum of the generator jets of flavour FLAV, pT > 20,
within dR < 0.8 of the leading one), and the event-level menu flags of vbf_menu.py (SingleJet230, HT seeds).
"""
import os
import sys

import awkward as ak
import numpy as np
import uproot

from vbf_menu import HT_ALONE, thr

PT8_MIN = float(os.environ.get("PT8_MIN", 100))
FLAV = int(os.environ.get("FLAV", 4))
NJ = 3
BR = ["luminosityBlock", "event", "sc8PuppiCorrJets_*", "L1SC8ProngJets_*", "L1PuppiCands_pt", "L1PuppiCands_eta",
      "L1PuppiCands_phi", "L1PuppiCands_mass", "L1NGJets_pt", "L1NGJets_eta", "L1NGJets_phi", "scPuppiCorrJets_pt",
      "scPuppiCorrJets_eta", "GenJets_pt", "GenJets_eta", "GenJets_phi", "GenJets_mass", "GenJets_hadronFlavour"]


def dphi(a, b):
    return (a - b + np.pi) % (2 * np.pi) - np.pi


def cone_mass(pt, eta, phi, m):
    px, py = pt * np.cos(phi), pt * np.sin(phi)
    pz, e = pt * np.sinh(eta), np.sqrt((pt * np.cosh(eta)) ** 2 + m ** 2)
    m2 = e.sum() ** 2 - px.sum() ** 2 - py.sum() ** 2 - pz.sum() ** 2
    return np.sqrt(max(m2, 0.0)), np.hypot(px.sum(), py.sum())


def higgs_proxy(ev):
    pt, eta, phi, m, fl = (ak.to_numpy(ev[f"GenJets_{k}"]) for k in ("pt", "eta", "phi", "mass", "hadronFlavour"))
    q = np.where((fl == FLAV) & (pt > 20))[0]
    if not len(q):
        return 0.0, 0.0, 0.0, 0
    lead = q[np.argmax(pt[q])]
    near = q[np.hypot(eta[q] - eta[lead], dphi(phi[q], phi[lead])) < 0.8]
    px, py = (pt[near] * np.cos(phi[near])).sum(), (pt[near] * np.sin(phi[near])).sum()
    pz = (pt[near] * np.sinh(eta[near])).sum()
    hpt = np.hypot(px, py)
    return hpt, np.arcsinh(pz / max(hpt, 1e-6)), np.arctan2(py, px), len(near)


def process(arr):
    rows, evs = [], []
    for i in range(len(arr)):
        ev = arr[i]
        hpt, heta, hphi, nq = higgs_proxy(ev)
        jc_pt, jc_eta = ak.to_numpy(ev.scPuppiCorrJets_pt), ak.to_numpy(ev.scPuppiCorrJets_eta)
        c = abs(jc_eta) < 2.4
        single = bool((jc_pt[c] > thr(230, jc_eta[c])).any()) if c.any() else False
        ng_pt, ng_eta, ng_phi = (ak.to_numpy(ev[f"L1NGJets_{k}"]) for k in ("pt", "eta", "phi"))
        ht = float(ng_pt[(abs(ng_eta) < 2.4) & (ng_pt > 30)].sum())
        evs.append((int(ev.luminosityBlock), int(ev.event), hpt, heta, hphi, nq, single, ht > HT_ALONE, ht))
        jpt, jeta, jphi = (ak.to_numpy(ev[f"sc8PuppiCorrJets_{k}"]) for k in ("pt", "eta", "phi"))
        sel = np.where((jpt > PT8_MIN) & (abs(jeta) < 2.4))[0]
        sel = sel[np.argsort(-jpt[sel])][:NJ]
        if not len(sel):
            continue
        cpt, ceta, cphi, cm = (ak.to_numpy(ev[f"L1PuppiCands_{k}"]) for k in ("pt", "eta", "phi", "mass"))
        ppt, peta, pphi, psc = (ak.to_numpy(ev[f"L1SC8ProngJets_{k}"]) for k in ("pt", "eta", "phi", "score_nprong"))
        ng_ok = (ng_pt > 15) & (abs(ng_eta) < 2.4)
        for rank, j in enumerate(sel):
            inc = np.hypot(ceta - jeta[j], dphi(cphi, jphi[j])) < 0.8
            m_raw, pt_raw = cone_mass(cpt[inc], ceta[inc], cphi[inc], cm[inc])
            mass = m_raw * jpt[j] / max(pt_raw, 1e-3)
            dp = np.hypot(peta - jeta[j], dphi(pphi, jphi[j]))
            prong = float(psc[np.argmin(dp)]) if len(dp) and dp.min() < 0.2 else -1.0
            dn = np.hypot(ng_eta - jeta[j], dphi(ng_phi, jphi[j]))
            sub = np.where(ng_ok & (dn < 0.8))[0]
            sub = sub[np.argsort(-ng_pt[sub])][:2]
            sub = np.concatenate([sub, -np.ones(2 - len(sub), int)])
            dh = np.hypot(jeta[j] - heta, dphi(jphi[j], hphi)) if hpt > 0 else 99.0
            rows.append((len(evs) - 1, rank, jpt[j], jeta[j], jphi[j], mass, m_raw, prong, sub[0], sub[1], dh))
    return rows, evs


def main():
    outname, sample, files = sys.argv[1], sys.argv[2], sys.argv[3:]
    rows, evs = [], []
    for chunk in uproot.iterate([f + ":Events" for f in files], filter_name=BR, step_size=100, library="ak"):
        r, e = process(chunk)
        rows += [(t[0] + len(evs),) + tuple(t[1:]) for t in r]
        evs += e
    J = np.array(rows, float).reshape(-1, 11)
    E = np.array(evs, float).reshape(-1, 9)
    np.savez_compressed(outname, sample=sample,
                        jet=J, jet_cols=["evt", "rank", "pt", "eta", "phi", "mass", "mass_raw", "prong", "sub0", "sub1", "dr_h"],
                        ev=E, ev_cols=["lumi", "event", "hpt", "heta", "hphi", "nq", "single230", "ht450", "ht"])
    print(f"{sample}: {len(E)} events, {len(J)} large jets -> {outname}")


if __name__ == "__main__":
    main()

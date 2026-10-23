#!/usr/bin/env python3
"""Per-jet padded lists of pixel tracks (and their hits) for set-based models and the bandwidth study.

    python3 make_lists.py out.npz SAMPLE file1.root [file2.root ...]

For every L1 SC4NG jet (pT > 30 GeV, |eta| < 2.4): the NMAX vertex-compatible pixel tracks in the
cone (same selection as make_jets.py), ordered by signed IP significance, with track features and
the features of their 4 hits. Also the jet's NN class scores, kinematics and gen flavour.
"""
import sys

import awkward as ak
import numpy as np
import uproot

import make_jets as MJ

NMAX = 16
NHIT = 4
TRK_FEATS = ["logpt", "ptrel", "deta", "dphi", "sip", "sipsig", "dzpv", "chi2ndof", "charge"]
HIT_FEATS = ["hdphi", "hdeta", "r", "absz", "layer", "barrel", "sizeX", "sizeY", "adc"]
SCORES = ["b", "c", "uds", "g", "tau_p", "tau_n", "mu", "e"]

BRANCHES = MJ.BRANCHES + ["PixelTracks_charge", "PixelTracks_chi2", "PixelTracks_ndof", "PixelTracks_hitIdx",
                          "PixelTracks_nHits", "PixelHits_x", "PixelHits_y", "PixelHits_z", "PixelHits_layer",
                          "PixelHits_subdet", "PixelHits_sizeX", "PixelHits_sizeY", "PixelHits_adc"]


def process(arr):
    zpv = ak.to_numpy(MJ.leading_vertex_z(arr))
    out = {k: [] for k in ["trk", "hit", "ntrk", "pt", "eta", "flav", "evt", "scores"]}
    for i in range(len(arr)):
        ev = arr[i]
        jpt, jeta, jphi = (ak.to_numpy(ev[f"L1NGJets_{k}"]) for k in ("pt", "eta", "phi"))
        sel_j = (jpt > 30) & (abs(jeta) < 2.4)
        if not sel_j.any():
            continue
        tpt, teta, tphi = (ak.to_numpy(ev[f"PixelTracks_{k}"]) for k in ("pt", "eta", "phi"))
        tdz, tdxy, terr = (ak.to_numpy(ev[f"PixelTracks_{k}"]) for k in ("dz", "dxyBS", "dxyErr"))
        tq, tchi2, tndof = (ak.to_numpy(ev[f"PixelTracks_{k}"]) for k in ("charge", "chi2", "ndof"))
        thidx = ak.to_numpy(ev.PixelTracks_hitIdx)
        hx, hy, hz = (ak.to_numpy(ev[f"PixelHits_{k}"]) for k in ("x", "y", "z"))
        hl, hs, hsx, hsy, hadc = (ak.to_numpy(ev[f"PixelHits_{k}"]) for k in ("layer", "subdet", "sizeX", "sizeY", "adc"))
        good = (tpt > MJ.PT_TRK) & (abs(tdz - zpv[i]) < MJ.DZ_PV)
        gpt, geta, gphi = (ak.to_numpy(ev[f"GenJets_{k}"]) for k in ("pt", "eta", "phi"))
        gfl = ak.to_numpy(ev.GenJets_hadronFlavour)
        for j in np.where(sel_j)[0]:
            # gen flavour (closest gen jet within DR_GEN)
            flav = -1
            if len(gpt):
                dr = np.hypot(geta - jeta[j], MJ.dphi(gphi, jphi[j]))
                k = np.argmin(dr)
                flav = int(gfl[k]) if dr[k] < MJ.DR_GEN else -1
            dphi_t = MJ.dphi(tphi, jphi[j])
            cone = good & (np.hypot(teta - jeta[j], dphi_t) < MJ.DR_TRK)
            idx = np.where(cone)[0]
            sip = np.sign(tdxy[idx] * np.sin(-dphi_t[idx])) * abs(tdxy[idx])
            sig = sip / terr[idx]
            order = np.argsort(-sig)[:NMAX]
            idx, sip, sig = idx[order], sip[order], sig[order]
            n = len(idx)
            trk = np.zeros((NMAX, len(TRK_FEATS)), np.float32)
            hit = np.zeros((NMAX, NHIT, len(HIT_FEATS)), np.float32)
            if n:
                trk[:n] = np.stack([np.log(tpt[idx]), tpt[idx] / jpt[j], teta[idx] - jeta[j], dphi_t[idx], sip * 10.0,
                                    np.clip(sig, -50, 50), tdz[idx] - zpv[i], tchi2[idx] / np.maximum(tndof[idx], 1),
                                    tq[idx]], axis=1)
                for a, t in enumerate(idx):
                    h = np.arange(thidx[t], thidx[t] + NHIT)
                    r = np.hypot(hx[h], hy[h])
                    hit[a] = np.stack([MJ.dphi(np.arctan2(hy[h], hx[h]), jphi[j]),
                                       np.arcsinh((hz[h] - zpv[i]) / r) - jeta[j], r, abs(hz[h]), hl[h],
                                       (hs[h] == 1).astype(float), hsx[h], hsy[h], hadc[h] / 1e4], axis=1)
            out["trk"].append(trk)
            out["hit"].append(hit)
            out["ntrk"].append(n)
            out["pt"].append(jpt[j])
            out["eta"].append(jeta[j])
            out["flav"].append(flav)
            out["evt"].append(i)
            out["scores"].append([float(ev[f"L1NGJets_score_{c}"][j]) for c in SCORES])
    return {k: np.array(v) for k, v in out.items()}


def main():
    outname, sample, files = sys.argv[1], sys.argv[2], sys.argv[3:]
    parts, offset = [], 0
    for chunk in uproot.iterate([f + ":Events" for f in files], filter_name=BRANCHES, step_size="300 MB", library="ak"):
        p = process(chunk)
        if len(p["pt"]):
            p["evt"] = p["evt"] + offset
            parts.append(p)
        offset += len(chunk)
    cols = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
    np.savez_compressed(outname, sample=sample, trk_feats=TRK_FEATS, hit_feats=HIT_FEATS, **cols)
    print(f"{sample}: {offset} events, {len(cols['pt'])} jets, median tracks/jet {np.median(cols['ntrk']):.0f} -> {outname}")


if __name__ == "__main__":
    main()

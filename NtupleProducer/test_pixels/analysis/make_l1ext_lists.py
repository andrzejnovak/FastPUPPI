#!/usr/bin/env python3
"""Per-jet padded lists like make_lists.py, but with L1 tracks extended into the pixel detector (l1ext.py)
instead of HLT pixel tracks: the realistic-L1 version of the pixel information.

    python3 make_l1ext_lists.py out.npz SAMPLE file1.root [file2.root ...]

Tracks: L1 tracks (pT > 2 GeV) within dR < 0.4 of the jet with at least 2 associated pixel clusters, refit d0 and z0.
Vertex: the L1 vertex, refined with the refit z0 of extended tracks within 1 cm of it (median); tracks within
DZ_PV of it are kept, as for the HLT pixel tracks. Track features and ordering as in make_lists.py (the d0 error from
l1ext.d0_err, chi2/ndof from the pixel refit); no hit features. Also counts tracks that found no pixel clusters.

MODE=otonly: no pixels at all; the displaced (5-parameter) L1 tracks with their Outer-Tracker-only d0 and z0
(d0 sign flipped to the CMS convention; resolution 200-650 um vs HLT pixel tracks, D0_ERR_OT), vertex = L1 vertex,
|z0 - z_vtx| < DZ_OT. The intermediate step of the chain: what the Outer Tracker alone says about displacement.
"""
import os
import sys

import awkward as ak
import numpy as np
import uproot

import l1ext as X
import make_jets as MJ
from make_lists import NHIT, NMAX, SCORES, TRK_FEATS, HIT_FEATS

JET_PTMIN = float(os.environ.get("JET_PTMIN", 15))
PT_L1 = 2.0
MODE = os.environ.get("MODE", "pixel")
D0_ERR_OT = (0.018, 0.15)  # [cm] hypot(a, b / pT), fit to the OT-only d0 spread vs HLT pixel tracks
DZ_OT = 0.5  # [cm] vertex compatibility for OT-only z0 (1-2 mm resolution)
D0_MAX_OT = 1.0  # [cm]
BRANCHES = ["L1NGJets_*", "GenJets_pt", "GenJets_eta", "GenJets_phi", "GenJets_hadronFlavour", "L1Tracks_*",
            "L1TracksVtx_z0", "luminosityBlock", "event"] + (["L1TracksExt_*"] if MODE == "otonly" else ["PixelClusters_*"])
TRK = "L1TracksExt" if MODE == "otonly" else "L1Tracks"


def process(arr):
    out = {k: [] for k in ["trk", "hit", "ntrk", "nl1", "pt", "eta", "flav", "evt", "scores", "jidx", "lumi", "event"]}
    for i in range(len(arr)):
        ev = arr[i]
        jpt, jeta, jphi = (ak.to_numpy(ev[f"L1NGJets_{k}"]) for k in ("pt", "eta", "phi"))
        sel_j = (jpt > JET_PTMIN) & (abs(jeta) < 2.4)
        if not sel_j.any():
            continue
        tpt, teta, tphi, tz0, tq, tchi = (ak.to_numpy(ev[f"{TRK}_{k}"]) for k in ("pt", "eta", "phi", "z0", "charge", "chi2XY"))
        zl1 = float(ev.L1TracksVtx_z0[0]) if len(ev.L1TracksVtx_z0) else 0.0
        cl = X.sort_phi(X.clusters_of(ev)) if MODE != "otonly" else None
        # extend every L1 track that is in some selected jet cone (once per track)
        incone = np.zeros(len(tpt), bool)
        for j in np.where(sel_j)[0]:
            incone |= np.hypot(teta - jeta[j], MJ.dphi(tphi, jphi[j])) < MJ.DR_TRK
        cand = np.where(incone & (tpt > PT_L1) & (abs(tz0 - zl1) < 1.5))[0]
        ext = {}
        if MODE == "otonly":
            td0, tns = ak.to_numpy(ev[f"{TRK}_d0"]), ak.to_numpy(ev[f"{TRK}_nStubs"])
            # b-hadron tracks have |d0| of at most a few mm; the displaced collection also has cm-scale tracks
            ext = {t: (-td0[t], tz0[t], tchi[t] / max(2 * tns[t] - 5, 1), int(tns[t])) for t in cand if abs(td0[t]) < D0_MAX_OT}
            cand = []
        for t in cand:
            sub = X.phi_window(cl, tphi[t])
            r = X.extend({"pt": tpt[t], "eta": teta[t], "phi": tphi[t], "z0": tz0[t], "charge": tq[t]}, sub)
            if r is not None:
                ext[t] = r[:4]
        z_ext = np.array([v[1] for v in ext.values()])
        near = z_ext[abs(z_ext - zl1) < 1.0] if len(z_ext) else z_ext
        zpv = (float(np.median(near)) if len(near) else zl1) if MODE != "otonly" else zl1
        gpt, geta, gphi = (ak.to_numpy(ev[f"GenJets_{k}"]) for k in ("pt", "eta", "phi"))
        gfl = ak.to_numpy(ev.GenJets_hadronFlavour)
        for j in np.where(sel_j)[0]:
            flav = -1
            if len(gpt):
                dr = np.hypot(geta - jeta[j], MJ.dphi(gphi, jphi[j]))
                k = np.argmin(dr)
                flav = int(gfl[k]) if dr[k] < MJ.DR_GEN else -1
            dphi_t = MJ.dphi(tphi, jphi[j])
            cone = np.where(np.hypot(teta - jeta[j], dphi_t) < MJ.DR_TRK)[0]
            dz_cut = DZ_OT if MODE == "otonly" else MJ.DZ_PV
            idx = np.array([t for t in cone if t in ext and abs(ext[t][1] - zpv) < dz_cut], int)
            nl1 = int(((tpt[cone] > PT_L1) & (abs(tz0[cone] - zl1) < 1.5)).sum())
            trk = np.zeros((NMAX, len(TRK_FEATS)), np.float32)
            n = 0
            if len(idx):
                d0 = np.array([ext[t][0] for t in idx])
                z0 = np.array([ext[t][1] for t in idx])
                chi2 = np.array([ext[t][2] for t in idx])
                sip = np.sign(d0 * np.sin(-dphi_t[idx])) * abs(d0)
                err = np.hypot(D0_ERR_OT[0], D0_ERR_OT[1] / tpt[idx]) if MODE == "otonly" else X.d0_err(tpt[idx], teta[idx])
                sig = sip / err
                order = np.argsort(-sig)[:NMAX]
                idx, sip, sig, z0, chi2 = idx[order], sip[order], sig[order], z0[order], chi2[order]
                n = len(idx)
                trk[:n] = np.stack([np.log(tpt[idx]), tpt[idx] / jpt[j], teta[idx] - jeta[j], dphi_t[idx], sip * 10.0,
                                    np.clip(sig, -50, 50), z0 - zpv, chi2, tq[idx]], axis=1)
            out["trk"].append(trk)
            out["hit"].append(np.zeros((NMAX, NHIT, len(HIT_FEATS)), np.float32))
            out["ntrk"].append(n)
            out["nl1"].append(nl1)
            out["pt"].append(jpt[j])
            out["eta"].append(jeta[j])
            out["flav"].append(flav)
            out["evt"].append(i)
            out["jidx"].append(j)
            out["lumi"].append(int(ev.luminosityBlock))
            out["event"].append(int(ev.event))
            out["scores"].append([float(ev[f"L1NGJets_score_{c}"][j]) for c in SCORES])
    return {k: np.array(v) for k, v in out.items()}


def main():
    outname, sample, files = sys.argv[1], sys.argv[2], sys.argv[3:]
    parts, offset = [], 0
    for chunk in uproot.iterate([f + ":Events" for f in files], filter_name=BRANCHES, step_size=50, library="ak"):
        p = process(chunk)
        if len(p["pt"]):
            p["evt"] = p["evt"] + offset
            parts.append(p)
        offset += len(chunk)
    cols = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
    np.savez_compressed(outname, sample=sample, trk_feats=TRK_FEATS, hit_feats=HIT_FEATS, **cols)
    print(f"{sample}: {offset} events, {len(cols['pt'])} jets, median extended tracks/jet {np.median(cols['ntrk']):.0f} "
          f"(L1 tracks/jet {np.median(cols['nl1']):.0f}) -> {outname}")


if __name__ == "__main__":
    main()

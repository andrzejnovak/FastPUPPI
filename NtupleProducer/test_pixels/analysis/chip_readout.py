#!/usr/bin/env python3
"""Pixel chips a regional (RoI) request around L1 tracks would read out, per minimum-bias crossing.

    python3 chip_readout.py chip_geom.npz OUT.npz file.root [file.root ...]
Requesting tracks and narrow windows as bits_budget.py (L1 tracks pT > 2 GeV within dR < 0.4 of L1 jets with
pT > 30, |eta| < 2.4, |z0 - z_vtx| < 1.5 cm; window +-0.8 mm r-phi x +-8 mm along z (barrel) or r (disks), l1ext.window).
A chip cannot return a window: a request returns everything the chip holds for that crossing. Per crossing with
HT > 140 this stores, for every module a window touches:
  mask  : chips whose area overlaps a window (geometric, the request), bit i = chip index i (chipgeo convention),
  nclus : clusters in each of the module's 4 chips (all clusters of the crossing),
  nwin  : window clusters in each chip (summed over tracks, as bits_budget.py's nclus_narrow).
For the calibration with the emulated chip bitstreams it also accumulates, over all crossings, the clusters per chip
and per-crossing histograms of clusters per chip for chips fully inside the cluster tables' |eta| < 2.5.
"""
import os
import sys

import awkward as ak
import numpy as np
import uproot

import chipgeo as CG
import l1ext as X
import make_jets as MJ

HT_STORE = 140.0
WIN = (0.08, 0.8, 0.8)  # narrow window: r-phi, z (barrel), r (disks) half-widths [cm]
NHIST = 400
MAXEV = int(os.environ.get("MAXEV", "0"))  # testing: stop after this many crossings

geo_path, out, files = sys.argv[1], sys.argv[2], sys.argv[3:]
G = CG.Geometry(geo_path)
RECT = G.chip_rects(np.arange(G.nmod))
FULL = G.accept >= 1.0
ALID = abs(G.lid)
REGIONS = np.unique(ALID)
by_lid = {int(l): np.where(G.lid == l)[0] for l in np.unique(G.lid)}
nout = np.einsum("ij,ij->i", G.n, G.c)
NOUT = G.n * np.sign(nout)[:, None]  # outward normals (barrel)
PHIN = np.arctan2(NOUT[:, 1], NOUT[:, 0])
DIST = abs(nout)  # distance of the barrel planes from the beam line
PHIC = np.arctan2(G.c[:, 1], G.c[:, 0])
RC = np.hypot(G.c[:, 0], G.c[:, 1])


def touched(trk):
    """Modules and chip masks whose area overlaps the narrow window of one track (all layers)."""
    hr, hz, hR = WIN
    k = X.CURV_SIGN * trk["charge"] * X.B_K / trk["pt"]
    cot = np.sinh(trk["eta"])
    mods, masks = [], []
    for lid, m in by_lid.items():
        if abs(lid) < 10:  # barrel: the track crosses each module plane at r = d / cos(phi_pred(r) - phi_n)
            r = DIST[m].copy()
            for _ in range(3):
                php = trk["phi"] - np.arcsin(np.clip(k * r / 2, -1, 1))
                dlt = X.dphi(php, PHIN[m])
                ok = abs(dlt) < 0.6
                r = DIST[m] / np.cos(np.where(ok, dlt, 0.0))
            s = 2 * np.arcsin(np.clip(k * r / 2, -1, 1)) / k if abs(k) > 1e-9 else r
            zp = trk["z0"] + cot * s
            P0 = np.stack([r * np.cos(php), r * np.sin(php), zp], 1)
            t1 = np.stack([-np.sin(php), np.cos(php), np.zeros(len(m))], 1)
            t2 = np.broadcast_to([0.0, 0.0, 1.0], P0.shape)
            h1, h2 = hr / np.cos(np.where(ok, dlt, 0.0)), hz
        else:  # disks: the track reaches the plane z = z_m at r_pred = (z_m - z0) / cot (as l1ext.window)
            if abs(cot) < 1e-3:
                continue
            zm = G.c[m, 2]
            r = (zm - trk["z0"]) / cot
            php = trk["phi"] - np.arcsin(np.clip(k * r / 2, -1, 1))
            ok = (r > 0) & (abs(r - RC[m]) < 5) & (abs(X.dphi(php, PHIC[m])) < 0.6)
            P0 = np.stack([r * np.cos(php), r * np.sin(php), zm], 1)
            t1 = np.stack([-np.sin(php), np.cos(php), np.zeros(len(m))], 1)
            t2 = np.stack([np.cos(php), np.sin(php), np.zeros(len(m))], 1)
            h1, h2 = hr, hR
        if not ok.any():
            continue
        m, P0, t1, t2 = m[ok], P0[ok], t1[ok], np.asarray(t2)[ok]
        h1 = h1[ok] if np.ndim(h1) else h1
        a0, b0, _ = G.local(P0, m)
        # window half-extent in the module's local axes (window half-vectors projected on the plane)
        ea = abs((t1 * G.e_long[m]).sum(1)) * h1 + abs((t2 * G.e_long[m]).sum(1)) * h2
        eb = abs((t1 * G.e_short[m]).sum(1)) * h1 + abs((t2 * G.e_short[m]).sum(1)) * h2
        R = RECT[m]
        ov = ((a0 - ea)[:, None] < R[:, :, 1]) & ((a0 + ea)[:, None] > R[:, :, 0]) & \
             ((b0 - eb)[:, None] < R[:, :, 3]) & ((b0 + eb)[:, None] > R[:, :, 2])
        hit = ov.any(1)
        if hit.any():
            mods.append(m[hit])
            masks.append((ov[hit] * (1 << np.arange(4))).sum(1))
    if not mods:
        return np.zeros(0, np.int64), np.zeros(0, np.int64)
    return np.concatenate(mods), np.concatenate(masks)


br = ["L1NGJets_pt", "L1NGJets_eta", "L1NGJets_phi", "L1Tracks_*", "L1TracksVtx_z0", "PixelClusters_*"]
sum_clus = np.zeros(G.nmod * 4)
hist = np.zeros((len(REGIONS), NHIST + 1))
n_events = 0
n_unassigned = 0
n_clus_total = 0
ev_rows, ev_mod, ev_mask, ev_ncl, ev_nwin = [], [], [], [], []
n_win_cl = n_win_cl_in_geo = 0
for f in files:
    for arr in uproot.iterate(f + ":Events", filter_name=br, step_size=50):
        for e in arr:
            if MAXEV and n_events >= MAXEV:
                break
            n_events += 1
            cl = X.clusters_of(e)
            p = np.stack([cl["x"], cl["y"], cl["z"]], 1)
            mod, chip, okc, *_ = G.assign(p, cl["lid"])
            n_unassigned += int((~okc).sum())
            n_clus_total += len(okc)
            uid = np.where(mod >= 0, mod * 4 + chip, 0)
            cnt = np.bincount(uid, minlength=G.nmod * 4).astype(float)
            sum_clus += cnt
            cm = cnt.reshape(-1, 4)
            for i, reg in enumerate(REGIONS):  # clusters per chip per crossing, chips fully in acceptance
                sel = (ALID == reg)[:, None] & FULL
                hist[i] += np.bincount(np.minimum(cm[sel], NHIST).astype(int), minlength=NHIST + 1)
            jpt, jeta, jphi = (ak.to_numpy(e[f"L1NGJets_{k}"]) for k in ("pt", "eta", "phi"))
            js = (jpt > 30) & (abs(jeta) < 2.4)
            ht = float(jpt[js].sum())
            if ht <= HT_STORE:
                continue
            tpt, teta, tphi, tz0, tq = (ak.to_numpy(e[f"L1Tracks_{k}"]) for k in ("pt", "eta", "phi", "z0", "charge"))
            zl1 = float(e.L1TracksVtx_z0[0]) if len(e.L1TracksVtx_z0) else 0.0
            inc = np.zeros(len(tpt), bool)
            for j in np.where(js)[0]:
                inc |= np.hypot(teta - jeta[j], MJ.dphi(tphi, jphi[j])) < 0.4
            req = np.where(inc & (tpt > 2) & (abs(tz0 - zl1) < 1.5))[0]
            X.WIN_RPHI, X.WIN_Z, X.WIN_R = WIN
            cl["idx"] = np.arange(len(cl["x"]))
            cls = X.sort_phi(cl)
            gm, gk, wins = [], [], []
            for t in req:
                trk = {"pt": tpt[t], "eta": teta[t], "phi": tphi[t], "z0": tz0[t], "charge": tq[t]}
                m_, k_ = touched(trk)
                gm.append(m_)
                gk.append(k_)
                sub = X.phi_window(cls, tphi[t])
                idx = X.window(trk, sub)[0]
                wins.append(sub["idx"][idx])
            gm = np.concatenate(gm) if gm else np.zeros(0, np.int64)
            gk = np.concatenate(gk) if gk else np.zeros(0, np.int64)
            wcl = np.concatenate(wins) if wins else np.zeros(0, np.int64)
            wuid = uid[wcl]
            # per module: OR of the chip masks over tracks
            mods = np.unique(np.concatenate([gm, wuid // 4]))
            mask = np.zeros(len(mods), np.int64)
            np.bitwise_or.at(mask, np.searchsorted(mods, gm), gk)
            nwin = np.zeros((len(mods), 4), np.int64)
            np.add.at(nwin, (np.searchsorted(mods, wuid // 4), wuid % 4), 1)
            inwin = (mask[np.searchsorted(mods, wuid // 4)] >> (wuid % 4)) & 1
            n_win_cl += len(wuid)
            n_win_cl_in_geo += int(inwin.sum())
            ev_rows.append((ht, js.sum(), len(req), len(cl["x"]), len(wcl), len(np.unique(wcl)), len(mods)))
            ev_mod.append(mods)
            ev_mask.append(mask)
            ev_ncl.append(cm[mods])
            ev_nwin.append(nwin)
rows = np.array(ev_rows, dtype=float).reshape(-1, 7)
off = np.concatenate([[0], np.cumsum([len(m) for m in ev_mod])])
cat = lambda L, shape: np.concatenate(L) if L else np.zeros(shape)
np.savez_compressed(out, rows=rows, row_cols=np.array(["ht", "njet", "ntrk_req", "nclus_event", "nwin_sum", "nwin_union", "nmod"]),
                    offsets=off, mod=cat(ev_mod, (0,)).astype(np.int32), mask=cat(ev_mask, (0,)).astype(np.uint8),
                    nclus=cat(ev_ncl, (0, 4)).astype(np.int32), nwin=cat(ev_nwin, (0, 4)).astype(np.int32),
                    sum_clus=sum_clus, n_events=n_events, hist=hist, regions=REGIONS,
                    n_unassigned=n_unassigned, n_clus_total=n_clus_total,
                    n_win_cl=n_win_cl, n_win_cl_in_geo=n_win_cl_in_geo, files=np.array(files))
print(f"{n_events} events, {len(rows)} with HT > {HT_STORE}; clusters not inside a module {n_unassigned / max(n_clus_total, 1):.2e}; "
      f"window clusters on a geometrically touched chip {n_win_cl_in_geo / max(n_win_cl, 1):.4f}")

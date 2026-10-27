#!/usr/bin/env python3
"""Emulation of L1 tracks extended into the pixel detector: pick up pixel clusters along each L1 track, refit d0, z0.

For one L1 track (Outer Tracker track finder, 4-parameter fit: pT, phi0, eta, z0; d0 = 0 by construction):
  1. Predict the crossing with every pixel layer (4 barrel layers, 6 forward disks per side) from the L1 helix.
  2. Candidate clusters per layer: within a window in r-phi (WIN_RPHI) and along the track (WIN_Z barrel, WIN_R disks).
     The window is wide enough for b-hadron displacements (r-phi shift ~ d0) and the L1 z0 resolution.
  3. Keep the NBEST closest candidates per layer, try every combination of one cluster (or none) per layer with
     at least MIN_HITS clusters, fit each, and keep the combination with the lowest chi2 / ndof.
  4. Fit (curvature fixed to the L1 value; the pixel lever arm adds little there):
       r-phi: r_i (Phi_i + asin(k r_i / 2)) = r_i phi0 + d0           (linear in phi0, d0; small-d0 helix)
       r-z  : z_i = z0 + cot(theta) s_i, s_i = (2 / k) asin(k r_i / 2)  (linear in z0, cot(theta))
     with the L1 cot(theta) as a soft constraint so that two hits suffice.
d0 follows the CMS dxy sign convention (dxy = -x sin(phi) + y cos(phi) at the point of closest approach).
Its uncertainty is a pT and eta parametrisation of the HLT pixel track dxy errors (same detector and hits),
see D0_ERR; set by calibrate_err().
"""
import os

import numpy as np

B_K = 0.01143  # |curvature| [1/cm] = B_K / pT[GeV] (3.81 T)
SIG_RPHI, SIG_Z, SIG_R = 0.0010, 0.0025, 0.0025  # cluster resolution [cm]: r-phi, z (barrel), r (disks)
WIN_RPHI, WIN_Z, WIN_R = 0.15, float(os.environ.get("WIN_Z", 1.5)), 1.5  # candidate windows [cm]
NBEST, MIN_HITS = 3, int(os.environ.get("MIN_HITS", 2))  # MIN_HITS=1: one-hit extension (L1 phi0 fixes the line)
MISS_PENALTY = 2.0  # added to chi2/ndof per pixel layer with candidates but no hit used
MAX_LAYERS = 4  # only the innermost layers with candidates enter the combinatorics (they set d0)
PHI_WIN = 0.12  # [rad] cluster preselection around the track direction (bending to r = 16 cm at 2 GeV: 0.05)
COT_SIG = 0.01  # soft constraint on cot(theta) from the L1 track
D0_ERR = (0.0088, 0.0139)  # d0 uncertainty [cm] = hypot(a, b / (pT sqrt(sin theta))), fit to HLT pixel track dxyErr
CURV_SIGN = 1  # sign of the curvature relative to the L1 charge (checked against HLT pixel tracks: -1 gives 31% purity)


def dphi(a, b):
    return (a - b + np.pi) % (2 * np.pi) - np.pi


def layers(subdet, layer):
    """Unique layer id: barrel 1-4, disks 11-16 (+z) and -11..-16 (-z, sign set by the caller from z)."""
    return np.where(subdet == 1, layer, 10 + layer)


def fit(r, phi, z, barrel, k, phi0_l1, cot_l1):
    """Least-squares helix fit of a few pixel clusters. Returns d0, z0, chi2/ndof, phi0."""
    a = np.arcsin(np.clip(k * r / 2, -1, 1))
    ph = phi0_l1 + dphi(phi, phi0_l1)
    y = r * (ph + a)
    w = 1 / SIG_RPHI**2
    A = np.column_stack([r, np.ones_like(r)])
    cov = np.linalg.inv(A.T @ A * w + np.diag([1e-12, 1e-12]))
    phi0, d0 = cov @ (A.T @ y * w)
    res_rphi = y - A @ np.array([phi0, d0])
    s = np.where(abs(k) > 1e-9, 2 * a / np.where(abs(k) > 1e-9, k, 1), r)
    sz = np.where(barrel, SIG_Z, SIG_R * abs(cot_l1) + 1e-4)
    Az = np.column_stack([np.ones_like(s), s])
    wz = 1 / sz**2
    M = (Az.T * wz) @ Az + np.diag([0.0, 1 / COT_SIG**2])
    bz = (Az.T * wz) @ z + np.array([0.0, cot_l1 / COT_SIG**2])
    z0, cot = np.linalg.solve(M, bz)
    res_z = z - Az @ np.array([z0, cot])
    chi2 = (res_rphi**2).sum() * w + (res_z**2 * wz).sum() + ((cot - cot_l1) / COT_SIG) ** 2
    ndof = max(2 * len(r) - 3, 1)
    return d0, z0, chi2 / ndof, phi0


def window(trk, cl):
    """Clusters inside the search window of an L1 track: indices, and the prediction residuals used to rank them."""
    k = CURV_SIGN * trk["charge"] * B_K / trk["pt"]
    cot = np.sinh(trk["eta"])
    # prediction at each cluster's radius (barrel) or z (disk)
    r, z = cl["r"], cl["z"]
    barrel = abs(cl["lid"]) < 10
    s_r = 2 * np.arcsin(np.clip(k * r / 2, -1, 1)) / k if abs(k) > 1e-9 else r
    z_pred = trk["z0"] + cot * s_r
    phi_pred = trk["phi"] - np.arcsin(np.clip(k * r / 2, -1, 1))
    rphi = r * dphi(cl["phi"], phi_pred)
    # disks: the radius where the track reaches the cluster's z (small-curvature approximation)
    r_pred = np.where(abs(cot) > 1e-3, (z - trk["z0"]) / np.where(abs(cot) > 1e-3, cot, 1), -1.0)
    along = np.where(barrel, abs(z - z_pred) < WIN_Z, abs(r - r_pred) < WIN_R)
    cand = np.where((abs(rphi) < WIN_RPHI) & along)[0]
    return cand, k, cot, barrel, rphi, z_pred, r_pred


def extend(trk, cl):
    """trk: dict of one L1 track (pt, eta, phi, z0, charge). cl: dict of cluster arrays (x, y, z, r, phi, lid).
    Returns (d0, z0, chi2ndof, nhits, cluster indices) or None if fewer than MIN_HITS clusters fit."""
    cand, k, cot, barrel, rphi, z_pred, r_pred = window(trk, cl)
    r, z = cl["r"], cl["z"]
    if len(cand) < MIN_HITS:
        return None
    per_layer = []
    for lid in np.unique(cl["lid"][cand]):
        c = cand[cl["lid"][cand] == lid]
        score = (rphi[c] / WIN_RPHI) ** 2 + (np.where(barrel[c], z[c] - z_pred[c], r[c] - r_pred[c]) / WIN_Z) ** 2
        per_layer.append(c[np.argsort(score)[:NBEST]])
    per_layer.sort(key=lambda c: r[c].mean())
    per_layer = per_layer[:MAX_LAYERS]
    # all combinations of one candidate or none (-1) per layer, as an index matrix
    grids = np.meshgrid(*[np.append(c, -1) for c in per_layer], indexing="ij")
    combo = np.stack([g.ravel() for g in grids], axis=1)
    m = combo >= 0
    nh = m.sum(1)
    combo, m, nh = combo[nh >= MIN_HITS], m[nh >= MIN_HITS], nh[nh >= MIN_HITS]
    if not len(combo):
        return None
    ix = np.where(m, combo, 0)
    rr, zz, bb = r[ix], z[ix], barrel[ix]
    aa = np.arcsin(np.clip(k * rr / 2, -1, 1))
    y = rr * (trk["phi"] + dphi(cl["phi"][ix], trk["phi"]) + aa)
    # r-phi: weighted line y = r phi0 + d0 (equal weights), closed form
    S, Sr, Srr = nh, (m * rr).sum(1), (m * rr * rr).sum(1)
    Sy, Sry = (m * y).sum(1), (m * rr * y).sum(1)
    det = S * Srr - Sr**2
    det = np.where(det > 1e-9, det, 1e-9)
    phi0 = (S * Sry - Sr * Sy) / det
    d0 = (Srr * Sy - Sr * Sry) / det
    one = nh == 1  # one hit: phi0 from the L1 track, d0 = the hit's r-phi offset from that line
    if one.any():
        phi0 = np.where(one, trk["phi"], phi0)
        d0 = np.where(one, Sy - Sr * trk["phi"], d0)
    chi2 = (m * (y - rr * phi0[:, None] - d0[:, None]) ** 2).sum(1) / SIG_RPHI**2
    # r-z: z = z0 + cot s with a soft constraint on cot from the L1 track
    ss = np.where(abs(k) > 1e-9, 2 * aa / (k if abs(k) > 1e-9 else 1.0), rr)
    wz = m / np.where(bb, SIG_Z, SIG_R * abs(cot) + 1e-4) ** 2
    c2 = 1 / COT_SIG**2
    A11, A12, A22 = wz.sum(1), (wz * ss).sum(1), (wz * ss * ss).sum(1) + c2
    b1, b2 = (wz * zz).sum(1), (wz * ss * zz).sum(1) + cot * c2
    dz = A11 * A22 - A12**2
    z0 = (A22 * b1 - A12 * b2) / dz
    cc = (A11 * b2 - A12 * b1) / dz
    chi2 = chi2 + (wz * (zz - z0[:, None] - cc[:, None] * ss) ** 2).sum(1) + (cc - cot) ** 2 * c2
    chi2n = chi2 / np.maximum(2 * nh - 3, 1)
    # prefer more hits at similar quality: penalise each missing layer
    b = np.argmin(chi2n + MISS_PENALTY * (len(per_layer) - nh))
    return d0[b], z0[b], chi2n[b], int(nh[b]), combo[b][m[b]]


def d0_err(pt, eta):
    a, b = D0_ERR
    sin_t = 1 / np.cosh(eta)
    return np.hypot(a, b / (pt * np.sqrt(sin_t)))


SKIP_LIDS = {int(x) for x in os.environ.get("SKIP_LIDS", "").split(",") if x}  # e.g. "1": drop barrel layer 1 (readout study)
KEEP_LIDS = {int(x) for x in os.environ.get("KEEP_LIDS", "").split(",") if x}  # e.g. "1": barrel layer 1 only (replacement-layer study)
HIT_LOSS = float(os.environ.get("HIT_LOSS", "0"))  # fraction of pixel clusters dropped at random (robustness study)


def clusters_of(ev, prefix="PixelClusters"):
    x, y, z = (np.asarray(ev[f"{prefix}_{c}"], float) for c in "xyz")
    sub, lay = np.asarray(ev[f"{prefix}_subdet"]), np.asarray(ev[f"{prefix}_layer"])
    lid = layers(sub, lay) * np.where((sub != 1) & (z < 0), -1, 1)
    cl = {"x": x, "y": y, "z": z, "r": np.hypot(x, y), "phi": np.arctan2(y, x), "lid": lid,
          "trk": np.asarray(ev[f"{prefix}_trkIdx"])}
    keep = ~np.isin(lid, list(SKIP_LIDS)) if SKIP_LIDS else np.ones(len(x), bool)
    if KEEP_LIDS:
        keep &= np.isin(abs(lid), list(KEEP_LIDS))
    if HIT_LOSS > 0:  # random cluster loss (chip inefficiency, buffer overflow); reproducible per event
        keep &= np.random.default_rng(int(abs(x).sum() * 1e4) % 2**32).random(len(x)) >= HIT_LOSS
    return cl if keep.all() else subset(cl, keep)


def subset(cl, m):
    return {k: v[m] for k, v in cl.items()}


def sort_phi(cl):
    """Clusters sorted in phi, for phi_window."""
    return subset(cl, np.argsort(cl["phi"]))


def phi_window(cl, phi, half=None):
    """Clusters (sorted with sort_phi) within +-half of phi, handling the wrap at +-pi."""
    half = PHI_WIN if half is None else half
    p = cl["phi"]
    lo, hi = phi - half, phi + half
    sel = [np.arange(np.searchsorted(p, max(lo, -np.pi)), np.searchsorted(p, min(hi, np.pi)))]
    if lo < -np.pi:
        sel.append(np.arange(np.searchsorted(p, lo + 2 * np.pi), len(p)))
    if hi > np.pi:
        sel.append(np.arange(0, np.searchsorted(p, hi - 2 * np.pi)))
    return subset(cl, np.concatenate(sel))

#!/usr/bin/env python3
"""Pixel summaries v2: calibrated transverse + longitudinal impact parameters (3D significance) for the b summary and
the charm word. Same inputs as charm_feats.py (per-jet track lists of make_l1ext_lists.py / make_lists.py).

Why: the lists store the transverse significance with the l1ext.D0_ERR parametrisation (fit to HLT pixel track dxyErr,
88 um floor), but the core resolution of the L1-track pixel refit is 20-90 um (pull width ~0.3 at high pT), and the
refit z0 (30-500 um) is not used at all by the v1 summaries. Charm lives at small displacements, so both matter.

Resolution: lookup table in (track pT, |eta|), the 68.3% quantile of |IP| of tracks on the NEGATIVE side (resolution-
dominated, no flavour label used), measured on minimum-bias jets (lists_l1ext_MinBiasSel.npz, ~150k tracks per view;
QCD jets give the same within ~10%, HH->4b jets are broadened by b tracks). A firmware LUT of 6 x 5 entries per view.
Signed longitudinal IP: a track from a vertex at transverse flight distance L along direction (phi_u, eta_u) has
d0 = L sin(phi_u - phi) and dz = z0 - z_PV = L (sinh eta_u - sinh eta); with the jet as flight direction,
szip = sign(-dz * deta) |dz|. 3D significance s3 = sign(sxy + sz) sqrt(sxy^2 + sz^2).
Vertex: L from the weighted least squares of both views of the displaced tracks (s3 > SIG_VTX, up to NVTX), with the
flight direction = momentum sum of those tracks.
"""
import numpy as np

M_PI = 0.13957
PT_EDGES = np.array([2, 3, 4, 6, 10, 20])  # lower edges [GeV]
ETA_EDGES = np.array([0, 0.5, 1.0, 1.5, 2.0])  # lower edges of |eta|
SIG_XY_UM = np.array([[46.4, 48.5, 67.9, 84.9, 80.0], [34.9, 35.6, 44.2, 56.9, 57.2], [27.7, 29.8, 34.1, 39.7, 42.8],
                      [22.8, 23.7, 26.6, 27.0, 29.2], [20.2, 19.5, 21.2, 20.2, 22.5], [19.3, 17.1, 18.5, 19.1, 17.4]])
SIG_Z_UM = np.array([[73.7, 90.8, 193.7, 364.1, 552.0], [57.6, 59.3, 115.6, 232.9, 429.5], [47.9, 48.9, 87.4, 163.3, 316.5],
                     [40.0, 37.9, 67.8, 114.5, 241.8], [37.6, 34.3, 56.3, 98.5, 184.4], [34.8, 32.1, 47.2, 92.8, 194.3]])

# b-oriented summary v2 (as train_sets.summary_features, with s3): 8 x 8 bits
SUMMARY2 = ["s3_1", "s3_2", "s3_3", "ntrk", "n_s3_gt3", "n_s3_gt5", "sum_s3_pos", "max_sip_mm"]
SUMMARY2_Q = [(-16, 15.875, 0.125)] * 3 + [(0, 255, 1)] * 3 + [(0, 127.5, 0.5), (-2.56, 2.54, 0.02)]
CHARM2_WORD = [
    ("n_s3_1_3", 4, (0, 15, 1)), ("n_s3_2_5", 4, (0, 15, 1)), ("n_s3_neg2", 3, (0, 7, 1)),
    ("m_vtx", 8, (0, 6.375, 0.025)), ("m_2trk", 7, (0, 6.35, 0.05)),
    ("fpt_disp_jet", 6, (0, 1.575, 0.025)), ("fpt_disp_trk", 6, (0, 1.0, 1 / 63)),
    ("lxy", 9, (-25.6, 25.5, 0.1)), ("lxy_sig", 8, (-16, 15.875, 0.125)), ("q_vtx", 3, (-3, 3, 1)), ("n_disp", 3, (0, 7, 1)),
]
CHARM2_NAMES = [n for n, _, _ in CHARM2_WORD]
CHARM2_BITS = sum(b for _, b, _ in CHARM2_WORD)


def lut(table, pt, aeta):
    i = np.clip(np.searchsorted(PT_EDGES, pt, side="right") - 1, 0, len(PT_EDGES) - 1)
    j = np.clip(np.searchsorted(ETA_EDGES, aeta, side="right") - 1, 0, len(ETA_EDGES) - 1)
    return table[i, j]


def track_views(trk, ntrk, jet_eta):
    k = trk.shape[1]
    valid = np.arange(k)[None, :] < ntrk[:, None]
    pt = np.where(valid, np.exp(trk[:, :, 0]), 1.0)
    deta = trk[:, :, 2]
    eta = jet_eta[:, None] + deta
    sip = np.where(valid, trk[:, :, 4], 0.0)  # mm
    dz = np.where(valid, trk[:, :, 6] * 10.0, 0.0)  # mm
    exy = lut(SIG_XY_UM, pt, abs(eta)) * 1e-3
    ez = lut(SIG_Z_UM, pt, abs(eta)) * 1e-3
    sxy = sip / exy
    sz = np.sign(-dz * deta) * abs(dz) / ez
    s3 = np.sign(sxy + sz) * np.hypot(sxy, sz)
    s3 = np.where(valid, s3, -99.0)
    return dict(valid=valid, pt=np.where(valid, pt, 0.0), eta=eta, dphi=trk[:, :, 3], sip=sip, dz=dz, exy=exy, ez=ez,
                sxy=sxy, sz=sz, s3=s3, q=np.where(valid, trk[:, :, 8], 0.0))


def summary2(trk, ntrk, jet_eta):
    t = track_views(trk, ntrk, jet_eta)
    s3 = np.clip(t["s3"], -50, 50)
    s3 = np.where(t["valid"], s3, -50.0)
    top = np.sort(s3, axis=1)[:, ::-1][:, :3]
    sipm = np.where(t["valid"], t["sip"], -1.0)
    return np.column_stack([top, ntrk, (s3 > 3).sum(1), (s3 > 5).sum(1), np.where(s3 > 0, s3, 0).sum(1), sipm.max(1)]).astype(np.float32)


def charm2(trk, ntrk, jet_eta, jet_pt, sig_vtx=3.0, nvtx=3):
    t = track_views(trk, ntrk, jet_eta)
    valid, s3, pt, eta, dph = t["valid"], t["s3"], t["pt"], t["eta"], t["dphi"]
    # displaced tracks, most significant first (the lists are ordered by the v1 significance: re-sort)
    order = np.argsort(-s3, axis=1)
    take = lambda a: np.take_along_axis(a, order, axis=1)
    s3, pt, eta, dph, valid = take(s3), take(pt), take(eta), take(dph), take(valid)
    sip, dz, exy, ez, q, sxy = take(t["sip"]), take(t["dz"]), take(t["exy"]), take(t["ez"]), take(t["q"]), take(t["sxy"])
    k = trk.shape[1]
    disp = valid & (s3 > sig_vtx)
    vtx = disp & (np.cumsum(disp, axis=1) <= nvtx)
    px, py, pz = pt * np.cos(dph), pt * np.sin(dph), pt * np.sinh(eta)
    e = np.sqrt(px ** 2 + py ** 2 + pz ** 2 + M_PI ** 2)

    def mass(m):
        s = lambda x: (x * m).sum(1)
        return np.sqrt(np.maximum(s(e) ** 2 - s(px) ** 2 - s(py) ** 2 - s(pz) ** 2, 0.0)) * (m.sum(1) >= 2)

    top2 = valid & (np.arange(k)[None, :] < 2) & (s3 > sig_vtx)
    spt_all, spt_disp = pt.sum(1), (pt * disp).sum(1)
    # flight distance from both views, direction = momentum sum of the vertex tracks
    vx, vy, vz = (px * vtx).sum(1), (py * vtx).sum(1), (pz * vtx).sum(1)
    phi_u = np.arctan2(vy, vx)
    sh_u = vz / np.maximum(np.hypot(vx, vy), 1e-6)  # sinh(eta_u) = pz / pT
    d0 = -sip * np.sign(np.sin(dph))
    a_xy = np.sin(phi_u[:, None] - dph)
    a_z = sh_u[:, None] - np.sinh(eta)
    w_xy, w_z = np.where(vtx, 1 / exy ** 2, 0.0), np.where(vtx, 1 / ez ** 2, 0.0)
    den = (w_xy * a_xy ** 2 + w_z * a_z ** 2).sum(1)
    good = (vtx.sum(1) >= 2) & (den > 0)
    L = np.where(good, (w_xy * d0 * a_xy + w_z * dz * a_z).sum(1) / np.where(good, den, 1.0), 0.0)
    feats = {
        "n_s3_1_3": (valid & (s3 > 1) & (s3 < 3)).sum(1), "n_s3_2_5": (valid & (s3 > 2) & (s3 < 5)).sum(1),
        "n_s3_neg2": (valid & (s3 < -2)).sum(1), "m_vtx": mass(vtx), "m_2trk": mass(top2) * (top2.sum(1) == 2),
        "fpt_disp_jet": spt_disp / jet_pt, "fpt_disp_trk": np.where(spt_all > 0, spt_disp / np.maximum(spt_all, 1e-6), 0.0),
        "lxy": np.clip(L, -25.6, 25.5), "lxy_sig": np.where(good, np.clip(L * np.sqrt(den), -16, 15.875), 0.0),
        "q_vtx": (q * vtx).sum(1), "n_disp": disp.sum(1),
    }
    return np.column_stack([feats[n] for n in CHARM2_NAMES]).astype(np.float32)


def quantize(x, spec):
    q = x.copy()
    for i, (lo, hi, step) in enumerate(spec):
        q[:, i] = np.clip(np.floor(q[:, i] / step + 1e-6) * step, lo, hi)
    return q


def quantize_summary2(x):
    return quantize(x, SUMMARY2_Q)


def quantize_charm2(x):
    return quantize(x, [r for _, _, r in CHARM2_WORD])


# single 64-bit word v2: top-3 s3 at 6 b (-8..7.75, 0.25), ntrk 4, n(s3>3) 3, sum(s3>0) 6 (0..63), max sip 6
# (-0.64..0.62 mm), n(1<s3<3) 3, n(s3<-2) 2, m_vtx 7 (0..6.35, 50 MeV), fpt_disp_jet 5, lxy_sig 6, q_vtx 2 = 62 b
WORD64_2 = [("b", 0, -8, 7.75, 0.25), ("b", 1, -8, 7.75, 0.25), ("b", 2, -8, 7.75, 0.25), ("b", 3, 0, 15, 1), ("b", 4, 0, 7, 1),
            ("b", 6, 0, 63, 1), ("b", 7, -0.64, 0.62, 0.02),
            ("c", CHARM2_NAMES.index("n_s3_1_3"), 0, 7, 1), ("c", CHARM2_NAMES.index("n_s3_neg2"), 0, 3, 1),
            ("c", CHARM2_NAMES.index("m_vtx"), 0, 6.35, 0.05), ("c", CHARM2_NAMES.index("fpt_disp_jet"), 0, 1.55, 0.05),
            ("c", CHARM2_NAMES.index("lxy_sig"), -8, 7.75, 0.25), ("c", CHARM2_NAMES.index("q_vtx"), -2, 1, 1)]
WORD64_2_BITS = 62


def word64_2(summ, charm):
    cols = [np.clip(np.floor((summ if s == "b" else charm)[:, i] / st + 1e-6) * st, lo, hi) for s, i, lo, hi, st in WORD64_2]
    return np.column_stack(cols).astype(np.float32)

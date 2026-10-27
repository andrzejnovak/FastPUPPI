#!/usr/bin/env python3
"""Charm-oriented per-jet pixel summary, computed from the per-jet track lists (make_l1ext_lists.py / make_lists.py).

The b-oriented 8-number summary (train_sets.summary_features) looks at the few most displaced tracks; charm hadrons
fly ~3x less (D0 c*tau 123 um, D+ 312 um) and decay to 2-3 tracks with a vertex mass below ~1.9 GeV, so their tracks sit
at 1-5 sigma (the pixel-refit d0 error is >= 88 um). The charm word adds counts at moderate significance, a vertex
mass, displaced-pT fractions, a crude transverse vertex and the vertex charge.

Inputs per jet: trk (N, 16, 9) with TRK_FEATS = logpt, ptrel, deta, dphi, sip [mm], sipsig, dzpv [cm], chi2ndof,
charge; tracks ordered by decreasing signed IP significance; ntrk; jet eta and pT.

Transverse geometry, in the jet frame (jet axis along x): a track with azimuth dphi relative to the jet and CMS-convention
d0 is the straight line n.v = d0, n = (-sin dphi, cos dphi) (straight lines: R >= 175 cm at pT 2 GeV vs mm decay
lengths). The stored sip = sign(d0 sin(-dphi)) |d0| gives d0 = -sip * sign(sin dphi). A free two-line intersection is
ill-conditioned (opening angles ~0.1 rad, d0 errors >= 88 um), so the vertex is constrained to lie on the line from the
beam along the momentum sum u of the vertex tracks (>= 2 tracks with sig > SIG_VTX, up to NVTX): v = L u, and the
weighted (w = 1/err^2, err = sip / sig) least-squares L = sum w d0 s / sum w s^2, s_i = sin(phi_u - phi_i),
sigma_L = 1/sqrt(sum w s^2). Lxy = L, signed; fewer than two displaced tracks: Lxy = 0, sig = 0.

CHARM_WORD lists the features in the assumed 64-bit charm word and their bit widths (quantize_charm).
"""
import numpy as np

M_PI = 0.13957
SIG_VTX = 2.0  # IP significance threshold for "displaced" tracks entering mass, pT fraction, charge, vertex
NVTX = 3  # at most this many (most significant) displaced tracks enter the vertex mass and fit
D0_ERR = (0.0088, 0.0139)  # l1ext.D0_ERR [cm], fallback when the stored significance is clipped or zero

# name, bits, quantisation (lo, hi, step); counts saturate
CHARM_WORD = [
    ("n_sig_1_3", 4, (0, 15, 1)),  # tracks with 1 < sig < 3
    ("n_sig_2_5", 4, (0, 15, 1)),  # tracks with 2 < sig < 5
    ("n_sig_neg2", 3, (0, 7, 1)),  # tracks with sig < -2 (resolution tails, fakes: a light-jet handle)
    ("m_vtx", 8, (0, 6.375, 0.025)),  # invariant mass of up to NVTX displaced tracks, pion hypothesis [GeV]
    ("m_2trk", 7, (0, 6.35, 0.05)),  # mass of the two most significant tracks if both displaced [GeV]
    ("fpt_disp_jet", 6, (0, 1.575, 0.025)),  # sum pT(displaced) / jet pT
    ("fpt_disp_trk", 6, (0, 1.0, 1 / 63)),  # sum pT(displaced) / sum pT(all listed tracks)
    ("lxy", 9, (-25.6, 25.5, 0.1)),  # transverse flight distance along the vertex direction [mm]
    ("lxy_sig", 8, (-16, 15.875, 0.125)),  # Lxy / sigma(Lxy)
    ("q_vtx", 3, (-3, 3, 1)),  # charge sum of the displaced tracks entering the vertex
    ("n_disp", 3, (0, 7, 1)),  # number of displaced tracks (sig > SIG_VTX)
]
CHARM_NAMES = [n for n, _, _ in CHARM_WORD]
CHARM_BITS = sum(b for _, b, _ in CHARM_WORD)


def charm_features(trk, ntrk, jet_eta, jet_pt):
    n, k = trk.shape[:2]
    valid = np.arange(k)[None, :] < ntrk[:, None]
    sig = np.where(valid, trk[:, :, 5], -99.0)
    sip = np.where(valid, trk[:, :, 4], 0.0)  # mm
    pt = np.where(valid, np.exp(trk[:, :, 0]), 0.0)
    eta = jet_eta[:, None] + trk[:, :, 2]
    dph = trk[:, :, 3]
    q = np.where(valid, trk[:, :, 8], 0.0)
    a, b = D0_ERR
    err_param = 10 * np.hypot(a, b / (np.maximum(pt, 1e-3) * np.sqrt(1 / np.cosh(eta))))  # mm
    ok = valid & (abs(trk[:, :, 5]) > 1e-3) & (abs(trk[:, :, 5]) < 49.9) & (abs(sip) > 1e-7)
    err = np.where(ok, sip / np.where(ok, trk[:, :, 5], 1.0), err_param)
    err = np.where(err > 1e-4, err, err_param)

    disp = valid & (sig > SIG_VTX)
    ndisp = disp.sum(1)
    rank = np.cumsum(disp, axis=1)  # tracks are ordered by decreasing sig, so displaced tracks come first
    vtx = disp & (rank <= NVTX)

    px, py, pz = pt * np.cos(dph), pt * np.sin(dph), pt * np.sinh(eta)
    e = np.sqrt(px ** 2 + py ** 2 + pz ** 2 + M_PI ** 2)

    def mass(m):
        s = lambda x: (x * m).sum(1)
        return np.sqrt(np.maximum(s(e) ** 2 - s(px) ** 2 - s(py) ** 2 - s(pz) ** 2, 0.0)) * (m.sum(1) >= 2)

    top2 = valid & (np.arange(k)[None, :] < 2) & (sig > SIG_VTX)
    spt_all = pt.sum(1)
    spt_disp = (pt * disp).sum(1)

    # transverse flight distance: displaced-track lines n_i.v = d0_i with the vertex on the line from the beam along the
    # momentum sum u of the vertex tracks (the D flight direction up to neutrals): v = L u, so d0_i = L sin(phi_u - phi_i)
    d0 = -sip * np.sign(np.sin(dph))
    phi_u = np.arctan2((py * vtx).sum(1), (px * vtx).sum(1))
    s_i = np.sin(phi_u[:, None] - dph)
    w = np.where(vtx, 1.0 / err ** 2, 0.0)
    sww = (w * s_i ** 2).sum(1)
    good = (vtx.sum(1) >= 2) & (sww > 0)
    L = np.where(good, (w * d0 * s_i).sum(1) / np.where(good, sww, 1.0), 0.0)
    lxy = np.clip(L, -25.6, 25.5)
    lxy_sig = np.where(good, np.clip(L * np.sqrt(sww), -16, 15.875), 0.0)

    feats = {
        "n_sig_1_3": (valid & (sig > 1) & (sig < 3)).sum(1),
        "n_sig_2_5": (valid & (sig > 2) & (sig < 5)).sum(1),
        "n_sig_neg2": (valid & (sig < -2)).sum(1),
        "m_vtx": mass(vtx),
        "m_2trk": mass(top2) * (top2.sum(1) == 2),
        "fpt_disp_jet": spt_disp / jet_pt,
        "fpt_disp_trk": np.where(spt_all > 0, spt_disp / np.maximum(spt_all, 1e-6), 0.0),
        "lxy": lxy,
        "lxy_sig": lxy_sig,
        "q_vtx": (q * vtx).sum(1),
        "n_disp": ndisp,
    }
    return np.column_stack([feats[nm] for nm in CHARM_NAMES]).astype(np.float32)


def quantize_charm(x):
    """Truncate to each field's step and saturate to its range, as the firmware word would carry it."""
    q = x.copy()
    for i, (_, _, (lo, hi, step)) in enumerate(CHARM_WORD):
        q[:, i] = np.clip(np.floor(q[:, i] / step + 1e-6) * step, lo, hi)
    return q


# A single 64-bit combined word (b summary + charm), for when only one word per jet is available:
# top-3 IP sig at 6 b (ap_fixed<6,4>: -8..7.75 in 0.25), n_trk 4 b, n(sig>3) 3 b, sum(sig>0) 6 b (0..63),
# max sip 6 b (-0.64..0.62 mm, 20 um), n(1<sig<3) 3 b, n(sig<-2) 2 b, m_vtx 7 b (0..6.35, 50 MeV),
# fpt_disp_jet 5 b (0..1.55, 0.05), lxy_sig 6 b (-8..7.75, 0.25), q_vtx 2 b (-2..1)  -> 18+4+3+6+6+3+2+7+5+6+2 = 62 b
WORD64 = [  # (source, column, lo, hi, step)
    ("b", 0, -8, 7.75, 0.25), ("b", 1, -8, 7.75, 0.25), ("b", 2, -8, 7.75, 0.25), ("b", 3, 0, 15, 1), ("b", 4, 0, 7, 1),
    ("b", 6, 0, 63, 1), ("b", 7, -0.64, 0.62, 0.02),
    ("c", CHARM_NAMES.index("n_sig_1_3"), 0, 7, 1), ("c", CHARM_NAMES.index("n_sig_neg2"), 0, 3, 1),
    ("c", CHARM_NAMES.index("m_vtx"), 0, 6.35, 0.05), ("c", CHARM_NAMES.index("fpt_disp_jet"), 0, 1.55, 0.05),
    ("c", CHARM_NAMES.index("lxy_sig"), -8, 7.75, 0.25), ("c", CHARM_NAMES.index("q_vtx"), -2, 1, 1),
]
WORD64_BITS = 6 * 3 + 4 + 3 + 6 + 6 + 3 + 2 + 7 + 5 + 6 + 2


def word64(summ, charm):
    cols = []
    for src, i, lo, hi, step in WORD64:
        x = (summ if src == "b" else charm)[:, i]
        cols.append(np.clip(np.floor(x / step + 1e-6) * step, lo, hi))
    return np.column_stack(cols).astype(np.float32)

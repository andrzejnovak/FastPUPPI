#!/usr/bin/env python3
"""Inner Tracker module and chip (CROC) geometry learned from the ntuples, and point -> module / chip assignment.

The ntuple clusters carry global positions but no detId; the hits on HLT pixel tracks (PixelHits_*) carry both.
chip_geom.py learns, per detId, the sensor plane (centroid + PCA normal of its hits) and the in-plane extent along
two axes (barrel: r-phi and z; disks: radial and r-phi at the module centre), and from the extent the chip layout:
an axis longer than 25 mm holds 2 chips (CROC 16.8 mm x 21.6 mm; 2x2 quad module 33.6 x 43.2 mm,
1x2 module 16.8 x 43.2 mm). Chip index as in CMSSW's Phase2ITQCoreProducer (splitByChip): bit 0 = second half of the
long (column) axis, bit 1 = second half of the short (row) axis. Which end of each axis is "second" is a convention
(the emulator's local row / column directions are not known here); only the partition matters for the readout.

Layer key (lid) as l1ext.layers: barrel 1-4, disks +-(10 + disk) by the sign of z.
"""
import numpy as np
from scipy.spatial import cKDTree

GEOM = "/scratch/submit/cms/novaka/l1pixels/derived/chip_readout/chip_geom.npz"
TWO_CHIP = 2.5  # [cm] an in-plane extent above this holds 2 chips along that axis


def lid_of(subdet, layer, z):
    lid = np.where(subdet == 1, layer, 10 + layer)
    return lid * np.where((subdet != 1) & (z < 0), -1, 1)


def decode(detid):
    """subdet, layer/disk from a Phase-2 pixel raw detId (TrackerTopology bit layout)."""
    detid = np.asarray(detid, np.int64)
    sub = (detid >> 25) & 7
    lay = np.where(sub == 1, (detid >> 20) & 0xF, (detid >> 18) & 0xF)
    return sub, lay


def inplane_axes(c, n, barrel):
    """Provisional in-plane axes a1, a2: barrel a2 = z projected on the plane; disks a1 = radial projected."""
    n = n / np.linalg.norm(n, axis=-1, keepdims=True)
    zhat = np.broadcast_to([0.0, 0.0, 1.0], c.shape)
    rad = np.stack([c[:, 0], c[:, 1], np.zeros(len(c))], 1)
    rad = rad / np.linalg.norm(rad, axis=1, keepdims=True)
    ref = np.where(barrel[:, None], zhat, rad)
    ref = ref - (ref * n).sum(1, keepdims=True) * n
    ref /= np.linalg.norm(ref, axis=1, keepdims=True)
    other = np.cross(n, ref)
    a1 = np.where(barrel[:, None], other, ref)
    a2 = np.where(barrel[:, None], ref, other)
    return a1, a2


class Geometry:
    """Module table (one row per detId seen) with chip layout; assign(points) -> module, chip, local coordinates."""

    def __init__(self, path=GEOM):
        g = np.load(path)
        self.__dict__.update({k: g[k] for k in g.files})
        self.nmod = len(self.detid)
        self.trees = {}
        for lid in np.unique(self.lid):
            idx = np.where(self.lid == lid)[0]
            self.trees[int(lid)] = (idx, cKDTree(self.c[idx]))

    def local(self, p, m):
        d = p - self.c[m]
        return (d * self.e_long[m]).sum(-1), (d * self.e_short[m]).sum(-1), (d * self.n[m]).sum(-1)

    def chip_of(self, m, a, b):
        return ((self.n_long[m] == 2) & (a > 0)).astype(np.int64) + 2 * ((self.n_short[m] == 2) & (b > 0))

    def assign(self, p, lid, k=8, tol=0.05, wtol=0.1):
        """Nearest module plane containing each point (same layer key). Returns module index, chip index, ok flag
        (inside the sensor within tol and within wtol of the plane), and the local coordinates."""
        n = len(p)
        mod = np.full(n, -1, np.int64)
        out = np.zeros(n, bool)
        A, B, W = np.zeros(n), np.zeros(n), np.zeros(n)
        for l in np.unique(lid):
            sel = np.where(lid == l)[0]
            if int(l) not in self.trees:
                continue
            idx, tree = self.trees[int(l)]
            kk = min(k, len(idx))
            _, j = tree.query(p[sel], k=kk)
            j = idx[j.reshape(len(sel), kk)]
            a, b, w = self.local(p[sel][:, None, :], j)
            excess = np.maximum(abs(a) - self.L_long[j] / 2, 0) + np.maximum(abs(b) - self.L_short[j] / 2, 0)
            score = abs(w) + 10 * excess
            best = np.argmin(score, 1)
            r = np.arange(len(sel))
            mod[sel] = j[r, best]
            A[sel], B[sel], W[sel] = a[r, best], b[r, best], w[r, best]
            out[sel] = (excess[r, best] <= tol) & (abs(W[sel]) <= wtol)
        chip = np.where(mod >= 0, self.chip_of(np.maximum(mod, 0), A, B), -1)
        return mod, chip, out, A, B, W

    def chip_uid(self, mod, chip):
        return mod * 4 + chip

    def chip_rects(self, m):
        """Chip rectangles of modules m in local (a = long, b = short) coordinates: arrays (len(m), 4, 4) of
        (a_lo, a_hi, b_lo, b_hi) for chip index 0..3; chips that do not exist get an empty rectangle."""
        La, Lb = self.L_long[m] / 2, self.L_short[m] / 2
        two_a, two_b = self.n_long[m] == 2, self.n_short[m] == 2
        r = np.zeros((len(m), 4, 4))
        for ci in range(4):
            hi_a, hi_b = ci & 1, ci >> 1
            alo = np.where(two_a, np.where(hi_a, 0, -La), -La)
            aha = np.where(two_a, np.where(hi_a, La, 0), La)
            blo = np.where(two_b, np.where(hi_b, 0, -Lb), -Lb)
            bhi = np.where(two_b, np.where(hi_b, Lb, 0), Lb)
            exists = (two_a | (hi_a == 0)) & (two_b | (hi_b == 0))
            r[:, ci] = np.where(exists[:, None], np.stack([alo, aha, blo, bhi], 1), [1, -1, 1, -1])
        return r

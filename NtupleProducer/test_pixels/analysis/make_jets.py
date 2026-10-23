#!/usr/bin/env python3
"""Build a flat table of L1 jets with gen flavour, L1 NN tag scores and pixel-track features.

    python3 make_jets.py out.npz SAMPLE file1.root [file2.root ...]

Jets: L1NGJets (the SC4NG tagger jets), matched to GenJets within dR < 0.3 for the hadron flavour.
Pixel features use the HLT pixel tracks within dR < 0.4 of the jet axis that are compatible with the
leading pixel vertex (max sum pT^2): |z0 - z_PV| < 0.2 cm, pT > 1 GeV. The transverse impact parameter
w.r.t. the beam spot is signed by the jet direction (positive = track crosses the jet axis downstream).
"""
import sys

import awkward as ak
import numpy as np
import uproot

DR_GEN = 0.3
DR_TRK = 0.4
DZ_PV = 0.2
PT_TRK = 1.0
SIG_CUT = 3.0
NTOP = 3

BRANCHES = [
    "nL1NGJets", "L1NGJets_*",
    "GenJets_pt", "GenJets_eta", "GenJets_phi", "GenJets_hadronFlavour",
    "PixelTracks_pt", "PixelTracks_eta", "PixelTracks_phi", "PixelTracks_dz",
    "PixelTracks_dxyBS", "PixelTracks_dxyErr", "PixelTracks_vtxIdx",
    "PixelVertices_z", "PixelVertices_sumPt2",
]


PT_CAP = 10.0


def leading_vertex_z(arr):
    nvtx = ak.to_numpy(ak.num(arr.PixelVertices_z))
    offsets = np.concatenate([[0], np.cumsum(nvtx)])
    vidx = arr.PixelTracks_vtxIdx
    w = np.minimum(arr.PixelTracks_pt, PT_CAP) ** 2
    gidx = ak.flatten(vidx + offsets[:-1])
    keep = ak.to_numpy(ak.flatten(vidx >= 0))
    sums = np.bincount(ak.to_numpy(gidx)[keep], weights=ak.to_numpy(ak.flatten(w))[keep], minlength=offsets[-1])
    best = ak.argmax(ak.unflatten(sums, nvtx), axis=1, keepdims=True)
    return ak.fill_none(ak.firsts(arr.PixelVertices_z[best]), -999.0)


def dphi(a, b):
    return (a - b + np.pi) % (2 * np.pi) - np.pi


def process(arr, sample):
    jets = ak.zip({k[len("L1NGJets_"):]: arr[k] for k in arr.fields if k.startswith("L1NGJets_")})
    gen = ak.zip({"pt": arr.GenJets_pt, "eta": arr.GenJets_eta, "phi": arr.GenJets_phi,
                  "flav": arr.GenJets_hadronFlavour})
    trk = ak.zip({"pt": arr.PixelTracks_pt, "eta": arr.PixelTracks_eta, "phi": arr.PixelTracks_phi,
                  "dz": arr.PixelTracks_dz, "dxy": arr.PixelTracks_dxyBS, "dxyErr": arr.PixelTracks_dxyErr})

    # leading pixel vertex: max sum of min(pT, PT_CAP)^2 over its tracks. The stored sumPt2 is dominated
    # by badly measured high-pT pixel tracks and picks a pileup vertex in ~60% of PU200 events.
    zpv = leading_vertex_z(arr)
    trk = trk[(trk.pt > PT_TRK) & (abs(trk.dz - zpv) < DZ_PV)]

    # gen matching (closest gen jet within DR_GEN)
    pairs = ak.cartesian({"j": jets, "g": gen}, nested=True)
    dr = np.hypot(pairs.j.eta - pairs.g.eta, dphi(pairs.j.phi, pairs.g.phi))
    best = ak.argmin(dr, axis=2, keepdims=True)
    drbest = ak.flatten(dr[best], axis=2)
    gbest = ak.flatten(pairs.g[best], axis=2)
    matched = ak.fill_none(drbest < DR_GEN, False)
    flav = ak.where(matched, ak.fill_none(gbest.flav, -1), -1)
    genpt = ak.where(matched, ak.fill_none(gbest.pt, -1.0), -1.0)

    # tracks in the jet cone
    jt = ak.cartesian({"j": jets, "t": trk}, nested=True)
    dr_t = np.hypot(jt.j.eta - jt.t.eta, dphi(jt.j.phi, jt.t.phi))
    jt = jt[dr_t < DR_TRK]
    sign = np.sign(jt.t.dxy * np.sin(jt.j.phi - jt.t.phi))
    sip = sign * abs(jt.t.dxy)
    sig = sip / jt.t.dxyErr
    sig_sorted = ak.sort(sig, axis=2, ascending=False)
    padded = ak.fill_none(ak.pad_none(sig_sorted, NTOP, axis=2), -50.0)

    out = {
        "sample": sample,
        "pt": jets.pt, "eta": jets.eta, "phi": jets.phi, "mass": jets.mass,
        "flav": flav, "genpt": genpt,
        "nTrk": ak.num(sig, axis=2),
        "nSig3": ak.sum(sig > SIG_CUT, axis=2),
        "nSig5": ak.sum(sig > 5.0, axis=2),
        "sumSig": ak.sum(ak.where(sig > 0, sig, 0), axis=2),
        "maxSIP": ak.fill_none(ak.max(sip, axis=2), -1.0),
    }
    for i in range(NTOP):
        out[f"ipsig{i + 1}"] = padded[:, :, i]
    for c in ["b", "c", "uds", "g", "tau_p", "tau_n", "mu", "e"]:
        out[f"score_{c}"] = jets[f"score_{c}"]
    out["evt"] = ak.broadcast_arrays(ak.local_index(arr.nL1NGJets, axis=0), jets.pt)[0]
    out["jetIdx"] = ak.local_index(jets.pt, axis=1)
    flat = {k: (ak.to_numpy(ak.flatten(v)) if not isinstance(v, str) else v) for k, v in out.items()}
    n = len(flat["pt"])
    flat["sample"] = np.array([sample] * n)
    return flat


def main():
    outname, sample, files = sys.argv[1], sys.argv[2], sys.argv[3:]
    tables, offset = [], 0
    for chunk in uproot.iterate([f + ":Events" for f in files], filter_name=BRANCHES, step_size="200 MB", library="ak"):
        t = process(chunk, sample)
        t["evt"] = t["evt"] + offset
        offset += len(chunk)
        tables.append(t)
    cols = {k: np.concatenate([t[k] for t in tables]) for k in tables[0]}
    np.savez_compressed(outname, **cols)
    print(f"{sample}: {offset} events, {len(cols['pt'])} jets -> {outname}")


if __name__ == "__main__":
    main()

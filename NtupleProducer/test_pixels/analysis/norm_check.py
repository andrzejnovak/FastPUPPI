#!/usr/bin/env python3
"""Why does the weighted QCD (pT-hat 30-470 + PU 200) predict more L1 window events than minimum bias (x1.47)?

    python3 norm_check.py OUT.json SCOUTING.json QCDPT_DIR MB_GLOBS
Hypothesis: double counting. Each QCD event is one hard scatter plus 200 minimum-bias interactions, which already
contain hard scatters at their natural rate (~0.3 per crossing with pT-hat 30-50), so a crossing with two such scatters
is counted once per scatter. Per pT-hat bin and HT bin: weighted window yield, and the number of the 4 leading L1 jets
matched to a generator jet of the hard scatter (dR < 0.3); minimum-bias yields for comparison.
"""
import glob
import json
import os
import sys

import awkward as ak
import numpy as np
import uproot

os.environ.setdefault("HT_MIN", "150")
os.environ.setdefault("MB_TOTAL", "1999360")
import scouting as SC  # noqa: E402

LUMI_PB = 3.0e6
HT_EDGES = np.array([150, 200, 250, 300, 360, 450, 600, 1e9])


def nmatched(files, ev):
    g = ak.concatenate([uproot.open(f)["Events"].arrays(["GenJets_eta", "GenJets_phi", "GenJets_pt"]) for f in files])
    out = np.zeros(len(ev["ht"]), int)
    for i in range(len(ev["ht"])):
        ge, gp = np.asarray(g.GenJets_eta[i]), np.asarray(g.GenJets_phi[i])
        if not len(ge):
            continue
        for j in range(4):
            if ev["jidx"][i, j] < 0:
                continue
            dr = np.hypot(ge - ev["eta"][i, j], (gp - ev["phi"][i, j] + np.pi) % (2 * np.pi) - np.pi)
            out[i] += dr.min() < 0.3
    return out


def main():
    out, sc_json, qdir, mb_pat = sys.argv[1:5]
    c1, r1, c2, r2 = json.load(open(sc_json))["setup"]["window"]
    sel = lambda d: d["n4"] & (d["ht"] > SC.HT_CUT)
    win = lambda d: sel(d) & (np.hypot((d["m1"] - c1) / r1, (d["m2"] - c2) / r2) < 1.6)
    mb = SC.read(mb_pat)
    SC.kinematics(mb)
    w_mb = SC.N_BX / SC.MB_TOTAL
    res = {"ht_edges": HT_EDGES.tolist(), "mb": {}, "qcd": {}}
    for name, m in (("4 jets", sel(mb)), ("window", win(mb))):
        res["mb"][name] = (np.histogram(mb["ht"][m], HT_EDGES)[0] * w_mb).tolist()
    for bn in sorted({os.path.basename(f).split("_")[1] for f in glob.glob(f"{qdir}/perfNano_QCDPt*_*.root")}, key=lambda s: int(s[5:])):
        files = sorted(glob.glob(f"{qdir}/perfNano_{bn}_*.root"))
        xs = np.mean([float(np.load(f)["xsec"][0]) for f in glob.glob(f"/scratch/submit/cms/novaka/l1pixels/offline_w/{bn}_*.npz")
                      if float(np.load(f)["xsec"][0]) > 0])
        q = SC.read(",".join(files))
        SC.kinematics(q)
        w = xs * LUMI_PB / len(q["ht"])
        nm = nmatched(files, q)
        r = res["qcd"][bn] = {"weight": w, "xsec_pb": float(xs)}
        for name, m in (("4 jets", sel(q)), ("window", win(q))):
            r[name] = (np.histogram(q["ht"][m], HT_EDGES)[0] * w).tolist()
            r[name + " raw"] = np.histogram(q["ht"][m], HT_EDGES)[0].tolist()
            r[name + " n_matched"] = np.bincount(nm[m], minlength=5).tolist()
        print(bn, json.dumps({k: v for k, v in r.items() if "n_matched" in k or "raw" in k}), flush=True)
    for name in ("4 jets", "window"):
        tot = np.sum([res["qcd"][b][name] for b in res["qcd"]], axis=0)
        print(f"{name:8s} QCD/MB per HT bin:", " ".join(f"{a / b:.2f}" if b > 0 else "-" for a, b in zip(tot, res["mb"][name])),
              f" total {tot.sum() / np.sum(res['mb'][name]):.2f}", flush=True)
        for b in res["qcd"]:
            print(f"   {b:9s} share of QCD:", " ".join(f"{x / t:.2f}" if t > 0 else "-" for x, t in zip(res["qcd"][b][name], tot)), flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()

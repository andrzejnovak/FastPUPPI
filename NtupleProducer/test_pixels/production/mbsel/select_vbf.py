#!/usr/bin/env python3
"""Select minimum-bias events for a VBF-like targeted production from the stored-L1-jet scan (scan_jets.py).

    python3 select_vbf.py "JSCAN_GLOB" "DONE_GLOB" OUT_JOBS.txt OUT_SUMMARY.json [FILES_PER_JOB]
Preselection on the stored 14_0 emulator SC4 jets (|eta| < 5): any pair with leading pT > LEAD, second > SUB and
m_jj > MJJ (massless jets). Validation on events already re-simulated with pixels (DONE_GLOB, our 17_0 emulation):
fraction of events passing an emulated VBF seed (scPuppiCorrJets, online pT, any pair) that the stored preselection
keeps. New events = preselected and not in DONE_GLOB; written as "lfn|run:lumi:event,...;lfn|..." jobs.
"""
import glob
import json
import os
import sys

import awkward as ak
import numpy as np
import uproot

LEAD, SUB, MJJ = (float(os.environ.get(k, d)) for k, d in (("LEAD", 40), ("SUB", 20), ("MJJ", 250)))
scan_glob, done_glob, out_jobs, out_sum = sys.argv[1:5]
per_job = int(sys.argv[5]) if len(sys.argv) > 5 else 25


def best_pair(pt, eta, phi, lead, sub):
    """Per event: does any pair (i != j) have pt_i > lead, pt_j > sub; returns the max m_jj over such pairs."""
    n = pt.shape[1]
    best = np.zeros(pt.shape[0])
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            ok = (pt[:, i] > lead) & (pt[:, j] > sub)
            m2 = 2 * pt[:, i] * pt[:, j] * (np.cosh(eta[:, i] - eta[:, j]) - np.cos(phi[:, i] - phi[:, j]))
            best = np.where(ok, np.maximum(best, np.sqrt(np.maximum(m2, 0))), best)
    return best


sc = {k: np.concatenate([np.load(f)[k] for f in sorted(glob.glob(scan_glob))]) for k in ("run", "lumi", "event", "pt", "eta", "phi")}
m_st = best_pair(sc["pt"], sc["eta"], sc["phi"], LEAD, SUB)
pre = m_st > MJJ
print(f"scanned {len(pre)} events; stored VBF-like preselection (lead {LEAD:g}, sub {SUB:g}, mjj {MJJ:g}) keeps {pre.sum()} "
      f"({pre.mean():.4f})", flush=True)

# validation on already re-simulated events
ids, emu = [], {}
for f in sorted(glob.glob(done_glob)):
    a = uproot.open(f)["Events"].arrays(["luminosityBlock", "event", "scPuppiCorrJets_pt", "scPuppiCorrJets_eta", "scPuppiCorrJets_phi"])
    pt = ak.to_numpy(ak.fill_none(ak.pad_none(a.scPuppiCorrJets_pt, 8, clip=True), 0.0))
    eta = ak.to_numpy(ak.fill_none(ak.pad_none(a.scPuppiCorrJets_eta, 8, clip=True), 0.0))
    phi = ak.to_numpy(ak.fill_none(ak.pad_none(a.scPuppiCorrJets_phi, 8, clip=True), 0.0))
    for (l1, s1) in ((92, 25), (70, 25), (60, 20), (50, 20)):
        emu.setdefault((l1, s1), []).append(best_pair(pt, eta, phi, l1, s1))
    ids += list(zip(ak.to_numpy(a.luminosityBlock).tolist(), ak.to_numpy(a.event).tolist()))
done = {k: i for i, k in enumerate(ids)}
key = list(zip(sc["lumi"].tolist(), sc["event"].tolist()))
idx = np.array([done.get(k, -1) for k in key])
indone = idx >= 0
val = {}
for (l1, s1), ms in emu.items():
    m_emu = np.concatenate(ms)[idx[indone]]
    for mcut in (400, 500, 620):
        sel = m_emu > mcut
        val[f"emu_{l1:g}_{s1:g}_mjj{mcut}"] = {"n": int(sel.sum()), "kept_by_stored_presel": float(pre[indone][sel].mean()) if sel.any() else None}
print(f"already re-simulated: {len(ids)}, found in scan: {indone.sum()}")
for k, v in val.items():
    print(f"  emulated {k}: {v['n']} events, stored preselection keeps {v['kept_by_stored_presel']}")

lumi_file = {}
for line in open("file_lumi.txt"):
    lfn, lumis = line.split()
    for lumi in lumis.strip("[]").split(","):
        lumi_file[int(lumi)] = lfn
new = pre & ~indone
by_file = {}
for r, l, e in zip(sc["run"][new], sc["lumi"][new], sc["event"][new]):
    by_file.setdefault(lumi_file[int(l)], []).append(f"{r}:{l}:{e}")
files = sorted(by_file)
jobs = [";".join(f"{f}|{','.join(by_file[f])}" for f in files[i:i + per_job]) for i in range(0, len(files), per_job)]
open(out_jobs, "w").write("\n".join(jobs) + "\n")
summary = {"lead": LEAD, "sub": SUB, "mjj": MJJ, "n_scanned": len(key), "n_presel": int(pre.sum()),
           "n_done_in_scan": int(indone.sum()), "n_new_selected": int(new.sum()), "n_jobs": len(jobs), "validation": val}
json.dump(summary, open(out_sum, "w"), indent=1)
print(f"new VBF-like events: {new.sum()} in {len(files)} files -> {len(jobs)} jobs")

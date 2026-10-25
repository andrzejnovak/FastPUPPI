#!/usr/bin/env python3
"""Validate a stored-L1-HT preselection against the official ntuples, then select new minimum-bias events.

    python3 select_new.py "SCAN_GLOB" "OFFICIAL_MB_GLOB" CUT OUT_JOBS.txt OUT_SUMMARY.json [FILES_PER_JOB]
Stored HT: 14_0 emulator jets saved in the RAW (scan_ht.py). Emulated HT: our 17_0 ntuples, as in select_events.py.
On events in both, prints how many emulated-HT > X events a stored-HT cut keeps. New events = scanned events not in the
official ntuples; those with stored HT > CUT go into jobs ("lfn|run:lumi:event,...;lfn|..."), grouped by file.
"""
import glob
import json
import sys

import awkward as ak
import numpy as np
import uproot

scan_glob, off_glob, cut, out_jobs, out_sum = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4], sys.argv[5]
per_job = int(sys.argv[6]) if len(sys.argv) > 6 else 25
sc = {k: np.concatenate([np.load(f)[k] for f in sorted(glob.glob(scan_glob))]) for k in ("run", "lumi", "event", "ht")}
ids, emu, nns = [], [], []
for f in sorted(glob.glob(off_glob)):
    a = uproot.open(f)["Events"].arrays(["luminosityBlock", "event", "L1NGJets_pt", "L1NGJets_eta", "L1NGJets_score_b",
                                         "L1NGJets_score_uds", "L1NGJets_score_g"])
    pt, eta = a.L1NGJets_pt, a.L1NGJets_eta
    emu.append(ak.to_numpy(ak.sum(pt[(pt > 30) & (abs(eta) < 2.4)], axis=1)))
    nn = a.L1NGJets_score_b / np.maximum(a.L1NGJets_score_b + a.L1NGJets_score_uds + a.L1NGJets_score_g, 1e-6)
    sel = (abs(eta) < 2.4) & (pt > 15)
    nns.append(ak.to_numpy(ak.sum(nn[sel][ak.argsort(pt[sel], ascending=False)][:, :4], axis=1)))  # as in direct_rate
    ids += list(zip(ak.to_numpy(a.luminosityBlock).tolist(), ak.to_numpy(a.event).tolist()))
emu, nns = np.concatenate(emu), np.concatenate(nns)
off = {k: i for i, k in enumerate(ids)}
key = list(zip(sc["lumi"].tolist(), sc["event"].tolist()))
idx = np.array([off.get(k, -1) for k in key])
inoff = idx >= 0
print(f"scanned {len(key)} events; official {len(ids)}, of which found in scan {inoff.sum()}; new {(~inoff).sum()}")

st, em, nn = sc["ht"][inoff], emu[idx[inoff]], nns[idx[inoff]]
val = {}
for c in (40, 50, 60, 70, 80, 90):
    row = {"kept_frac_all": float((st > c).mean())}
    for x in (90, 100, 150, 200, 300):
        m = em > x
        row[f"eff_emu_ht_gt{x}"] = float((st[m] > c).mean())
        row[f"lost_emu_ht_gt{x}"] = int((st[m] <= c).sum())
    for x, sc_ in ((150, 1.4), (170, 1.5), (250, 1.5)):  # b-tagged seeds like those of the direct test
        m = (em > x) & (nn > sc_)
        row[f"eff_tagged_ht{x}_nn{sc_}"] = float((st[m] > c).mean())
        row[f"n_tagged_ht{x}_nn{sc_}"] = int(m.sum())
    val[c] = row
    print(f"stored HT > {c}: keeps {row['kept_frac_all']:.4f} of events; of emulated HT > 100/150/200/300: "
          + " ".join(f"{row[f'eff_emu_ht_gt{x}']:.4f} ({row[f'lost_emu_ht_gt{x}']} lost)" for x in (100, 150, 200, 300))
          + "; tagged seeds: " + " ".join(f"{k[12:]} {v:.4f}" for k, v in row.items() if k.startswith("eff_tagged")))

lumi_file = {}
for line in open("file_lumi.txt"):
    lfn, lumis = line.split()
    for lumi in lumis.strip("[]").split(","):
        lumi_file[int(lumi)] = lfn
new = ~inoff & (sc["ht"] > cut)
by_file = {}
for r, l, e in zip(sc["run"][new], sc["lumi"][new], sc["event"][new]):
    by_file.setdefault(lumi_file[int(l)], []).append(f"{r}:{l}:{e}")
files = sorted(by_file)
jobs = [";".join(f"{f}|{','.join(by_file[f])}" for f in files[i:i + per_job]) for i in range(0, len(files), per_job)]
open(out_jobs, "w").write("\n".join(jobs) + "\n")
summary = {"n_scanned": len(key), "n_official": len(ids), "n_official_in_scan": int(inoff.sum()),
           "n_new_total": int((~inoff).sum()), "cut": cut, "n_new_selected": int(new.sum()), "n_jobs": len(jobs),
           "validation": val}
json.dump(summary, open(out_sum, "w"), indent=1)
print(f"new events with stored HT > {cut:.0f}: {new.sum()} of {(~inoff).sum()} in {len(files)} files -> {len(jobs)} jobs")

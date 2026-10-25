#!/usr/bin/env python3
"""Inner Tracker link occupancy at PU 200 from the emulated chip bitstreams (dump_bits.py) and the tkLayout
module -> lpGBT -> DTC cabling map shipped with CMSSW (data-CondTools-SiPhase2Tracker, CMSSWCablingMap__OT800_IT700).

    python3 occupancy.py bits_*.npz
Payload only: the QCore-encoded hits of Phase2ITQCoreProducer, without chip stream headers, tags or link framing,
so occupancies are lower bounds. lpGBT uplink payload taken as 7 e-links x 1.28 Gb/s = 8.96 Gb/s (assumption).
"""
import csv
import glob
import json
import sys
from collections import defaultdict

import numpy as np

MAP = ("/cvmfs/cms.cern.ch/el9_amd64_gcc13/cms/data-CondTools-SiPhase2Tracker/V00-02-00/CondTools/SiPhase2Tracker/"
       "data/CMSSWCablingMap__OT800_IT700.csv")
L1A = 750e3
LPGBT = 7 * 1.28e9

files = sys.argv[1:] or sorted(glob.glob("bits_*.npz"))
d = {k: np.concatenate([np.load(f)[k] + (i * 1000 if k == "event" else 0) for i, f in enumerate(files)])
     for k in ("event", "detid", "chip", "bits")}
nev = len(np.unique(d["event"]))
cab = {}
for r in csv.reader(open(MAP)):
    if r and r[0].strip().isdigit() and ((int(r[0]) >> 25) & 7) in (1, 2):
        cab[int(r[0])] = (int(r[2]), int(r[1]))  # (DTC, lpGBT within DTC)

mods = np.unique(d["detid"])
known = np.isin(mods, list(cab))
print(f"{nev} events, {len(mods)} modules with hits, {known.mean():.1%} found in the cabling map")

# per module and per chip: mean bits per event
per_mod = defaultdict(float)
per_chip = defaultdict(float)
for det, chip, b in zip(d["detid"], d["chip"], d["bits"]):
    per_mod[int(det)] += b / nev
    per_chip[(int(det), int(chip))] += b / nev
total = sum(per_mod.values())


def region(det):
    sub = (det >> 25) & 7
    if sub == 1:
        return f"TBPX L{(det >> 20) & 0xF}"
    disk = (det >> 18) & 0xF
    return f"{'TFPX' if disk <= 8 else 'TEPX'} D{disk}"


# per lpGBT link
per_link = defaultdict(float)
nmiss = 0
for det, b in per_mod.items():
    if det in cab:
        per_link[cab[det]] += b
    else:
        nmiss += b
occ = np.array(sorted(per_link.values())) * L1A / LPGBT
reg = defaultdict(list)
for det, b in per_mod.items():
    reg[region(det)].append(b)
chips = np.array(list(per_chip.values()))
res = {
    "events": nev, "mean_bits_per_event": total, "readout_Tbps_at_750kHz": total * L1A / 1e12,
    "bits_not_in_map_frac": nmiss / total, "links_with_hits": len(per_link), "links_in_map": len(set(cab.values())),
    "link_occupancy_median": float(np.median(occ)), "link_occupancy_p90": float(np.percentile(occ, 90)),
    "link_occupancy_max": float(occ.max()),
    "spare_Tbps_at_750kHz": float(((1 - occ) * LPGBT).sum() / 1e12),
    "chip_bits_per_event_median": float(np.median(chips)), "chip_bits_per_event_p99": float(np.percentile(chips, 99)),
    "chip_Gbps_at_750kHz_max": float(chips.max() * L1A / 1e9),
    "by_region": {k: {"modules": len(v), "mean_bits_per_module": float(np.mean(v)),
                      "Gbps_per_module_at_750kHz": float(np.mean(v) * L1A / 1e9)} for k, v in sorted(reg.items())},
}
json.dump(res, open("occupancy.json", "w"), indent=1)
print(json.dumps(res, indent=1))

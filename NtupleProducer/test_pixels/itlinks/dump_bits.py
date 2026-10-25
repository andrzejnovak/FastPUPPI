#!/usr/bin/env python3
"""Bits per chip per event from bitstream_cfg.py output -> npz (detid, chip, bits, ndigi per event).
    python3 dump_bits.py bits.root out.npz"""
import sys
import numpy as np
from DataFormats.FWLite import Events, Handle

ev = Events(sys.argv[1])
hb = Handle("edm::DetSetVector<Phase2ITChipBitStream>")
hd = Handle("edm::DetSetVector<PixelDigi>")
rows = []
for i, e in enumerate(ev):
    e.getByLabel(("bits", "", "ITBITS"), hb)
    e.getByLabel(("simSiPixelDigis", "Pixel"), hd)
    nd = {ds.detId(): ds.size() for ds in hd.product()}
    for ds in hb.product():
        for c in ds:
            rows.append((i, ds.detId(), c.get_rocid(), c.get_bitstream().size(), nd.get(ds.detId(), 0)))
a = np.array(rows, dtype=np.int64)
np.savez(sys.argv[2], event=a[:, 0], detid=a[:, 1], chip=a[:, 2], bits=a[:, 3], ndigi_module=a[:, 4])
print(f"{len(set(a[:, 0]))} events, {len(set(a[:, 1]))} modules, mean bits/event {a[:, 3].sum() / len(set(a[:, 0])):.3g}")

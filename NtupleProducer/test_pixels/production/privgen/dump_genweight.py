#!/usr/bin/env python3
"""lumi, event, generator weight, pT-hat of every event in a GEN(-SIM) file: python3 dump_genweight.py gs.root out.txt"""
import sys

from DataFormats.FWLite import Events, Handle

h = Handle("GenEventInfoProduct")
with open(sys.argv[2], "w") as out:
    for e in Events(sys.argv[1]):
        e.getByLabel("generator", h)
        a = e.eventAuxiliary().id()
        out.write(f"{a.luminosityBlock()} {a.event()} {h.product().weight():.6g} {h.product().qScale():.4f}\n")

#!/usr/bin/env python3
"""Concatenate per-file list npz files (make_l1ext_lists.py output) into one, renumbering the event index.

    python3 merge_lists.py OUT.npz part1.npz [part2.npz ...]
"""
import sys

import numpy as np

out, parts = sys.argv[1], [dict(np.load(p, allow_pickle=True)) for p in sys.argv[2:]]
meta = ("sample", "trk_feats", "hit_feats")
cols, offset = {k: [] for k in parts[0] if k not in meta}, 0
for p in parts:
    for k in cols:
        cols[k].append(p[k] + offset if k == "evt" else p[k])
    offset += int(p["evt"].max()) + 1 if len(p["evt"]) else 0
np.savez_compressed(out, **{k: parts[0][k] for k in meta}, **{k: np.concatenate(v) for k, v in cols.items()})
print(f"{len(parts)} parts, {sum(len(p['pt']) for p in parts)} jets -> {out}")

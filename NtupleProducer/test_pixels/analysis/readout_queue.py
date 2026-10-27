#!/usr/bin/env python3
"""Queueing of the regional pixel request behind normal L1-accept readout, per module, on the real uplinks.

    python3 readout_queue.py OUT.json queue_A.npz[:label] [queue_B.npz[:label] ...]
Inputs: chip_readout_merge.py with QUEUE_DUMP (per module: uplinks, normal-readout bits of each emulated PU 200 crossing;
per pre-selected crossing: the modules the request reads and their bits).
Model: every module is one first-in-first-out server of upl x 1.28 Gb/s. L1 accepts arrive as a Poisson process at
750 kHz and load every module with the bits of a random emulated crossing; requests arrive at the pre-selection rate
(HT > 140: 367 kHz, HT > 200: 123 kHz) and load the modules of a random pre-selected crossing. Request latency = time
until the last of its modules has sent its bits, for (a) one shared queue (FIFO) and (b) requests served first
(pre-emptive priority; a non-pre-emptive chip adds at most one normal event). Plus the chip's fixed minimum delay
from start of read to first output bit (RD53B manual v2.21 sec. 9.1: 31 BX = 0.775 us). Not modelled: trigger rules,
the higher occupancy of accepted crossings, link framing (Aurora 64b/66b, ~3%), back-end processing.
"""
import json
import sys

import numpy as np

ELINK = 1.28e9
L1A_RATE = 750e3
RATES = {140: 367e3, 200: 123e3}
T_FIXED_US = 31 * 0.025
T_SIM = float(__import__("os").environ.get("T_SIM", "0.05"))  # simulated seconds
REGIONS = {1: "TBPX L1", 2: "TBPX L2", 3: "TBPX L3", 4: "TBPX L4"}


def region(l):
    return REGIONS.get(abs(l), "TFPX/TEPX")


def simulate(q, cut, rate, rng):
    cap = q["upl"] * ELINK / 1e6  # bits per us
    E = q["emu_bits"].astype(float)
    off, rm, rb = q["req_off"], q["req_mod"], q["req_bits"].astype(float)
    pool = np.where(q["ht"] > cut)[0]
    n_l1a, n_req = rng.poisson(L1A_RATE * T_SIM), rng.poisson(rate * T_SIM)
    t = np.concatenate([rng.uniform(0, T_SIM * 1e6, n_l1a), rng.uniform(0, T_SIM * 1e6, n_req)])
    kind = np.concatenate([np.zeros(n_l1a, int), np.ones(n_req, int)])
    o = np.argsort(t)
    t, kind = t[o], kind[o]
    nmod = len(cap)
    b_all = np.zeros(nmod)  # FIFO backlog (bits)
    b_req, b_norm = np.zeros(nmod), np.zeros(nmod)  # priority model: two classes
    last_norm = np.zeros(nmod)
    lat_fifo, lat_prio, lat_np, lat_alone, util = [], [], [], [], np.zeros(nmod)
    tp = 0.0
    for ti, k in zip(t, kind):
        dt = ti - tp
        tp = ti
        srv = cap * dt
        b_all = np.maximum(b_all - srv, 0)
        r = np.minimum(b_req, srv)
        b_req -= r
        b_norm = np.maximum(b_norm - (srv - r), 0)
        if k == 0:
            w = E[rng.integers(len(E))]
            b_all += w
            b_norm += w
            last_norm = w
            util += w
        else:
            c = pool[rng.integers(len(pool))]
            m, w = rm[off[c]:off[c + 1]], rb[off[c]:off[c + 1]]
            if len(m) == 0:
                continue
            b_all[m] += w
            b_req[m] += w
            util[m] += w
            lat_fifo.append((b_all[m] / cap[m]).max())
            lat_prio.append((b_req[m] / cap[m]).max())
            lat_np.append(((b_req[m] + np.minimum(b_norm[m], last_norm[m])) / cap[m]).max())
            lat_alone.append((w / cap[m]).max())
    util /= cap * T_SIM * 1e6
    return {k: np.array(v) + T_FIXED_US for k, v in (("fifo", lat_fifo), ("priority", lat_prio),
                                                       ("priority_nonpreemptive", lat_np), ("alone", lat_alone))}, util


def stats(a):
    return {"median": float(np.median(a)), "p90": float(np.percentile(a, 90)), "p99": float(np.percentile(a, 99)),
            "p999": float(np.percentile(a, 99.9)), "frac_above_1p5us": float((a > 1.5).mean()),
            "frac_above_2p5us": float((a > 2.5).mean()), "frac_above_5us": float((a > 5).mean())}


def main():
    out = sys.argv[1]
    res = {"method": __doc__.strip().splitlines()[2:], "t_sim_s": T_SIM, "t_fixed_us": T_FIXED_US, "variants": {}}
    rng = np.random.default_rng(7)
    for spec in sys.argv[2:]:
        path, label = (spec.split(":") + [None])[:2]
        q = dict(np.load(path))
        label = label or path
        cap = q["upl"] * ELINK
        reg = np.array([region(l) for l in q["lid"]])
        u_norm = L1A_RATE * q["emu_bits"].mean(0) / cap
        v = {"charge_fix": bool(q["charge_fix"]), "normal_readout_utilisation": {}, "cuts": {}}
        for r in np.unique(reg):
            s = reg == r
            v["normal_readout_utilisation"][r] = {"mean": float(u_norm[s].mean()), "max": float(u_norm[s].max())}
        for cut, rate in RATES.items():
            sel = q["ht"] > cut
            # mean request load per module and command frames: how often each module is addressed
            nreq = np.zeros(len(cap))
            breq = np.zeros(len(cap))
            for c in np.where(sel)[0]:
                m = q["req_mod"][q["req_off"][c]:q["req_off"][c + 1]]
                nreq[m] += 1
                breq[m] += q["req_bits"][q["req_off"][c]:q["req_off"][c + 1]]
            p_mod = nreq / sel.sum()
            u_req = rate * breq / sel.sum() / cap
            lat, util = simulate(q, cut, rate, rng)
            v["cuts"][f"ht>{cut}"] = {
                "request_rate_kHz": rate / 1e3,
                "request_utilisation": {r: {"mean": float(u_req[reg == r].mean()), "max": float(u_req[reg == r].max())}
                                        for r in np.unique(reg)},
                "total_utilisation_simulated_max": float(util.max()),
                "total_utilisation_simulated_by_region_max": {r: float(util[reg == r].max()) for r in np.unique(reg)},
                "requests_per_module_kHz_max": float(rate * p_mod.max() / 1e3),
                "latency_us": {k: stats(a) for k, a in lat.items()}}
        res["variants"][label] = v
        print(label, json.dumps({c: {k: (x["median"], x["p99"], x["frac_above_2p5us"]) for k, x in d["latency_us"].items()}
                                 for c, d in v["cuts"].items()}), flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()

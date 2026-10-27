# Internal feasibility studies, 2026-10-27

Internal only (not for circulation). Question: is the pixel path workable at all, and what would make the κλ
pixel-vs-NN projection and pixel scouting deliverable?

## Verdict up front

- **The CROC readout chip, as built, cannot deliver a region of interest early.** This is not a bandwidth problem. Hits
  leave the chip only at a fixed, programmed latency after a trigger. A ~1–5 µs regional read and the 12.5 µs L1 accept
  of every other crossing cannot both be served (details in item 4). It blocks path A (L1 pixel seed) and path B (pixel
  scouting) in Phase-2 as built.
- **Bandwidth and latency would be fine** if a chip had a prioritised early path: ~1.9 µs median (p99 2.7 µs), including the
  chip's fixed 0.78 µs, on the real uplinks with normal 750 kHz readout running.
- **The one hardware opening is the replacement of barrel layer 1** (designed to be swapped at least once in HL-LHC).
  Layer 1 alone is weak, though (item 5): a single hit cannot confirm the track at PU 200.
- **The refit and tag package itself is robust:**
  - 64-bit word: no loss;
  - 10% random hit loss: −0.6 points at the seed.
- **Background:** pT-binned QCD with generator cross-sections is being produced:
  - pixel ntuples: 558 OSG jobs, ~140k events;
  - offline jets with weights: all 654 QCD files.
  - Fit (`kl_qcdbkg.py`): direct flavour-aware background, closure against minimum bias, and a bootstrap.
  - The κλ pixel-vs-NN statement waits on it (section "Background").

## Item 4: what the pixel readout would need

**Chip architecture** (RD53B manual v2.21, shared CROC/ATLAS digital design; text in
`/scratch/.../derived/rd53b_manual_v2.21.txt`):

- Sec. 7.4 (lines ~850–880):
  - every 4-pixel region has 8 latency memories holding the BCID;
  - when the programmed latency is reached (one global value, ≤ 511 BX = 12.8 µs), the hit is kept only if a trigger is
    present; otherwise it is released.
  - So one chip setting serves one latency.
- Sec. 9 (lines ~1190–1215):
  - "two-level" (manual-read) mode: an L0 trigger at the programmed latency marks a crossing; a later `RdTrig` selects it.
  - But "the read_trigger command has no action other than setting the read or clear bit. Readout will happen when the
    countdown timer expires, as usual."
  - The countdown (second-level latency) is again one global value. Data therefore come out at a fixed delay for every
    trigger.
- **Consequence.** To read a requested crossing at ~1–2 µs and still read any other crossing at the 12.5 µs L1 accept, a
  chip would need both:
  - (a) a short trigger latency for the request;
  - (b) its hits retained to 12.5 µs for crossings without a request.
  - The CROC does neither.
- **The two-level route is no way out either.** Every crossing CMS might accept would need an L0 within the latency.
  CMS Phase-2 has no such fast L0 for the whole menu, and the design envelope is about 4 MHz L0 / 1 MHz L1. L0 on every
  crossing would take 100% of the command bandwidth (one 4-BX trigger frame per 4 BX) and about 500 tags in flight
  (table: 256).
- Hit-loss cost: the manual notes that latency buffers stay occupied longer in two-level mode. That lowers the hit-rate
  capacity, which matters most in barrel layer 1.

**If a chip had an early path** (`readout_queue.py`, `run_readout_queue.sh` → `derived/chip_readout/readout_queue.json`).

Model:
- each module is one server of (uplinks × 1.28 Gb/s);
- Poisson 750 kHz L1 accepts carry the corrected CROC payload of a random emulated PU 200 crossing;
- requests at the pre-selection rate carry the bits of a real pre-selected crossing;
- plus the chip's minimum 31 BX (0.775 µs) from start of read to first bit.

| Request | Normal-readout utilisation (max module) | Request alone | Request first (pre-emptive) | Request first, non-pre-emptive | Shared FIFO |
|---|---|---|---|---|---|
| jets > 30, narrow windows, HT > 140 (367 kHz) | L1 0.37, L2 0.73, L4 0.97 | 1.88 µs med., p99 2.62 | 1.88 / 2.65 | 2.61 / 4.41 | 3.3 / 34 µs |
| jets > 15, wide windows | same | 1.97 / 2.69 | 1.99 / 2.78 | 2.77 / 4.74 | 3.6 / 40 µs |
| every L1 track (early request) | same | 2.05 / 2.78 | 2.12 / 3.15 | 3.22 / 6.0 | 6.6 / 465 µs |
| jets > 30, uncorrected CMSSW payload | L1 1.07, L2 2.0, L4 2.7 (> 1: impossible, confirms the emulator bug) | 3.96 / 6.1 | | | diverges |

**Requirements for a future chip:**
1. a separate early-trigger latency or tag with retention to the L1 accept;
2. priority of request data over queued normal data (the shared FIFO fails: normal readout already fills the hottest
   module links to 60–97% in this model);
3. a pre-emptive or fine-grained arbitration (non-pre-emptive costs ~0.7 µs);
4. ≤ 38–228 kHz of request commands per module, which is small next to 10 M command frames/s;
5. back-end retention of ~25–200 Gb/s × 12.5 µs ≈ 0.3–2.5 Mbit in total.

Caveats:
- 20 emulated crossings for the normal-readout payload;
- accepted crossings are busier than average (normal load underestimated);
- no Aurora framing (~3%);
- no trigger rules.

## Item 5: compact refit and tag package

All results come from the same chain as the page:
- per-jet b efficiency at 1% / 10% light mistag;
- the HH→4b seed at +2.5 / +15 kHz on top of the HT seeds (share of all SM events);
- in brackets, the share of offline-selectable events.

| Variant | Per jet | Seed +2.5 kHz | Seed +15 kHz | Where |
|---|---|---|---|---|
| Reference (float summary, pixi env) | 47.3 / 77.7 | 77.8 (97.5) | 86.3 (98.8) | `derived/analysis_q8/curves_ref.json` |
| 64-bit word (8 × 8 bit, `PIXSUM=q8`) | 46.9 / 77.5 | 77.6 (97.6) | 86.7 (98.9) | `curves_q8.json`, `tag_chain_q8.json` |
| 10% of pixel clusters lost at random (retrained) | 43.0 / 74.6 | 77.2 (97.1) | 85.7 (98.9) | `derived/curves_hl10.json`, `tag_chain_hl10.json` |
| Barrel layer 1 only, one hit (L1 φ0 fixes the line) | 17.7 / 45.1 | 70.3 (93.9) | 78.1 (97.0) | `derived/curves_L1only.json` |
| Barrel layer 1 only, z window 3 mm | 17.9 / 45.1 | 70.4 (93.4) | 77.9 (96.4) | `derived/curves_L1onlyz3.json` |
| Without barrel layer 1 (earlier) | 39 / 70 | (91 of offline-selectable low mass) | | `tag_chain_variants.json` |
| Today's NN | 15.3 / 36.3 | 69.5 (92.6) | 77.7 (96.3) | |

Reading:
- the word size and moderate hit loss are not issues;
- a single layer is not enough: at PU 200 one hit in a ±1.5 mm × ±15 mm window has no second point to reject a wrong
  cluster, and the gain over the NN shrinks to ~1 point. Why (pT > 30 jets): with one hit the light-jet track |IP| has
a median of 66 um (19 um with the full pixel fit), 29% of light tracks have |IP| > 0.2 mm (7%), and 11% of light jets
have two tracks above 3 sigma (3%). The L1 track direction extrapolated to 2.9 cm (~70-100 um) plus wrong-hit choices
swamp the b-hadron displacement; a second pixel point fixes the local direction.
- **The replaceable layer alone does not carry path A.** At least two fast layers are needed (layers 1 + 2 together,
  or layer 1 + the replaceable TFPX ring 1, which only covers the forward region).

Not done:
- firmware latency and resources (needs an HLS implementation);
- vertex robustness (the L1 vertex is used for the z0 cut);
- the one-hit d0 error (it reuses the multi-hit parametrisation).

## Item 3: low-mass offline selection (internal)

Pending: `offline/offline_lowmass_w.py` (`run_lowmass_w.sh`). Background:
- pT-binned QCD with cross-sections (all 1000 events per file, 558 files);
- real UParT tags on the chosen jets;
- for comparison, the truth-tag probabilities used before;
- n_eff per variant;
- an m_4j sculpting check (4-tag vs 2-medium-tag shape in the window).

## Background for the κλ projection and scouting

Pending: `analysis/kl_qcdbkg.py` (`run_qcdbkg.sh`).

**Production:**
- pixel ntuples of QCD pT 30–470, 250 events per file: OSG cluster 3824054 on submit05, `osg/qcdpt/`, private script
  copies;
- offline jets with generator weight, pT-hat and cross-section: `offline/slurm_offline_w.sh` → `/scratch/.../offline_w`;
- `dump_offline.py` now also writes `genweight`, `pthat`, `xsec`.

**Validation plan:**
1. yields per stream and HT bin, QCD vs minimum bias (QCD lacks pT-hat < 30 and non-QCD processes; the ratio shows
   where QCD is complete);
2. truth-tag vs real UParT 4-/3-tag yields in the window;
3. κλ fits with the QCD background for HT seeds, NN and pixel seeds (thresholds from minimum bias, as scouting.py);
4. Poisson bootstrap of the QCD events: spread of Z_SM, 68% width, and the fraction of replicas where pixel beats NN.

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
- **Background:** pT-binned QCD with generator cross-sections (production complete 2026-10-27 16:00):
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

`offline/offline_lowmass_w.py` (`run_lowmass_w.sh` → `derived/offline_lowmass_w.json`).

Background:
- pT-binned QCD (pT-hat 30–470), 1.22M events, each bin weighted with its generator cross-section to 3000/fb;
- ≥ 4 jets, offline HT 150–800: 251k events;
- the same selection variants as offline_lowmass.py.

Results:
- **Real UParT tags:** the tagged window holds n_eff = 1–13 weighted events (one 30–50 GeV event weighs 7e8), so
  real-tag background ratios are noise (±100%).
- **Truth-tag probabilities** (b 0.84, c 0.12, light 0.01 per jet, every event contributes):

| Variant | κλ information | m_HH < 400 eff. | QCD (truth-tag) | Information-weighted S/√B |
|---|---|---|---|---|
| today (jets > 30, \|m1 − m2\| pairing, window 30) | ×1.00 | 5.3% | ×1.0 | ×1.00 |
| jets > 20, χ² pairing, window 30 (earlier "best") | ×2.11 | 11.9% | ×4.6 | ×0.99 |
| jets > 20, χ² pairing, window 40 | ×2.97 | 16.1% | ×6.7 | ×1.15 |
| jets > 20, χ² pairing, window 50 | ×3.53 | 18.8% | ×9.8 | ×1.13 |

- **This revises the earlier claim.** "2.1× information for 1.4× QCD" came from unweighted QCDFlat. With properly
  weighted QCD the softer selections take in 5–10× more background, and S/√B gains only ~1.0–1.15×.
- The low-mass signal can be accepted, but the multijet background grows as fast. A real gain needs better
  discrimination (tagging or kinematics), not looser cuts.
- Caveats: QCD only (no ttbar), truth tags assume independent jets, and no pT-hat < 30.

## L1 (40 MHz) scouting: what the earlier result really shows (revised after a bug check)

### Bugs in scouting.py's scouting streams

1. **Perfect tags.** The QCDFlat 4-tag fraction is exactly 0, so `background()` substituted a one-minimum-bias-event
   floor (1/2577 of the window, 6e8 events at 3000/fb) in the most sensitive category.
   The earlier "perfect tags: Z 0.24" was set by that floor.
2. **NN working point.** The scan keeps the narrowest-interval working point but defaults to the first (0.2% mistag,
   3.7% b efficiency) when none gives a finite interval. "NN scouting 0.02σ" was not optimised.
3. **Flavour transfer.** Minimum bias has no flavour, so every scouting background used one unweighted QCDFlat tag
   fraction.

### Check with flavour-labelled, cross-section-weighted QCD

`scout_check.py` → `derived/scout_check.json`. QCD pT-hat 30–470, 140k events; L1-jet flavour from generator jets.

**Normalisation.** QCD window yield 2.35e12 vs minimum bias 1.60e12, i.e. ×1.47.
- QCD should be a subset of minimum bias, so this does not close.
- Resolved by `norm_check.py` (→ `derived/norm_check.json`). QCD/minimum bias per L1 HT bin
  (150, 200, 250, 300, 360, 450, 600+):
  - ≥ 4 jets: 1.53, 1.44, 1.46, 1.10, 0.98, 0.94, 1.03;
  - window: 1.50, 1.60, 1.15, 0.92, 2.08 (few events), 1.84, 0.28.
- Above HT 300 it closes. Below, the pT-hat 30–80 bins dominate, and their events are built from pileup jets: in the
  30–50 bin, 25 of 42 window events have ≤ 1 of the 4 leading L1 jets matched to the hard scatter.
- This is double counting by construction. "One hard scatter + 200 minimum-bias" counts a crossing once per hard
  scatter it contains, and pT-hat 30–50 scatters occur ~0.3 times per crossing.
- Rule: below L1 HT 300 take normalisation and shape from minimum bias, flavour from QCD; above 300 QCD can stand alone.
- It also explains the triggered menu's Z = 1.07 with the QCD background vs 1.61 with minimum bias.

**Genuine 4b QCD in the window.** 1 simulated event (QCDPt120) → fraction 2.4e-5 ± 100%; 3 true b: 3.3e-4 (9 events).
The 4b background cannot be measured with this sample.

| Scouting tags | All crossings, Z | Menu-rejected part, Z | Menu + menu-rejected scouting |
|---|---|---|---|
| perfect | 0.56 (direct) – 0.76 (factorised) | 0.09 | 1.07 → 1.07 |
| NN, 5% light mistag (b eff ~35%/jet) | 0.06–0.10 | 0.04–0.05 | 1.07 → 1.07 |
| NN, 0.2% / 1% mistag | S = 50 / 126 events, B unmeasurable (0 QCD events) | | |

### Reading

- **Realistic L1 taggers.** Hopeless in scouting: a 4-tag requirement at mistags that suppress the 1e12 window
  background leaves (b eff)^4 of a few % of the signal.
- **Perfect tags.** The ceiling is not determined. It rests on the genuine-4b QCD rate in the window, which this sample
  measures with one event; pileup b jets (no generator record) are missing on top.
- **Expert intuition.** It can only be tested with a 4b-enriched QCD sample (generator-level bbbb or a b-enriched
  filter) at L1 HT 150–360.

**4b-enriched private sample (2026-10-28).**
- Generation: `privgen/fragments/QCD4b_fragment.py`. Pythia8 CP5, HardQCD:all, pT-hat > 30 with a pT-hat^4.5 bias
  (event weights).
- Filter: ≥ 4 last-copy b quarks with pT > 15, |eta| < 2.6, applied before SIM.
- GEN test: filter efficiency 1.35e-3 (unweighted), 52 ms per generated event → ~180 s per accepted event through
  GEN-SIM-DIGI (PU 200) and the ntuples.
- Jobs: `run_privgen_4b.sh` + `slurm_privgen_4b.sh` record the generated count, the cross-section before the filter and
  per-event weight / pT-hat (`dump_genweight.py`).

### First result with the 4b-enriched sample (2026-10-28, 825 accepted events from 131 jobs)

`scout4b.py` → `derived/scout4b.json`. Background composition:
- genuine 4b from QCD4b;
- everything else from pT-binned QCD without its genuine-4b events;
- yields below L1 HT 300 scaled to minimum bias (double counting).

**Genuine 4b in the window:** 3.5e7 events at 3000/fb, i.e. 2.2e-5 of the window yield.
- Built from 4 events (n_eff 2.8); pT-hat median 109 GeV, 10–90%: 90–187 GeV.
- The pT-binned QCD's single event gave 5.7e7, consistent.
- Only 0.5% of the filtered events land in the window with 4 b-matched leading L1 jets: the b-quark filter is loose, and
  only 26% of accepted events have ≥ 4 b generator jets.

| Scouting tags | All crossings, Z | Menu-rejected, Z | Menu (QCD bkg) 1.07 + menu-rejected scouting |
|---|---|---|---|
| perfect | 0.71 (B 7.2e8, 4-tag 3.5e7) | 0.30 (B 6.5e8, 4-tag 2.9e7 from 3 events) | 1.11 |
| NN 5% mistag | 0.06 | 0.04 | 1.07 |
| NN 0.2% / 1% | S = 43 / 126, no QCD event passes | | 1.07 |

**Reading.**
- Even perfect b-tagging at 40 MHz adds ~0.04σ (×1.04) to the HT seeds.
- The 3-tag category (3 true b among the 4 leading jets: 6e8 events, pT-binned QCD) dominates the background of the
  rejected events.
- A 4-tag background lower by 2σ (×4) would raise the rejected-event Z to ~0.6 and the sum to ~1.2: modest either way.

**Open:**
- full statistics (~3300 accepted events);
- pileup b jets (no generator record): a lower bound on the background;
- pT-hat < 30;
- L1-jet resolution sets the window width; an "offline-quality kinematics" ceiling has not been run.

### Full statistics (2026-10-28, 2599 accepted events from 396 jobs; first result kept as `scout4b_825ev.json`)

**Genuine 4b in the window:** 5.1e7 events at 3000/fb (3.1e-5 of the window yield).
- 15 events, n_eff 8 (±35%); pT-hat median 114 GeV, 10–90%: 83–180 GeV.
- The pT-binned QCD's single event gave 5.7e7.

| Scouting tags | All crossings, Z | Menu-rejected, Z | Menu 1.07 + menu-rejected scouting |
|---|---|---|---|
| perfect | 0.60 (B 7.3e8, 4-tag 5.1e7) | 0.24 (B 6.7e8, 4-tag 4.8e7 from 13 events) | 1.10 |
| NN 5% mistag | 0.06 | 0.04 | 1.07 |

**Conclusion (lower bound on the background: pileup b jets unlabelled; pT-hat > 30 only).**
- With L1-object kinematics, even perfect b-tagging at 40 MHz adds ~3% to the HH→4b sensitivity of the HT seeds.
- Realistic L1 tags add nothing.
- The rejected events' background is dominated by 3-true-b crossings (~6e8), not by genuine 4b.
- Untested ceiling: offline-quality kinematics (narrower window) together with perfect tags.

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

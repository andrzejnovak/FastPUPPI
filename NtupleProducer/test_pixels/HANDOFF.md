# L1 pixel b-tag pilot: handoff (2026-10-25)

Question: would pixel information in the Phase-2 L1 jet tagger help HH→4b, and could L1 get it in time?
Collaborator: Marc Huwiler. Audience: PI + an undergrad who may take it over.

## Findings (all Phase2Spring24 PU 200)

1. **Pixels make a much better L1 b-tagger, and L1 tracks can collect the hits.** b-eff at 1% / 10% light mistag
   (HH→4b b jets vs QCD light, L1 jets pT > 15):
   L1 NN 15/35 → + Outer-Tracker-only displaced tracks 19/44 → **+ L1 tracks extended into the pixels 47/78** →
   + HLT pixel tracks 50/76 (offline UParT 84/94, other jets, reference). The extension (`analysis/l1ext.py`) picks
   hits along each L1 track out of ~58k clusters: 87% hit purity, d0 within 36 µm of HLT pixel tracks.
2. **Trigger level gain is real:** planned menu + 2.5 kHz seed keeps 69.5% (NN) → 77.8% (pixels) of all SM events.
3. **Analysis level, SM HH→4b: small, ×1.05–1.11** (offline 4b + 3b, UParT, b-response corrected masses). Only 7.9%
   of signal passes the offline selection; the planned menu + NN seed already keeps 93% of it. Even a perfect L1 b-tag
   gives ×1.08. The loss is offline (acceptance, b-tags, pairing), not in the trigger.
4. **Where it pays:** soft / low-m_HH events (κλ = 5: ×1.2–1.5 after selection) and rate: on top of the menu the pixel
   seed matches the NN seed's +2.3 kHz efficiency with ~0.3 kHz; standalone 2.7 vs 9.6 kHz.
5. **Bit budget** (minimum bias, pre-selection HT > 140 / 200 GeV = 367 / 123 kHz): 15–18 requesting tracks,
   ~14 clusters per narrow track window → hits back ~2.7 / 1.2 Gb/s (whole-cone readout 32 / 12 Gb/s). Tagger:
   +1 sign bit per candidate (reuse 8-b √|dxy| field) or a 64-b jet summary; GT jet word unchanged.

Open: whether pixel front-ends can answer a regional request mid-latency (needs pixel experts); firmware cost;
HLT emulation (can only lower the gain); a real b-jet regression; κλ sensitivity from an m_HH-shape fit.

## Pages

- Four-tab summary: `analysis/page/build_tabs.py` → `tabs.html`; run it in `/work/submit/novaka/l1pixels/pilot_page/`
  (reads `index.html` there for styles and diagrams, and `../analysis/plots_page/*.png` from `make_page_plots.py`).
  Built copy: `/work/submit/novaka/l1pixels/pilot_page/tabs.html`; published at
  https://claude.ai/artifact/MNbp8sYBCxz1SHwPvfdN3h (private; share from the page's Share menu).
  `analysis/event_display.py <HH4b ntuple> plots_page/event_display.png` makes the tab-3 display
  (local_v3/perfNano_HH4b_0.root picks event 1, track 27).
- Long-form pilot page: `analysis/page/index.html`, published as v16 at
  https://claude.ai/artifact/NFjQ7pzKxoXA1qj6SThpJr (shared with the organization). Older: project page 9q5PSiwbxrxW7XKmDVXA7v, info budget
  Xyx1BCt4asM2djsQNvVxvL.

## Where things are (subMIT)

| What | Path |
|---|---|
| Working areas | `/work/submit/novaka/l1pixels/` (`analysis/`, `offline/`, `mbsel/`, `local/`, `pilot_page/`, `review/`, `docs/`) |
| CMSSW | `/work/submit/novaka/l1pixels/{ngv2,hitdev}/CMSSW_17_0_0_pre2` (ngv2: production; hitdev: python env) |
| Extended ntuples (clusters, L1 tracks, vertex, PUPPI cands) | `/ceph/submit/data/user/n/novaka/l1pixels/local_v3` (HH4b, QCDFlat; 21k each) |
| Minimum bias with pixels | `.../local_mbsel_ext` (23,411 official events, L1 HT > 90) + `.../local_mbnew` (97,320 new, stored HT > 60); out of 1,999,360 total |
| Offline jets (MINIAOD) | `.../offline/{HH4b,QCDFlat}_*.npz` |
| Gen m_HH | `.../genmhh/mhh_*.npz`; κλ shapes `analysis/klreweight/nano_mhh_kl*.npz` |
| Key results | `analysis/curves.json` (+`curves_flags.npz`), `direct_rate2.json`, `direct_rate_l1ext.json`, `tag_chain.json`, `offline_flags2.npz`, `bits_mb.json` |

All scripts carry absolute `/work`, `/ceph` paths; run from `analysis/` with
`source /cvmfs/cms.cern.ch/cmsset_default.sh; cd .../hitdev/CMSSW_17_0_0_pre2/src; cmsenv`. Production on Slurm
(`submit` partition) only, never on the login node.

## Pipeline

| Step | Script(s) | Runner |
|---|---|---|
| Ntuples with clusters + L1 tracks | `step1_cfg.py clusters=True`, `step2_cfg.py extended=True` | `production/local/slurm_array_v3.sh` |
| MB preselection (stored 14_0 L1 HT) | `production/mbsel/scan_ht.py`, `select_new.py` | `slurm_scan.sh`, `run_mbnew.sh` |
| Per-jet lists, HLT pixel tracks | `analysis/make_lists.py` (`JET_PTMIN=15`) | `run_direct2.sh` |
| Per-jet lists, L1 tracks + pixels / OT only | `analysis/make_l1ext_lists.py` (`MODE=otonly`) | `run_l1ext_lists.sh`, `run_ot_lists.sh`, `merge_lists.py` |
| Association validation / settings | `l1ext_validate.py` | `run_l1ext_scan.sh` |
| Direct rate test, κλ split | `direct_rate.py`, `kl_direct.py` (`SEL=offline_flags2.npz:resolved_4b`) | `run_l1ext_direct.sh`, `run_offline2.sh` |
| Efficiency vs rate, perfect tag | `direct_curves.py` | `run_curves.sh` |
| Offline jets + selection | `analysis/offline/dump_offline.py`, `offline_sel.py` | `slurm_offline.sh` |
| Tagging chain ROC | `tag_compare.py` | `run_tagcmp.sh` |
| Bit budget | `bits_budget.py` | `run_bits.sh` |
| Plots, page | `make_page_plots.py`, `event_display.py`, `page/build_tabs.py` | — |

Earlier pilot steps (seed scan, learning curves, hit regression, MB mistag) are in `l1_seed.py`, `train_sets.py`,
`regress_hits.py`, `mb_mistag.py` and their `run_*.sh`.

## Gotchas

- L1 track curvature sign: `l1ext.CURV_SIGN = +1` (−1 gives 31% purity). Displaced-track d0 has the opposite sign to
  the CMS dxy convention (flipped in `MODE=otonly`); keep |d0| < 1 cm there.
- Offline PUPPI b jets have response 0.73 (25 GeV) → 0.96 (150 GeV); without the correction the Higgs candidates
  peak at ~105 GeV (`offline/b_response.json`).
- Stored 14_0 L1 HT in MinBias RAW runs low vs our emulation; MB rate scans use HT cuts ≥ 150 (`HT_MIN=150`).
- `direct_rate.py` thresholds are chosen on even events and quoted on odd ones; MB weight uses `MB_TOTAL=1999360`.
- The `doppio` Slurm jobs (F1r_tt_*, G5_tt_*) and the `claude-rc` jobs on this account are not part of this project.

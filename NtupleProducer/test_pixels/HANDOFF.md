# L1 pixel b-tag pilot: handoff (2026-10-26)

Question: would pixel information in the Phase-2 L1 jet tagger help HH→4b, and could L1 get it in time?
Collaborator: Marc Huwiler. Audience: PI + an undergrad who may take it over.

## Findings (all Phase2Spring24 PU 200)

1. **Pixels make a much better L1 b-tagger, and L1 tracks can collect the hits.** b-eff at 1% / 10% light mistag
   (HH→4b b jets vs QCD light, L1 jets pT > 15):
   L1 NN 15/35 → + Outer-Tracker-only displaced tracks 19/44 → **+ L1 tracks extended into the pixels 47/78** →
   + HLT pixel tracks 50/76 (offline UParT 84/94, other jets, reference). The extension (`analysis/l1ext.py`) picks
   hits along each L1 track out of ~58k clusters: 87% hit purity, d0 within 36 µm of HLT pixel tracks.
2. **The gain sits at low m_HH, where κλ is measured.** 78% of the κλ information near the SM (per-bin
   (∂s/∂κλ)²/s from the Run-3 κλ shapes) is below m_HH = 400 GeV. There, of offline-selected events (4b + 3b), L1 keeps
   60% (Run-3-style menu) → 83% (+2.5 kHz NN seed) → **96% (+2.5 kHz pixel seed)**, perfect tag 99.5%; spending the
   2.5 kHz on lower HT cuts instead gives 63%. A pixel seed at +1 kHz keeps as much as the NN seed at +15 kHz.
   (`make_page_plots.py` sections 9–13, `ht_control.py`, `seed_plane.py`.)
3. **Total SM yield: small, ×1.05–1.11** (offline 4b + 3b, UParT, b-response corrected masses): only 7.9% of signal
   passes offline and the NN seed already keeps 93% of it (perfect tag ×1.08). At low m_HH only 1–6% pass offline.
4. **Softer offline makes L1 bite again** (`offline/offline_scenarios.py`, `scen_ana.py`): 20 GeV jets, looser tags,
   40 GeV window (23% of signal selected): low-m_HH events kept 70% (NN) → 85% (pixels) → 96% (perfect). The pixel
   seed keeps ×1.26–1.30 the κλ information of the NN seed in every scenario. Background not modelled.
   Rate: the pixel seed matches the NN seed's +2.3 kHz efficiency with ~0.3 kHz on top of the menu (standalone 2.7 vs
   9.6 kHz), but that is ~1% of the TDR menu (346 kHz, 450 with margin, of 750): the case is efficiency, not bandwidth.
5. **Bit budget** (minimum bias, pre-selection HT > 140 / 200 GeV = 367 / 123 kHz): 15–18 requesting tracks,
   ~14 clusters per narrow track window → hits back ~2.7 / 1.2 Gb/s (whole-cone readout 32 / 12 Gb/s). Tagger:
   +1 sign bit per candidate (reuse 8-b √|dxy| field) or a 64-b jet summary; GT jet word unchanged.

Open: whether pixel front-ends can answer a regional request mid-latency (needs pixel experts); firmware cost;
HLT emulation (can only lower the gain); a real b-jet regression; a κλ interval from an m_HH-shape fit (needs a
background model after the 4b selection).

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
| Extended ntuples (clusters, L1 tracks, vertex, PUPPI cands) | `/scratch/submit/cms/novaka/l1pixels/local_v3` (HH4b, QCDFlat; 21k each) |
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

## Pixel link archaeology (preliminary)

`itlinks/`: `run_bits.sh` (Slurm) runs CMSSW's chip-output emulator (`Phase2ITQCoreProducer`, `bitstream_cfg.py`) on
PU 200 RAW digis, `dump_bits.py` stores bits per chip, `occupancy.py` maps them to lpGBT links with the tkLayout cabling
map (`CMSSWCablingMap__OT800_IT700.csv`) → `occupancy.json`. Findings: 2.4e7 bits per crossing (~130 b per cluster,
3× the bit-budget assumption); a request returns a whole chip (median 1.1 kbit, p99 ~8 kbit: ~1–6 µs on one
1.28 Gb/s e-link); the real e-link configuration is not in CMSSW (a naive 8.96 Gb/s/lpGBT model gives >100%
occupancy). Prompt L1 tracks carry d0 = 0 (13-b field empty); the NG tagger runs on the extended (displaced-track)
chain, so a pixel-refit d0 could fill the existing field.

## Beyond HH→4b (2026-10-26, page tab 6)

- **Charm:** pixels make L1 charm tagging possible: c efficiency at 10% light mistag 16% (NN) → 29% (L1 tracks + pixel
  hits), c vs b at 30% b: 41% → 61% (`analysis/ctag_compare.py`, `run_ctag.sh` → `ctag_chain.json`; QCD jets).
- **VBF H→cc / bb:** the planned menu keeps only 57% / 53% of events in a generator VBF + cc/bb acceptance
  (`analysis/vbf_menu.py`). A looser VBF pair + two tagged central jets at ~+2 kHz on top of the menu
  (`analysis/vbf_ctag.py`, `run_vbf_ctag.sh WHICH=cc|bb`, minimum bias `local_mbsel_ext` + `local_mbnew` + `local_mbvbf`):
  cc 58 → 61% (NN) / 62% (pixels); bb 51 → 56% / 61%; looser VBF thresholds alone ~+1 point. Charm is limited by the
  c-tag (29% at 10% light mistag with the b-oriented summary).
- **Run-3 VBF H→cc HLT paths** (in CMSSW `HLT_GRun_cff.py`): `HLT_QuadPFJet{100_88_70_30,105_88_75_30,111_90_80_30}_
  PNet1CvsAll{0p5,0p6}_VBF3Tight`, L1 seeded by Run-3 VBF/multijet/HT seeds (no flavour), ≥1 central CvsAll > 0.5,
  m_qq > 460, |Δη_qq| > 3.5. No VBF or charm path in the Phase-2 HLT menu (`HLT_75e33`).
- **Boosted ggH and ZH(νν) are not L1-limited** (full private samples, ~5k events each): menu keeps 98–100% of ggH with
  Higgs pT > 200 (`fatjet_parts.py`, `fatjet_ana.py`) and 96–98% of ZH with generator MET > 150 (`zh_met.py`).
  Large-jet mass from PUPPI constituents works (merged H→cc ~125 GeV). Private samples: `production/privgen/`.
- **Menu rates vs TDR (CMS-TDR-021, PU 200):** our emulation HT + quad-jet 19 kHz (TDR 20), DoubleJet112 95 (71),
  VBF 22 (40). Added-rate comparisons are unaffected.
- **OSG** (`production/osg/`): works for CMS xrootd inputs only with `X509_CERT_DIR`/`X509_VOMS_DIR` from cvmfs (in the
  runners; without them xrootd falls back to tokens: "Auth failed"). Exclude FANDM-ITS and SU-ITS for the private
  production. `sweep_held_mb.sh` moves held OSG jobs to Slurm.
- **Data** lives on CMS scratch, `/scratch/submit/cms/novaka/l1pixels/` (not backed up; everything is regenerable
  from the recipes here; the old /ceph copy is deleted). In the working `analysis/` folder every data file and output
  folder is a symlink into `.../l1pixels/derived/analysis/`; new outputs go to `.../derived/`.
- **Batch:** when the `submit` partition is congested, `tier3` is often idle, but its CPUs cannot run the CMSSW 17
  python ("Illegal instruction"): use the pip venv `/work/submit/novaka/tools/ana-venv` there (the `run_*.sh` for
  `vbf_ctag`, `seed_plane`, `ht_control`, `fatjet_parts`, `zh_met`, offline scenarios do).

## Gotchas

- L1 track curvature sign: `l1ext.CURV_SIGN = +1` (−1 gives 31% purity). Displaced-track d0 has the opposite sign to
  the CMS dxy convention (flipped in `MODE=otonly`); keep |d0| < 1 cm there.
- Offline PUPPI b jets have response 0.73 (25 GeV) → 0.96 (150 GeV); without the correction the Higgs candidates
  peak at ~105 GeV (`offline/b_response.json`).
- Stored 14_0 L1 HT in MinBias RAW runs low vs our emulation; MB rate scans use HT cuts ≥ 150 (`HT_MIN=150`).
- `direct_rate.py` thresholds are chosen on even events and quoted on odd ones; MB weight uses `MB_TOTAL=1999360`.
- The `doppio` Slurm jobs (F1r_tt_*, G5_tt_*) and the `claude-rc` jobs on this account are not part of this project.

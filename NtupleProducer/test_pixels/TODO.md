# L1 pixel pilot: to do

- [x] Code/data split (2026-10-26): every data file and output folder in `analysis/` is a symlink into
      `/scratch/submit/cms/novaka/l1pixels/derived/analysis/` (copied, verified file by file); `/work` keeps code only.
- [x] Boosted H→cc first pass (2026-10-26, `analysis/fatjet_parts.py`, `fatjet_ana.py` → `fatjet_ana.json`): constituent
      mass works (merged H→cc jets peak at ~125 GeV for H pT > 250, minimum bias ~23 GeV), but the planned menu
      (SingleJet230 | HT450) already keeps 98–100% of ggH events with H pT > 200 (74% at 100–150, 93% at 150–200).
      Boosted ggH→cc is HLT-limited, not L1-limited. Rerun on the full private samples (~5k events each): unchanged.
      R = 0.8 pixel summary only if the 100–200 GeV region turns out to matter.
- [x] VBF H→cc/bb rate side (2026-10-26, `analysis/vbf_ctag.py` → `vbf_ctag_{cc,bb}.json`): at ~+2 kHz on top of the
      menu, pixel-tagged VBF seed 58 → 62% (cc), 51 → 61% (bb); today's NN 61% / 56%; looser VBF without tag ~+1 point.
- [x] Menu rates vs the TDR table (CMS-TDR-021, PU 200; 2026-10-26): ours HT + quad-jet 19 kHz (TDR 20), DoubleJet112
      95 (71), VBF 22 (40). Whole TDR menu 346 kHz (450 with margin) of 750: saving a few kHz on HH→4b is ~1%, so the
      case is efficiency at fixed rate, not bandwidth. Offsets explained (`rate_check.py`, stored 14_0 jets of all
      2M events): DoubleJet 72 kHz = TDR; 17_0 jets ~6% higher response; the TDR VBF seed is defined differently.
- [x] ZH(νν) H→bb/cc (2026-10-26, `analysis/zh_met.py` → `zh_met.json`, first 22 files): the menu keeps 96–98% of
      fiducial events with generator MET > 150 (PuppiMET200 alone 93–95%); 82% at 100–150. Not L1-limited for the
      standard 0-lepton selection; full samples (50 files each) give 96% / 98%.
- [x] Charm-oriented pixel summary (2026-10-26, `charm_feats2.py`, `ctag_charm.py`): a charm word alone adds nothing;
      recalibrating the IP resolution (`l1ext.D0_ERR` ~3x too large) + 3D significance + charm word: 29 → 33.5% at 10%
      light. VBF H→cc seed unchanged (62%).
- [x] Recalibrated impact parameter in the HH→4b seed (2026-10-27, `PIXSUM=v2|v2xy`): per-jet 48/78 → 55/83%, but the
      seed at fixed rate gets worse with the z term (pileup jets in minimum bias) and +0.8 points with the transverse
      part only; page keeps the original summary. Open: pileup-robust z0 use (per-track vertex association).
- [x] BSM truth in the κλ fit (κλ = 5: SM excluded 2.0σ NN → 3.7σ pixel) and the HT reach of scouting (`hh_ht_reach.py`:
      ≤ 6% of windowed signal below L1 HT 150).
- [x] Generator-boson table (2026-10-27): opt-in `step2_cfg.py genBosons=True` (`addGenBosons()`: H, Z, W last copy with
      daughter pdgIds); tested on HH4b (2 x H->bb), ZH(nunu), ggH(bb); default/extended outputs unchanged. To use in
      private production: add `genBosons=True` to the step2 line of `privgen/run_privgen.sh` (atomic replace only).
- [x] HH→4b reframed around low m_HH (2026-10-26): κλ-information weighting (78% below 400 GeV), lower-HT control
      (`ht_control.py`), thesis-style plots (`seed_plane.py`, `make_page_plots.py` sections 9–13), softer offline scenarios
      (`offline/offline_scenarios.py`, `scen_ana.py`): pixel seed keeps ×1.26 the κλ information of the NN seed in every
      scenario; with the softest selection L1 bites (pixel 85%, perfect 95%).
- [x] κλ interval with background (2026-10-26, `scouting.py`, page tab 7): L1-object level, minimum-bias background with
      QCD 4b/3b fractions; stat-only 68%: NN [0.43, 1.90] → pixel [0.53, 1.75]. Open: systematics, offline resolution.
- [x] Scouting prototype (same script): L1-only 4b scouting Z 0.26 vs 2.0 triggered, adds nothing on top of the trigger.
- [x] Scouting as a fallback for real-time pixel tagging (2026-10-27, tab 7): recovers nothing (menu 1.61 → 1.61σ).
- [ ] Background flavour content for seed-added events: minimum bias has no flavour truth; QCDFlat has 27–49 events in
      the seed-added class. Need a QCD (or b-enriched) sample at L1 HT 150–400, or the HH→4b group's background model,
      to settle pixel vs NN at analysis level (models A/B in tab 7).
- [x] Perfect-tag ceiling with a flavour-aware rate (2026-10-27, `perfect_ceiling.py`): 92.6 → 82.2% of all events at
      +2.5 kHz; 99.5 → 98.9% of offline-selected below 400 GeV. Still an upper bound (pileup b jets unlabelled).
- [x] Analysis environment moved to pixi (`analysis/pixi.toml`); CMSSW only for production and FWLite.

## Page plots we want but lack the inputs for (2026-10-27 page overhaul)
- [ ] κλ scan at offline resolution with a real background model (needs the HH→4b group's background model, or a large
      QCD / b-enriched sample at L1 HT 150–400 to fix the flavour content of seed-added events: models A/B on the page).
- [ ] Rate case for other b-rich channels (ttH(bb), bbH, Z'→bb, HH→bbττ): needs those Phase-2 samples with pixel tables.
- [ ] Readout latency per crossing with the real IT e-link configuration (pixel DAQ input; CMSSW has no e-link map).
- [ ] Gains after an HLT emulation (can only lower them).
- [ ] Firmware latency and resources of the track extension (FPGA study).
- [ ] Same-definition comparison with the published CMS b-tag NN seed (PoS(ICHEP2022)639, fig. 4: NN @ 15 kHz vs
      QuadJet+HT @ 11 kHz vs m_HH).


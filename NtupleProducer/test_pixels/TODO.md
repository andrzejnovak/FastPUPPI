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
      case is efficiency at fixed rate, not bandwidth. Open: understand the DoubleJet/VBF offsets (14_0 vs 17_0 jets).
- [x] ZH(νν) H→bb/cc (2026-10-26, `analysis/zh_met.py` → `zh_met.json`, first 22 files): the menu keeps 96–98% of
      fiducial events with generator MET > 150 (PuppiMET200 alone 93–95%); 82% at 100–150. Not L1-limited for the
      standard 0-lepton selection; full samples (50 files each) give 96% / 98%.
- [ ] Charm-oriented pixel summary (moderate-significance track counts, vertex mass) to push the c-tag beyond 29%.
- [ ] Generator-Higgs table in the ntuples for future private samples (now a proxy from generator jets).
- [x] HH→4b reframed around low m_HH (2026-10-26): κλ-information weighting (78% below 400 GeV), lower-HT control
      (`ht_control.py`), thesis-style plots (`seed_plane.py`, `make_page_plots.py` sections 9–13), softer offline scenarios
      (`offline/offline_scenarios.py`, `scen_ana.py`): pixel seed keeps ×1.26 the κλ information of the NN seed in every
      scenario; with the softest selection L1 bites (pixel 85%, perfect 95%).
- [ ] κλ interval from an m_HH-shape fit: needs a background model after the 4b selection (HL-LHC HH→4b projection or a
      3b-based estimate); the page quotes the signal-dominated limit.

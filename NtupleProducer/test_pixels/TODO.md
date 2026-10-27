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
- [ ] Propagate the recalibrated 3D impact parameter (b tag 48/78 → 55/83% at 1/10% light, `btag_v2check.py`) to the
      HH→4b seeds (`seed_plane.py`, `direct_curves.py`, `scouting.py`) and the pages.
- [ ] Generator-Higgs table in the ntuples for future private samples (now a proxy from generator jets).
- [x] HH→4b reframed around low m_HH (2026-10-26): κλ-information weighting (78% below 400 GeV), lower-HT control
      (`ht_control.py`), thesis-style plots (`seed_plane.py`, `make_page_plots.py` sections 9–13), softer offline scenarios
      (`offline/offline_scenarios.py`, `scen_ana.py`): pixel seed keeps ×1.26 the κλ information of the NN seed in every
      scenario; with the softest selection L1 bites (pixel 85%, perfect 95%).
- [x] κλ interval with background (2026-10-26, `scouting.py`, page tab 7): L1-object level, minimum-bias background with
      QCD 4b/3b fractions; stat-only 68%: NN [0.43, 1.90] → pixel [0.53, 1.75]. Open: systematics, offline resolution.
- [x] Scouting prototype (same script): L1-only 4b scouting Z 0.26 vs 2.0 triggered, adds nothing on top of the trigger.

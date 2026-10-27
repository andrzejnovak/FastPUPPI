You are a senior CMS Phase-2 trigger/tracking physicist (second PI) auditing the CONCLUSIONS of a pilot study before it
goes to a PI. Read-only: do not modify anything. Be candid and specific; no filler.

Read first: page_text.html (the current summary page, figures replaced by alt text; every figure has a "How this was made"
list naming scripts and inputs), then the handoff /work/submit/novaka/l1pixels/ngv2/CMSSW_17_0_0_pre2/src/FastPUPPI/NtupleProducer/test_pixels/HANDOFF.md,
then check the code and results it points to. Working copies: /work/submit/novaka/l1pixels/analysis (scripts; data files are
symlinks into /scratch/submit/cms/novaka/l1pixels/derived), /work/submit/novaka/l1pixels/offline, /work/submit/novaka/l1pixels/itlinks.

CONCLUSIONS TO AUDIT (verify each against code and results; say whether it is supported, overstated, understated or wrong):
A. The gap: planned HT seeds (PuppiHT450 | PuppiHT400+QuadJet70_55_40_40, 19 kHz) miss 40% of SM HH->4b, 64% below
   m_HH = 400 GeV. (plot_gap.py, curves_flags.npz)
B. Today's NN tagger already uses 5-parameter (displaced) Outer-Tracker tracks; their d0 resolution ~545 um makes it weak
   (15% b eff at 1% mistag). (CMSSW L1TPFJetsExtendedTask; tag_compare.py, tag_chain.json; l1ext_validate.py)
C. Path A (L1 tracks extended into the pixel layers, refit, 8-number summary): 47% b eff at 1%; pixel seed +2.5 kHz keeps
   78% of all SM events vs 70% (NN), 96% vs 83% of offline-selectable events below 400 GeV; +15 kHz 86/78%, 99/93%.
   (l1ext.py, make_l1ext_lists.py, direct_curves.py, make_story_plots.py)
D. Perfect-tag ceiling: minimum bias carries no flavour truth, so its rate comes from QCD P(n_b | HT) (perfect_ceiling.py).
E. kappa_lambda fit at L1-object level with minimum-bias background and QCD 4b/3b fractions (scouting.py, qcd_tagfrac.py):
   pixel seed ahead of the NN at +2.5 kHz (68%: 0.45-1.93 vs 0.38-2.03); ~+-0.1 sigma precision from minimum-bias statistics.
   Background-model history: one inclusive QCD fraction (model A), per-L1-class fractions from 27-49 QCD events (model B,
   judged a small-sample artefact), now QCD binned in seed score + seed-score categories. Is the current model sound?
F. Path B (pixel tags only in 40 MHz L1 scouting) adds no sensitivity; lower m_HH not reachable (only 1.8-5.6% of
   windowed signal below L1 HT 150); it would still need the regional pixel readout. (scouting.py, hh_ht_reach.py)
G. Readout: a region-of-interest request must read whole pixel chips: ~68 chips, 73 / 28 Gb/s at HT > 140 / 200, ~9 us per
   crossing on one 1.28 Gb/s e-link per chip (barrel layer 1 dominates); 4 lanes -> 2.3 us median, 30% above 2.5 us.
   (chip_readout.py, chipgeo.py, chip_geom.py, chip_readout_merge.py, itlinks/). Check geometry, calibration, window
   definition (all layers?), the e-link assumptions, and whether "infeasible in the latency budget" is the right reading.
   Also: are there feasibility effects we miss (trigger/command distribution to chips, destructive readout vs the later
   L1 accept, chip buffer depth, CROC data format / lanes per chip in TBPX L1, DTC/back-end aggregation, time-multiplexing)?
H. Offline selection: the mock selection loses low m_HH (jets > 30, |m1-m2| pairing); jets > 20 + chi2 pairing doubles the
   kappa_lambda information for 1.4x QCD (offline/offline_lowmass.py; QCD proxy unweighted QCDFlat).
I. Rate case: a pixel-tagged standalone multijet seed matches the HT seeds' HH->4b efficiency at 3.4 kHz (NN 13.7, HT only
   21.4); at ~20 kHz the HT cut drops 340 -> 170 GeV (rate_case.py on seed_plane.npz).
J. Recalibrated 3D impact parameter improves per-jet tagging but worsens the seed (pileup); charm: 16 -> 29 -> 34% c eff.

DELIVER (markdown, print as your final answer):
1. For each of A-J: verdict (supported / overstated / understated / wrong / cannot verify), the evidence (file:line or
   number), and the fix.
2. The limitation claims (F, G, and the kappa_lambda precision in E) deserve the most scrutiny: are we too pessimistic or
   too optimistic about what cannot be delivered? What would change the verdict?
3. Any bug, inconsistency or methodological flaw you find anywhere (ranked by impact on the conclusions).
4. Given the limitations, what could this group realistically DELIVER (to CMS L1 / HLT / HH or other analyses) with the
   tools and samples they have, even if not HH->4b at L1? Rank by value and effort.

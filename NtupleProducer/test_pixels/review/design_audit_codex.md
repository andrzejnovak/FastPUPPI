A first-year student will grasp “pixels improve b tagging,” but not the complete argument within ten seconds per section. (`shots/tab1_hh_00.png`, `shots/tab2_how_00.png`)  
The strongest features are the numbered story, consistent page layout, and captions that often state a result. (`shots/tab1_hh_01.png`, `shots/tab4_rate_01.png`)  
**Obstacle 1:** percentages switch between all events, low-mass events, offline-selectable events, and self-coupling information. (`figures/recovery.png`)  
**Obstacle 2:** essential definitions and qualifications are hidden, while implementation details occupy the main reading path. (`shots/tab1_hh_02.png`, `shots/tab3_flow_01.png`)  
**Obstacle 3:** several headlines overstate the evidence, and some figures disagree with the surrounding numbers or method. (`shots/tab1_hh_03.png`, `figures/seed_plane.png`)

**Tab 1 — HH→4b.** The likely ten-second takeaway is “the trigger loses many events; pixels almost solve the problem; scouting is useless.” The intended takeaway needs three qualifications: the NN already recovers some events; pixels recover additional low-mass signal at fixed added rate; improved self-coupling sensitivity remains background-dependent. The verdict arrives too late to establish these distinctions. (`shots/tab1_hh_00.png`, `shots/tab1_hh_01.png`, `shots/tab1_hh_03.png`)

- **Define on first use:** *menu* = collection of trigger selection rules; *seed* = one rule that can accept an event; *NN* = neural network; *HT* = sum of jet transverse momenta; *mHH* = invariant mass of the Higgs pair; *κλ* = Higgs self-coupling relative to the Standard Model, where 1 is the SM value. (`shots/tab1_hh_00.png`, `shots/tab1_hh_01.png`)
- **Explain the denominators:** “offline 4b + 3b” means events that would pass the later analysis’s four-tag or three-tag selections—not events already recovered by offline processing. “κλ information” is a signal-only sensitivity measure here, not the final precision including background. (`shots/tab1_hh_00.png`, `figures/recovery.png`; `page_text.html`, first methods toggle)
- **Simplify the statistics vocabulary:** *minimum bias* = broadly sampled collisions used to estimate background and rate; *QCD background* = ordinary strong-interaction jet production; *Asimov* = expected data without random fluctuations; *second minimum* = another coupling value compatible with the expected data. Define model A as using a common background flavour fraction and model B as estimating it separately for existing and newly accepted events. (`shots/tab1_hh_02.png`; `page_text.html`, self-coupling methods toggle)

| Figure | At a glance? | Single most useful change |
|---|---|---|
| `figures/gap_mhh.png` | Partly. Red losses are clear, but four panels combine event counts, percentages and information; the long title shrinks substantially on the page. | Put “Below 400 GeV: 64% of signal missed” directly over the shaded region. |
| `figures/recovery.png` | Closest to an effective summary, but filled/open symbols change meaning between panels. The right title does not reveal that the event points are low-mass only. | Replace the changing marker meanings with separately labelled rows for each population. |
| `figures/mhh_eff.png` | Too much for ten seconds: six panels, five trigger choices, two ratios and a long legend. | Make the default view one low-mass efficiency plot with menu, NN and pixels; move the remaining panels into details. |
| `figures/kl_scan.png` | No. Five overlapping curves, unfamiliar likelihood notation and three orange styles require expert reading. The interval plot mentions a second allowed region without drawing it. | Make a complete allowed-interval plot the main figure, explicitly drawing every disconnected region; move the likelihood scan into details. |
| `figures/klw_vs_rate.png` — expanded details | Reasonably clear once “added rate” is understood; the logarithmic x-axis and clipped y-range need deliberate reading. | Mark the two operating points supporting the “1 versus 10–15 kHz” comparison. |
| `figures/cutflow.png` — expanded details | Readable, with direct values and sensible colours. It explains the denominators better than the main summary. | Use explicit headings “All generated events” and “Events that would pass offline selection” instead of encoding the distinction primarily through shading. |
| `figures/offline_eff.png` — expanded details | Nine panels and seven legend entries make this an expert diagnostic. | Split it into two selectable questions: “Are the added events softer?” and “Would offline b tagging keep them?” |

**Text and flow:** retain the six-step sequence, but add a short answer above step 1. Reduce “Today’s plan” to its event-level benefit and limitation; move the 16×21 inputs and encoded displacement formula to tab 2. Introduce scouting before showing scouting curves. Keep background assumptions visible beside the self-coupling conclusion rather than exclusively in methods. (`shots/tab1_hh_01.png`, `shots/tab1_hh_02.png`, `shots/tab1_hh_03.png`)

**Tab 2 — How path A works.** The likely takeaway is “a complicated tracking procedure gives better resolution.” The intended takeaway is simpler: existing L1 tracks locate a few useful pixel hits, those hits reveal displaced tracks, and b tagging improves from 15% to 47% at the same 1% false-tag rate. The four-step strip is a good foundation, but its strongest outcome appears farther down. (`shots/tab2_how_00.png`, `shots/tab2_how_01.png`)

- **Define:** *Outer Tracker* = the outer tracking detector supplying L1 tracks; *cluster* = neighbouring pixel signals grouped into one hit; *d0/dxy* = transverse track displacement relative to the collision reference; *z0* = longitudinal position of closest approach; *hit purity* = fraction of selected hits correctly associated with the track. (`shots/tab2_how_00.png`)
- **Define performance language:** *b efficiency* = fraction of b jets tagged; *light mistag* = fraction of light-flavour jets incorrectly tagged; *ROC* = efficiency versus false-tag rate; *HLT* = the later software trigger; *UParT* = the offline jet-flavour classifier used as a reference. (`shots/tab2_how_01.png`)
- **Move or translate:** *PUPPI* = particle weighting that suppresses pileup; *impact-parameter significance* = displacement divided by its estimated uncertainty; *BDT* = boosted decision-tree classifier; *FPGA* = programmable electronics used for fast processing. These do not need to lead the explanation. (`shots/tab2_how_01.png`, `shots/tab2_how_02.png`; `page_text.html`, tagging methods)

| Figure | At a glance? | Single most useful change |
|---|---|---|
| `figures/event_display.png` | The numbered sequence helps. The pale 3D detector, tiny annotations and switch from centimetres to an exaggerated millimetre offset make it hard to follow. | Replace the default display with one enlarged track-to-pixel schematic; keep the four-panel event example expandable. |
| `figures/d0_resolution.png` | The narrow orange peak communicates improvement, but the logarithmic density and tiny legend hide the numerical result. | Directly label the distributions “545 μm” and “35 μm relative to HLT tracks.” |
| `figures/roc_chain.png` | Five curves and logarithmic fractions are not introductory; “lower is better” is unstated. | Add a prominent 1% false-tag line with labelled intersections: 15%, 19%, 47%, 50%, 84%. |
| `figures/jet_eff.png` | Six series, filled/open markers and two variables overload the message. The low-pT effect itself is strong. | Make the b-efficiency-versus-pT panel the default figure; move mistag and η dependence into details. |

**Text and flow:** lead with “Pixels identify displaced tracks and triple b-tag efficiency at the same false-tag rate.” Follow with the four-step strip, then the schematic. Move the feature inventory and failed 3D/raw-hit variants behind “Alternatives tested.” The statement “below 40 GeV the NN tags almost no b jet” also needs softening: the plotted efficiency rises toward roughly 10% near that boundary. (`shots/tab2_how_00.png`, `shots/tab2_how_01.png`, `shots/tab2_how_02.png`)

**Tab 3 — Getting the hits.** The likely takeaway is “the design needs 3 μs and 4–10 Gb/s.” The intended takeaway should be “the physics looks promising, but timely access to pixel hits is unproven; the quoted traffic is only a lower bound.” Precise tiles and a polished architecture diagram currently make the proposal look more established than the text supports. (`shots/tab3_flow_00.png`, `shots/tab3_flow_01.png`)

- **Define:** *RoI request* = request for the buffered hits from chips near a predicted track; *latency* = time available before the trigger decision; *buffer* = temporary storage of recent collisions; *CROC* = pixel readout chip; *destructive readout* = reading consumes the stored entry. (`shots/tab3_flow_00.png`, `shots/tab3_flow_01.png`)
- **Translate diagram labels:** *correlator* = electronics combining detector information into trigger objects; *PF* = particle reconstruction combining detector measurements; *seeded-cone jets* = jets assembled around initial energetic objects; *Global Trigger* = final L1 decision logic; *BX* = bunch crossing; *IP summary* = track-displacement summary. Clarify that correlator “L2” is an internal processing stage, not a second trigger after L1. (`shots/tab3_flow_01.png`)
- **Keep specialist infrastructure in details:** *e-link* = electrical data connection from detector electronics; *lpGBT* = chip aggregating detector data for high-speed links; *DAQ* = data acquisition; *TM* = time multiplexing across processing boards; *DTC* = data, trigger and control board. (`shots/tab3_flow_01.png`; `page_text.html`, readout and baseline toggles)

| Diagram | At a glance? | Single most useful change |
|---|---|---|
| Timing diagram, `shots/tab3_flow_00.png` | The highlighted window is useful, but tiny labels obscure why 5→9.5 μs leaves only 2.5–3 μs for this step. | Draw one enlarged proposed sequence showing request start, fetch/refit deadline and reserved downstream processing time. |
| Proposed architecture, `shots/tab3_flow_01.png` | Too many boxes and crossing arrows; the pixel loop is identifiable but not understandable without expertise. | Replace the main view with “L1 tracks → request nearby chip hits → refit tracks → tag jets,” with the uncertain readout step visibly marked. |
| Phase-2/Run-3 comparison, `page_text.html`, baseline toggle | Correctly placed behind details, but both diagrams still carry many internal acronyms. | Use matching simplified layouts so the added tracking and pixel paths are the only major visual differences. |

**Text and flow:** put the feasibility question first, then the simple loop, then timing and traffic. Bring the “1–6 μs on one e-link” example out of the toggle because it directly explains the timing risk, with its one-link assumption attached. Replace slash-separated traffic columns with separate HT>140 and HT>200 columns. Spell out **bits**: “64 b” is particularly confusing on a b-tagging page. (`shots/tab3_flow_00.png`, `shots/tab3_flow_01.png`; `page_text.html`, readout toggle)

**Tab 4 — Rate.** The likely takeaway is “pixels cut the trigger’s bandwidth sixfold.” The intended takeaway is narrower: a dedicated HH-like selection can match the HT seeds’ signal efficiency at much lower standalone rate; this does not imply sixfold savings for the full menu. The necessary qualification appears below the introductory tiles and large menu plot. (`shots/tab4_rate_00.png`, `shots/tab4_rate_01.png`)

- **Define:** *rate* = accepted events per second; *kHz* = thousands per second; *standalone rate* = rate of the selection alone; *added rate* = new events beyond those already accepted by the menu; *threshold* = minimum required value; *TDR* = Technical Design Report. (`shots/tab4_rate_00.png`, `shots/tab4_rate_01.png`)

| Figure | At a glance? | Single most useful change |
|---|---|---|
| `figures/menu_composition.png` | Bars and labels are readable, but overlapping categories resemble an additive budget breakdown. The total 346 kHz cannot be obtained by adding these bars. | Put “Overlapping selections—do not sum these bars” immediately under the title. |
| `figures/rate_case.png` | The three-bar comparison is strong; the left panel adds a logarithmic rate axis, four curves and a reference star. | Lead with the three bars under “Rate needed to keep 60% of HH→4b.” |
| `figures/seed_plane.png` — expanded details | Appropriate expert material, but contours, shaded density and boxed operating points need explanation; its values also conflict with the main result. | Regenerate it from the same result version as the main rate figure before publication. |

**Text and flow:** move the dedicated-seed qualification above the figures. Lead with the three-bar result, follow with the efficiency/rate trade-off, and put menu composition last as context. Change “cheaper” to “lower accepted-event rate” to avoid implying hardware or monetary savings. (`shots/tab4_rate_00.png`, `shots/tab4_rate_01.png`)

**Tab 5 — Beyond HH→4b.** The likely takeaway is “pixels help charm and VBF too.” The intended takeaway needs differentiation: per-jet charm tagging improves substantially; the demonstrated incremental VBF H→cc event gain over the NN is small; VBF H→bb gains more; the studied boosted channels already pass L1 efficiently. (`shots/tab5_more_00.png`, `shots/tab5_more_01.png`, `shots/tab5_more_03.png`)

- **Define:** *VBF* = Higgs production accompanied by two characteristic widely separated jets; *ggH* = Higgs production through gluon fusion; *boosted* = high transverse momentum; *ZH(νν)* = Higgs production with a Z decaying invisibly; *MET* = missing transverse momentum. (`shots/tab5_more_00.png`, `shots/tab5_more_02.png`)
- **Translate:** *acceptance* = events satisfying the stated simulated geometry and kinematic requirements; *c versus light at 10%* = charm efficiency when 10% of light jets are falsely tagged; *charm word* = encoded charm-sensitive features; *bootstrap ±0.5 points* = estimated statistical variation from resampling. ParticleNet/CvsAll can become “offline charm score” in the main text. (`shots/tab5_more_00.png`, `shots/tab5_more_01.png`, `shots/tab5_more_02.png`)

| Figure | At a glance? | Single most useful change |
|---|---|---|
| `figures/ctag_roc.png` | The improvement is visible, but two backgrounds and four curves require careful legend reading. | Label the operating-point intersections directly, especially 16%→29% at 10% light mistag. |
| `figures/vbf_tag_rate.png` | Useful comparison, but the different truncated y-ranges amplify small changes and hinder comparison between channels. | Use the same y-range in both panels and explicitly label it as a zoom. |
| `figures/menu_vs_pt.png` | Mostly readable, but blue/orange now encode decay flavour rather than NN/pixels; overlapping lines conceal that switch. | Use a different palette for decay flavour. |

**Text and flow:** start with a compact channel summary including the gain **over the NN**, then show supporting plots. Move the long recalibration paragraph, emulator-version discussion and Run-3 trigger-name table into details. Keep the important finding that stronger per-jet charm tagging does not materially improve the tested VBF event selection. (`shots/tab5_more_01.png`, `shots/tab5_more_02.png`)

**Tab 6 — Code.** The likely takeaway is “everything exists, but I need the author to navigate it.” The intended takeaway is “I know where to start, how to reproduce one result, and where each figure comes from.” The source inventory is valuable, but it precedes the beginner’s route through it. (`shots/tab6_code_00.png`, `shots/tab6_code_01.png`, `shots/tab6_code_02.png`)

- **Define only what is needed to begin:** *CMSSW* = CMS software framework; *ntuple* = analysis-oriented event table; *pixi* = the environment manager used here; *Slurm* = cluster job scheduler; *subMIT* = the computing cluster hosting these paths. Move FWLite, RAW/MINIAOD, xrootd and production-stage acronyms into the production instructions. (`shots/tab6_code_00.png`, `shots/tab6_code_03.png`)
- **Tables:** the dense lavender code fragments and broken filenames make scanning difficult. Group the result inventory by dashboard tab, and allow long paths to scroll or copy without breaking filenames midword. (`shots/tab6_code_01.png`, `shots/tab6_code_02.png`)
- **Text and flow:** put “Start with HANDOFF.md,” the environment requirement and one complete reproduction example first. Follow with result lookup, then production pipeline, data locations and troubleshooting. No scientific figure is needed here; a short input→script→figure example would help more than another diagram. (`shots/tab6_code_00.png`, `shots/tab6_code_02.png`, `shots/tab6_code_03.png`)

**Cross-cutting numerical and conceptual consistency.** These are presentation-level discrepancies; where the supplied material does not explain the difference, the underlying result should be checked rather than silently harmonized.

| Issue | Evidence and required clarification |
|---|---|
| **“1.5× below 400 GeV” conflicts with the summary.** | `figures/recovery.png` gives 66%/52%≈**1.27×**. `figures/mhh_eff.png` reaches about 1.5× in the lowest bin, not throughout the region. Correct the caption in `shots/tab1_hh_02.png`. |
| **The seed-plane operating points disagree with the rate story.** | At 20 kHz, `figures/seed_plane.png` reports NN/pixels **55%/68%**; `shots/tab4_rate_00.png` and `figures/rate_case.png` report about **65%/76%** near that rate. Identify differing versions, samples or definitions. |
| **The architecture describes a different pixel strategy.** | `shots/tab3_flow_01.png` shows jet-cone readout, ~800 clusters/jet and “Cone tracking”; the prose describes narrow track windows and 200–260 clusters/crossing. Tab 2 quotes ~660 clusters/cone. Distinguish alternative geometries or update the diagram. |
| **20 versus 21 NN features.** | The architecture says 16 candidates×20 features; tabs 1 and 2 say ×21. Explain any excluded feature or correct the count. (`shots/tab3_flow_01.png`, `shots/tab1_hh_01.png`, `shots/tab2_how_01.png`) |
| **The eight-number summary lists seven quantities.** | Top-three significances + two counts + summed significance + maximum d0 totals seven. Name the missing input. (`shots/tab2_how_01.png`) |
| **VBF baselines switch samples.** | The first table/tile gives **57%/53%** for cc/bb; the held-out-event comparison gives **58.0%/51.4%**. This can be a sample distinction, but the tile mixes them without explaining it. (`shots/tab5_more_00.png`, `shots/tab5_more_01.png`, `shots/tab5_more_02.png`) |
| **Recalibrated b-tag numbers differ.** | Tab 2 quotes **54/83%**, while tab 5 quotes **55/83%**, starting from **48/78%** rather than **47/78%**. Label the evaluation sample/version. Tab 5 also references nonexistent “tab 7.” (`shots/tab2_how_02.png`, `shots/tab5_more_01.png`) |
| **ZH headline ranges are ambiguous.** | The tile gives **96–98% above 150 GeV**, the caption gives **96–100%**, and `figures/menu_vs_pt.png` has a first bin above 150 GeV around **92–95%**. Distinguish an integrated efficiency above threshold from a range of per-bin efficiencies. (`shots/tab5_more_00.png`, `shots/tab5_more_03.png`) |
| **Scouting’s NN baseline is over-rounded.** | “2.0σ … in both background models” sits below a table giving NN **1.9/2.0σ** for A/B. Use those values or state only that adding scouting produces no material change. (`shots/tab1_hh_03.png`) |
| **19 versus 20 kHz has an explanation, but it is buried.** | These are emulated versus TDR HT-seed rates. Label both wherever compared; also distinguish the single HT-only selection’s **21.4 kHz**. (`shots/tab4_rate_00.png`, `figures/rate_case.png`; `page_text.html`, rate methods) |
| **“Planned menu” has inconsistent scope.** | HH methods specify the two HT/quad-jet selections, while tab 4 describes the full **346 kHz** menu. Label the HH baseline “HT/quad-jet baseline used here,” unless equivalence to the full menu is established. (`figures/gap_mhh.png`, `shots/tab4_rate_00.png`; `page_text.html`, gap methods) |

Some prominent numbers **do** agree: 40% missed versus 60% kept; 64% missed versus 36% kept below 400 GeV; and 16% missed versus 84.1% kept among offline-selectable events. The problem is that the reader must discover the denominators. (`shots/tab1_hh_00.png`, `figures/recovery.png`, `figures/cutflow.png`)

**Colour and symbol consistency:** grey=baseline, blue=NN and orange=pixels works well across the main performance figures. It breaks when blue denotes proposed pixel hardware, or blue/orange denote bb/cc. Filled/open markers also change meaning within `recovery.png`. Keep comparison colours fixed, use another palette for decay channels, and supplement colour with direct labels or distinct markers. (`figures/recovery.png`, `figures/roc_chain.png`, `shots/tab3_flow_01.png`, `figures/menu_vs_pt.png`)

**“How this was made” boxes:** the collapsed placement works for scripts, training splits and detailed cuts. It fails when it hides information needed to interpret the claim: signal-only information, background models, sample completeness or the meaning of the rate baseline. Keep those qualifications visible; rename toggles by content, such as “Selection and samples” or “Background assumptions.” The boxes’ expanded visual layout is not shown in the screenshots, so this assessment concerns their contents and placement. (`shots/tab1_hh_00.png`, `shots/tab1_hh_02.png`, `shots/tab4_rate_01.png`; `page_text.html`, corresponding toggles)

**Headlines and claim strength:**

- “Closes most of the gap” needs a denominator. Across all events, 60→78% recovers **18 of the 40 percentage points lost**, or 45% of the original loss. For offline-selectable low-mass events, 60→96% recovers 90% of that loss. Say which result is meant. (`figures/recovery.png`, `shots/tab1_hh_01.png`)
- “Scouting recovers nothing” and “in any background model” are broader than the study. Use **“No additional HH sensitivity found in the two background models tested.”** This distinguishes sensitivity from recording additional events. (`shots/tab1_hh_03.png`)
- “Pixels make charm tagging possible” overstates a change from an already nonzero 16% efficiency; use **“Pixels nearly double charm efficiency at 10% light mistag.”** “Lower thresholds do not” also ignores the small plotted improvement. (`shots/tab5_more_00.png`, `shots/tab5_more_01.png`)
- “The HLT is [the bottleneck]” is not demonstrated by a plot of L1 efficiency alone. Use **“Little L1 loss remains in these simulated kinematic regions.”** (`shots/tab5_more_00.png`, `figures/menu_vs_pt.png`)
- “Being computed” and “in no CMS plan we know of” obscure status. Prefer **“Full-chip traffic not yet evaluated”** and **“Pilot proposal; hardware feasibility unverified.”** (`shots/tab3_flow_01.png`)

Two supplied assets are not represented among the figure entries in `page_text.html`: `figures/rate_curves.png` and `figures/mhh_categories.png`. If retained for later use, the former needs conspicuous population labels because its y-axes are tightly zoomed; the latter needs “incremental union of selections” explained so its stacked additions are not mistaken for the standalone pixel efficiency.

**The 15 highest-value edits, ranked:**

1. **Add a three-sentence answer above tab 1’s first plot:** NN helps; pixels further recover low-mass signal; hardware feasibility and background-dependent sensitivity remain unresolved. (`shots/tab1_hh_00.png`, `shots/tab1_hh_03.png`)
2. **Give every headline percentage an explicit population**, starting with “all HH events,” “mHH<400 GeV,” and “would pass offline selection.” (`shots/tab1_hh_00.png`, `figures/recovery.png`)
3. **Expose the distinction between signal recovery and final κλ sensitivity** beside the 97% information claim, including the signal-only assumption. (`shots/tab1_hh_01.png`, `shots/tab1_hh_02.png`)
4. **Correct the 1.5× caption** to approximately 1.27× for the integrated below-400-GeV comparison, or explicitly restrict 1.5× to the lowest bin. (`figures/recovery.png`, `figures/mhh_eff.png`)
5. **Reconcile and regenerate the seed-plane figure** against the main rate result; publish one labelled result version. (`figures/seed_plane.png`, `figures/rate_case.png`)
6. **Replace the proposed readout diagram with the actual track-window method**, labelling request unit, payload unit and unresolved hardware step. (`shots/tab3_flow_01.png`)
7. **Rename the scouting headline** to “No added HH sensitivity found with scouting in this study.” (`shots/tab1_hh_03.png`)
8. **Lead tab 3 with “Can the pixel chips deliver hits before the decision?”** and make “Full-chip traffic unknown” a headline tile. (`shots/tab3_flow_00.png`, `shots/tab3_flow_01.png`)
9. **Redesign `recovery.png` into explicitly labelled population comparisons**, eliminating panel-dependent filled/open meanings. (`figures/recovery.png`)
10. **Add brief first-use definitions** for seed, HT, κλ, mistag, RoI and offline-selectable; move implementation acronyms behind details. (`shots/tab1_hh_01.png`, `shots/tab2_how_01.png`, `shots/tab3_flow_00.png`)
11. **Make the self-coupling result a complete interval comparison**, including disconnected allowed regions and plain-language model labels. (`figures/kl_scan.png`)
12. **Lead tab 2 with “15%→47% b efficiency at the same 1% false-tag rate,”** followed by a simplified track/pixel schematic. (`shots/tab2_how_00.png`, `shots/tab2_how_01.png`)
13. **Lead tab 4 with the three-bar rate comparison**, prominently labelled “standalone HH-like selection; not total-menu savings.” (`figures/rate_case.png`, `shots/tab4_rate_00.png`)
14. **Replace tab 5’s long opening detail sequence with a channel comparison**, showing baseline, NN, pixels and evaluation sample; move Run-3 path names into a toggle. (`shots/tab5_more_00.png`, `shots/tab5_more_02.png`)
15. **Turn tab 6’s opening into a reproducible starting point:** linked handoff, prerequisites and one complete figure-generation example; group the inventory by tab. (`shots/tab6_code_00.png`, `shots/tab6_code_01.png`)

**Suggested tab 1 wording:** “Pixel hits recover low-mass HH→4b events; their impact on the self-coupling measurement depends on background.” (`figures/recovery.png`, `shots/tab1_hh_02.png`)

| Tile | Proposed copy |
|---|---|
| **The current gap** | **40% of HH→4b missed** — rising to 64% below mHH=400 GeV. (`shots/tab1_hh_00.png`) |
| **What pixels add** | **83%→96% kept** — among low-mass events that would pass offline selection, comparing NN and pixel seeds at the same +2.5 kHz. (`figures/recovery.png`) |
| **What remains unresolved** | **Sensitivity and hardware feasibility** — more signal is recovered, but the added background and timely pixel readout still need evaluation. (`shots/tab1_hh_03.png`, `shots/tab3_flow_01.png`) |
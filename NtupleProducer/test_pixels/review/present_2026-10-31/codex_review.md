Read-only review complete. The main efficiency results largely match the outputs, but I would revise the page before showing it: several conclusions exceed the evidence, and some numbers have the wrong denominator or rate interpretation.

**1. Clarity for the ATLAS reader**

Apply these replacements consistently, including figure titles and legends.

| Current wording | Suggested replacement or clarification |
|---|---|
| “today’s L1 NN”; “tracks CMS already has” | “the baseline Phase-2 L1 NN in this emulation”; “tracks available in the Phase-2 L1 design.” These are not descriptions of the operating Run-3 trigger. |
| “the planned hardware trigger … misses 40%” | “The emulated HT450 OR quad-jet+HT400 seed pair misses 40%…” The HH study does not establish the loss of the complete CMS menu. |
| “All SM HH→4b events” | “All simulated SM **gluon-fusion** HH→4b events.” |
| “three times better” | “raises b-jet efficiency from 15% to 47% at 1% light-jet mistag in this sample.” |
| “most of the sensitivity to the Higgs self-coupling” | “78% of our **generator-level, signal-only information measure** near κλ = 1.” Define κλ = λHHH/λHHH,SM immediately. This is not the information in a background-inclusive analysis. |
| “offline-selectable”; “offline 4b + 3b” | “passing our mock offline selection: four selected jets, either four medium b-tags or three medium plus one loose tag, and a two-Higgs mass requirement.” Put the detailed selection in Methods. |
| “+15 kHz” | “a target additional rate of 15 kHz relative to the HT-seed pair; measured validation rates are given below.” Explain overlap removal and distinguish additional from standalone rate. |
| “HT > 450 … online cuts 361/316” | “Seed names quote offline-equivalent thresholds; the emulator applies HT > 361.0 or 316.3 GeV.” Identify the scale of every HT annotation in `rate_case.png`. |
| “CMSSW 17”; “CMS L1 correlator”; “TDR” | On first use: “CMS simulation/reconstruction software, CMSSW 17”; “the processor combining tracking, calorimeter and muon trigger information”; “Technical Design Report.” |
| “PUPPI” | “pileup-per-particle identification, the pileup-weighting algorithm used to construct these jets.” |
| “displaced (5-parameter) fit” | “a five-parameter track fit in which transverse impact parameter d0 is free.” Distinguish this from the prompt, d0 = 0 track used to seed the illustrated extension. |
| “HLT pixel tracks” | “pixel-only tracks reconstructed in software, used here as a reference.” They are neither L1 inputs nor full offline tracks. |
| “Compression to 64 bits per jet” | “Quantising the **eight additional track-summary features** to 64 bits per jet…” This does not compress the entire jet or demonstrate fixed-point classifier performance. |
| “perfect b tag” | “ideal identification of generator-labelled b-jets, with no inefficiency or mistag; pileup heavy flavour is missing from the labels.” |
| “generator jets: perfect resolution” | “generator-level jets without detector smearing or pileup jets.” This is an idealised object definition, not a demonstrated absolute ceiling. |
| “mHH”; “m4j” | Explicitly distinguish generator Higgs-pair mass from the reconstructed four-jet mass used in the fit. |
| “pT-hat bins” | “bins in the generator hard-scattering scale, p̂T.” |
| “in acceptance” | Give the actual generator cuts. In the VBF code these are flavour-selected central jets and a non-Higgs-flavour jet pair; the code does **not** explicitly match the central jets to Higgs daughters. |

Figure-specific fixes:

- **`gap_mhh.png`:** replace “kept by the planned menu” with “accepted by the HT-seed pair.” Label the final bin “≥800 GeV, including overflow”; it contains events above 1 TeV despite ending at 1000 on the axis.
- **`recovery.png`:** add “Each row is a separate alternative.” The final panel needs “**all masses**”; its denominator differs from the low-mass panel beside it.
- **`roc_chain.png` and `ctag_roc.png`:** explain that each “+” curve is a separately trained classifier using baseline scores plus the indicated features. The inputs are not successively accumulated. Define light jets as the non-b/non-c category, including gluons.
- **`d0_resolution.png`:** replace “robust width” with “1.4826 × median absolute deviation of the residual.” Label the ordinate “normalised density [µm⁻¹]”; explain that the edge spikes include clipped overflow.
- **`event_display.png`:** define d0 and z0, and label the track as a **selected successful example**. Replace “pileup clusters” with “other nearby clusters” unless pileup ancestry was checked. The outer-tracker points are drawn along the reconstructed helix, not plotted measured stubs.
- **`menu_vs_pt.png`:** “generator MET (Z pT)” is too exact: the code uses `genMet_pt`. Use “generator missing transverse momentum.” Explain that the boosted-Higgs horizontal variable is a generator-jet proxy.
- **`vbf_tag_rate.png`:** specify the meaning of horizontal and vertical error bars, and identify the limited baseline seed set.
- **`menu_composition.png`:** replace `SinglePuppijet`, `DoublePuppijet`, `PuppiHT` shorthand with ordinary descriptions; retain exact seed names in the source box.

The page explains too much in three places: “How to read this page” repeats the navigation; tab 3 repeats the fixed-latency argument in its opening, diagram, bullets and aside; and the eight-feature enumeration interrupts the physics explanation. Keep the CMS–ATLAS architectural distinction, but move these details into expandable methods. The audience does not need elementary explanations of b-tagging, HT, pileup or FPGAs.

**2. Numerical audit**

The principal discrepancies and numerical qualifications are:

| Quoted text/value | Check and fix |
|---|---|
| “60% … below 400 GeV and 63% of **their** κλ information”; similarly “93% … and 92% of their information” | **Wrong denominator.** The information values 62.6% and 92.4% cover **all offline-selectable masses**. Restricting the same calculation to mHH < 400 gives **47.0% and 90.0%**. Separate the two populations explicitly. |
| “at +15 kHz” | In `curves.json`, validation rates are **16.280 kHz for NN** and **14.038 kHz for pixels**. At the 2.5-kHz target they are **2.335 and 2.210 kHz**. Label these as optimisation targets, or interpolate to a common measured rate. |
| “Without barrel layer 1 … 75% … +2.5 kHz” | The 75.34% efficiency is traceable to `curves_noL1.json`, but its measured added rate is **2.023 kHz**. Again, 2.5 is the target. |
| “Today’s L1 NN … 15 / 36%” | **Mixed baseline.** `tag_chain.json["L1 NN"]` gives **14.75 / 34.51%**. The **15.26 / 36.30%** values belong to `"NN only"`, a newly trained boosted-tree classifier using NN scores and kinematics. Use **15 / 35%**, or rename the row. |
| “Summary packed … 47 / 78%” | The q8 output is **46.868 / 77.492%**. Direct integer rounding gives **47 / 77%**; 78 arises from double rounding. Prefer **46.9 / 77.5%** throughout this table. |
| “29–34% with pixel hits” | **Mismatch with the displayed ROC.** It gives **28.96%** for L1+pixel and **30.22%** for HLT pixel tracks. Replace with “29% with the L1 extension; 30% with the software pixel-track reference.” |
| “Missing-energy seeds keep 96–98%” | These are the **combined tested-menu** values: **96.04% bb**, **97.70% cc**. `PuppiMET200` alone gives **92.74% and 92.07%**. Replace the subject with “the tested MET/MHT and jet seed combination.” |
| “about 3% … about 5%” | Exact relative increases in ZSM are **2.472%** and **5.213%**. “About 2.5% and 5.2%” is preferable. The formal “≤5%” statement is false even numerically. |
| “background grows 5–10 times as fast; S/√B improves by ×1.0–1.15” | The background grows **by factors 4.60, 6.73 and 9.77**, not “times as fast.” The quoted figure of merit is **Irel/√Brel**, not ordinary S/√B. Its values are **0.985, 1.146, 1.128**. |
| “Above 300 GeV QCD and minimum bias agree within 10%” | Approximately true only for the inclusive four-jet selection. Ratios above 300 are **1.102, 0.978, 0.935, 1.033**. In the Higgs window they are **0.923, 2.083, 1.840, 0.278**. State the selection and sparse statistics. |
| “2 million re-simulated minimum-bias crossings” | **Wrong sample description.** There are **1,999,360 parent crossings**, of which **120,731 selected crossings** were re-simulated with pixel clusters. |
| “Top panels: the share of the κλ information in each mHH bin” | Both strips are **identical inclusive generator-level information**: `plot_gap.py` does not apply the offline selection to the right strip. Label this explicitly or calculate the right-hand quantity for its displayed population. |
| “124 ± 29, 114 ± 30 GeV” | The numbers match the saved centres/scales, but they are not the full window boundary. The code requires **√[((m1−124.386)/28.871)² + ((m2−113.816)/29.869)²] < 1.6**. Include the 1.6 factor and avoid presenting scales as uncertainties. |
| “1.9 µs (99% within 2.7 µs)” | Numerically matches the **hypothetical pre-emptive-priority** model: **1.883 µs median, 2.650 µs p99**. It is not an end-to-end collision-to-L1 latency. |

Sources for these checks: [recovery.json](/work/submit/novaka/l1pixels/analysis/plots_page/recovery.json), [curves.json](/work/submit/novaka/l1pixels/analysis/curves.json), [tag_chain.json](/work/submit/novaka/l1pixels/analysis/tag_chain.json), [scout4b.json](/scratch/submit/cms/novaka/l1pixels/derived/scout4b.json), [scout_kin.json](/scratch/submit/cms/novaka/l1pixels/derived/scout_kin.json), [norm_check.json](/scratch/submit/cms/novaka/l1pixels/derived/norm_check.json), and [offline_lowmass_w.json](/scratch/submit/cms/novaka/l1pixels/derived/offline_lowmass_w.json).

The following numerical groups check out, subject to the definitions above:

- **Recovery figure and tab-6 table:** the efficiencies agree with `recovery.json`, including 59.6% overall, 36.2% low-mass, 60.4% offline-selected low-mass, and the quoted NN/pixel/perfect-tag improvements. The per-bin missed fractions in `gap_mhh.png` also reproduce.
- **78% below 400 GeV:** recalculates to **78.199%**, for the inclusive generator-level signal-only information measure.
- **Standalone rates:** **21.434 / 13.694 / 3.371 kHz** reproduce the displayed **21.4 / 13.7 / 3.4**. These are interpolated rates matching **59.558%**, not separately demonstrated working points at exactly 60%.
- **Scouting:** **3815.8 signal**, **6.699×10⁸ background**, **0.2393σ** rejected-stream significance; **0.3534σ** with generator jets. All displayed significance bars round correctly.
- **Tagging:** the plotted b ROC values **15/19/47/50/84%** and charm values **16/16/29/30%**, **41/42/61/60%** agree with their JSONs. The other robustness values agree with the variant outputs.
- **Other channels:** VBF **51→56/61%** and **58→61/62%** agree at approximately 2 kHz. Boosted-Higgs **98–100%** and sample counts **4910/4800** reproduce from the saved arrays.
- **Readout:** approximately **70 chips** is a **mean of 68.45**; median is 64. The **25–41%** payload range corresponds to different assumed quarter-core overheads, not a measured uncertainty interval. **511 × 25 ns = 12.775 µs**, correctly rounded to 12.8.
- **Menu composition:** category sums match the hard-coded seed table. **346 kHz**, **450 kHz including 30% margin**, and **15/750 = 2%** are consistent. However, that historical table uses **SingleJet180**, whereas the other-channel emulation uses **SingleJet230**; identify the different menu configurations. The published table supports the totals. [CMS menu presentation](https://indico.cern.ch/event/1422718/contributions/6155985/attachments/2991572/5269949/Spatind2025_L1TriggerUpgrade_JHeikkilae.pdf)

Provenance still needs repair:

- **545 µm** is traceable to the ROOT-based plotting calculation; **35.43 µm** reproduces from `scan_0.json`. I did not independently regenerate the 545-µm ROOT calculation.
- The event-display numbers—**63,872 clusters, 29 candidates, 498/532 µm, 2.3/70 GeV, z0 1.67→1.61 cm**—are generated from a selected event, but the page gives no input filename/event identifier. Add those and the command.
- **70–100 µm** is asserted in the internal note without a linked numerical output.
- **±30%** is described in the notes as variation between models; it is not a documented confidence interval.
- The timing window **“about 1–5 µs”** has no demonstrated upstream/downstream latency budget.
- Geometry radii, the 16-candidate NN configuration and the **6/2/2/1 module links** need exact configuration/design references on the page.
- “Every figure has a ‘How this was made’ box” is false: several figures, including the event display, resolution, menu composition and charm ROC, lack one.

**3. Claims that need weakening or correction**

**Readout-chip argument**

> “The pixel chip only reads hits out at one fixed latency after a trigger.”

Replace with:

> “The documented architecture selects hits at one configured latency after the crossing. Readout begins after a configured trigger-processing delay; output arrival then depends on processing and queueing.”

The supplied [RD53B manual](/scratch/submit/cms/novaka/l1pixels/derived/rd53b_manual_v2.21.txt:1335) supports the single hit-selection latency. Section 9.1 explicitly describes variable output waiting time, with a **31-BX minimum**. The timeline should not draw a 12.5-µs accept followed by a separate mandatory 12.8-µs decision: 12.8 is the configurable maximum.

> “A request at about 2 µs and the L1 accept at 12.5 µs cannot both be served for the same crossing.”

The important constraint is preserving **other crossings that might later receive L1 accepts**, not reading one crossing twice. Replace with:

> “Selecting hits at an early latency would discard unselected crossings before the normal L1 decision. The documented architecture provides no independent early regional-read path while retaining all other potentially accepted crossings.”

This is an architectural inference, not a demonstrated impossibility for every alternative system design.

> “CROC / ITkPix / RD53B … versions of the RD53B pixel readout chip.”

Update the chip generation. **CROCv2 and ITkPixV2 are RD53C production chips**; RD53B describes their predecessors. A public **CMS-specific RD53C manual already exists**, so “the CROC-specific manual should confirm” should become a direct comparison against it. [RD53C manual record](https://cds.cern.ch/record/2890222), [CMS production-chip announcement](https://cms.cern/news/cms-high-luminosity-tracker-chip-ready)

> “The chip can run a first trigger level …”

For the production chip, replace with:

> “RD53B documented a two-level mode. The RD53C CMS manual identifies it as a prototype feature not selected for either final detector and not fully supported.”

The historical ATLAS connection is supported, but distinguish **two hardware trigger levels** from the ordinary hardware-plus-software trigger chain. [RD53C CMS manual, §7.4](https://cds.cern.ch/record/2890222/files/rd53cCMS1v92.pdf), [RD53 historical requirements](https://cds.cern.ch/record/2632187/files/RD53B_requirements_V2-1.pdf?subformat=pdfa&version=1)

> “Bandwidth is not the obstacle.”

Too categorical. Replace with:

> “An idealised priority-readout model gives short regional service times, but available bandwidth and end-to-end latency remain unvalidated.”

The notes report **p99 34.2 µs with FIFO**, **4.41 µs without pre-emption**, versus **2.65 µs with pre-emption**. Normal traffic already approaches **97% utilisation**, before omitted framing and the greater occupancy of accepted crossings. Only 20 crossings supply the normal-payload model. These qualifications belong beside the headline.

Also change:

> “Dashed red: the path both pixel ideas need.”

to:

> “Dashed red: early pixel delivery required for pixel-assisted L1 decisions.”

Pixel scouting of rejected crossings needs a separate readout/retention mechanism, but does not intrinsically require delivery **before** the L1 decision.

**Scouting conclusion**

> “Scouting gain ≤5%”; “no useful gain”; “the gain would only shrink.”

Replace with:

> “For the tested four-leading-jet selection and background model, ideal flavour labels increase expected SM discovery significance by 2.5% with L1 jets and 5.2% with generator jets. This does not establish a general scouting bound.”

Reasons:

- Perfect tagging does not optimise jet choice, pairing, event classification or all available kinematic information.
- The rejected-stream background has **neff = 2.83** with L1 jets and **2.45** with generator jets.
- The nominal mass fit collapses to **two bins total**, effectively one per tag category.
- The offline-jet test has **zero simulated four-b background events**, and that category contributes zero to the reported Z. It is inconclusive for four tags.
- Missing pileup heavy flavour motivates caution, but does not prove the relative combined-stream gain must decrease when both stream models change.

The metric also matters: these percentages concern **ZSM**, not general κλ sensitivity. The same L1-jet JSON changes the quoted κλ interval from **[−0.125, 5.55] to [−0.05, 5.125]**, about **9% narrower**, subject to the same substantial model limitations.

> “With realistic L1 tags the gain is zero.”

Use:

> “The tested 5%-mistag working point gives a negligible gain at displayed precision; tighter working points lack sufficient background statistics.”

The 5% point changes Z from **1.06958 to 1.07043**. At tighter points, the fitter assigns zero significance contribution to empty-background bins; that is not evidence of zero physical sensitivity.

> “offline-quality jets give a Higgs mass window no narrower … because pileup jets and b-jet response dominate.”

Use:

> “The tested offline-PUPPI configuration has a wider fitted signal window. Its four-tag sensitivity could not be evaluated with the available background sample.”

The causal explanation is plausible, but not isolated by the comparisons shown.

**Other physics/implementation claims**

- **“resolution … 545 µm … 35 µm”:** call these **residual widths relative to matched HLT pixel tracks**. Shared pixel hits make the reference correlated; these are not independent truth-resolution measurements.
- **“At least two layers are needed”:** use “The tested single-layer method gives little improvement; a useful fast-pixel design needs further multi-layer studies.” The study does not establish that two layers suffice.
- **“deliverable”:** use “compatible with the planned L1 inputs; integration remains to be demonstrated.” FPGA implementation, full-menu overlap, HLT acceptance and downstream resources remain relevant.
- **“15 kHz is the rate CMS has already shown”:** supported as a published **seed-rate benchmark**, not approval for **15 kHz additional to this baseline**. Cite it with that distinction. [CMS HH trigger presentation](https://indico.cern.ch/event/1399335/contributions/6381918/attachments/3068023/5427429/CMS_Phase2_Trigger_HH_Elba2025_v1.pdf)
- **“background … double counting by construction”:** present this as the interpretation of the observed closure failure. The inclusive closure does not validate the Higgs-window flavour transfer or shapes.
- **“VBF H→cc … barely moves”:** distinguish the small pixel-over-NN increment near 2 kHz from the approximately four-percentage-point improvement over the baseline menu.

**ATLAS comparisons**

- **“L0 (1 MHz, 10 µs, no tracking)”**: the rate and latency are correct. Say **“no ITk tracking in the L0 decision”**, since muon tracking/segments are involved. ITk tracking occurs after L0 acceptance in the Event Filter. [ATLAS Phase-II overview](https://indico.cern.ch/event/1419878/contributions/6441907/attachments/3063656/5419372/LHCP2025_gvolpe.pdf), [ATLAS EF tracking](https://indico.cern.ch/event/1499357/contributions/6621933/)
- **“ATLAS has no direct equivalent”**: narrow this to the pre-L0, full-crossing acquisition concept. ATLAS has trigger-level analysis streams; the distinction is where selection occurs, not whether reduced-object analysis exists. [ATLAS trigger-operation documentation](https://twiki.cern.ch/twiki/bin/view/AtlasPublic/TriggerOperationPublicResults)
- **“stores … every crossing”**: use **“acquires and processes selected L1 data streams independently of L1 acceptance.”** Full-rate acquisition does not imply permanent storage of every object from every crossing. [CMS scouting design, §17.1](https://cds.cern.ch/record/2759074/files/CMS-TDR-023.pdf)

**4. Structure and questions the audience will ask**

| Tab | Does its first sentence answer the question? | Recommended opening/change |
|---|---|---|
| 1 Summary | Yes, but overstates three conclusions. | “Pixel extension improves simulated tagging substantially, but needs a readout capability absent from the documented architecture; the tested scouting analysis adds little SM discovery significance.” |
| 2 Trigger gap | Only the first paragraph does; the first sentence just says “no b-tagging.” | Lead with “The tested HT-seed pair retains 60% overall and 36% below 400 GeV.” |
| 3 Where pixel data exist | Yes, with an overly absolute conclusion. | Scope to normal physics readout and distinguish acquisition, retention and output timing. |
| 4 Pixels in L1 | Yes. | Put “at fixed 1% light mistag” and “simulation” in the opening sentence. |
| 5 Scouting | Yes, but gives a general conclusion from a restricted test. | Lead with the exact metric, tested selection and 2.5%/5.2% results. |
| 6 What works | First sentence is a fragment; the result comes next. | Lead with the NN seed’s low-mass efficiency and measured added rate. Rename “What does work” to “Practical next step.” |
| 7 Other channels | No: “We looked…” describes the process. | “Among the tested channels, VBF H→bb shows the largest gain from improved flavour tagging.” |
| 8 Methods | No opening answer. | Add: “These are private simulation projections; efficiencies, rate estimates and sensitivity models have different validation levels.” |

Missing questions worth answering explicitly:

- What does the **complete menu** retain, including muon-containing b-jet seeds?
- What are the uncertainties? The low-mass offline comparison has only **187 validation events**.
- How much of the L1 gain survives **HLT and final offline selection**?
- What exactly is optimised, and on which events? The ROC script uses **two-fold out-of-fold predictions pooled across both parities**, contrary to “training on even … curves on odd.” Seed optimisation does use the stated even/odd split.
- What arrives early enough to form a regional request, and what time remains for transport, refitting and the final decision?
- What does the planned replaceable pixel layer permit? The notes discuss this; the page omits it.
- Which results use real offline tags, independent truth-tag probabilities, or generator labels?
- Which uncertainties and backgrounds—especially finite QCD statistics, pileup heavy flavour and tt̄—enter the sensitivity calculation?

**5. Five most important fixes, ranked**

1. **Withdraw the universal scouting bound.** State the metric and restricted analysis; expose sparse background statistics and the missing offline four-tag category.
2. **Rewrite the chip argument using the production RD53C/CROCv2 manual.** Separate hit-selection latency from variable output timing and qualify the bandwidth claim.
3. **Correct the denominators and menu scope.** Especially the 63%/92% information values, the duplicated information strips, and HT-pair versus full-menu language.
4. **Report measured validation rates.** Separate the 15-kHz target, the 16.28-kHz NN result, and the published standalone 15-kHz benchmark.
5. **Repair the remaining numerical/method labels.** Raw NN versus retrained baseline, charm 29–34%, ZH menu versus MET efficiency, and the information-weighted proxy currently called S/√B.
**I would not send these conclusions unchanged.** The pixel-assisted tagging and HH acceptance gains are credible pilot results. The claimed κλ advantage is background-model dependent; the scouting no-go is not established; and the readout calibration contains a concrete encoding problem that invalidates the quoted payload as a physical lower bound.

I read the summary, then the handoff, and checked the referenced code and saved results. I independently recomputed the principal acceptance fractions from the event flags. Nothing was modified.

**1. Verdicts on A–J**

**A. Supported, specifically for these two emulated HT seeds.**

- `curves_flags.npz`: on 10,509 held-out HH events, the seeds retain **59.56%**, missing **40.44%**. Below generator \(m_{HH}=400\) GeV, they retain **36.21%** of 3,328 events, missing **63.79%**. The saved rate is approximately **19.2 kHz**.
- [direct_rate.py:39](/work/submit/novaka/l1pixels/analysis/direct_rate.py:39) implements the named seeds using online HT thresholds **361.0 and 316.3 GeV**, plus the corresponding regional jet thresholds. The names “450/400” are not the numerical cuts applied to these reconstructed jets.
- This is not the inefficiency of the complete planned L1 menu. Other seeds and overlaps have not been included in that headline.

**Fix:** “These two emulated HT seeds miss 40% of all generated SM HH→4b events, and 64% below 400 GeV.” Keep “all generated” distinct from offline-selectable.

**B. Supported configuration and ROC; overstated resolution and causal interpretation.**

- The configured chain does use extended, five-parameter OT tracks: `runPerformanceNTuple.py:912–918`, `l1pfJetMet_cff.py:56–71`, and `l1tPFTracksFromL1Tracks_cfi.py:28–38`.
- `tag_chain.json` gives **14.75% b efficiency at 1% light mistag** for the NN and **47.32%** for the pixel-assisted classifier.
- The reported **545 μm** is a robust width of the residual against matched HLT pixel tracks, not generator-truth \(d_0\) resolution. [make_page_plots.py:211](/work/submit/novaka/l1pixels/analysis/make_page_plots.py:211) also compares different track populations: the OT residual uses all eligible matched tracks; the pixel residual comes from the extension validation in jet cones.
- These ROCs use HH b jets versus QCD light jets with kinematic reweighting. They are not a universal performance statement about the CMS NN.
- The pixel validation has appreciable tails: `scan_0.json` gives approximately **36 μm robust width versus 138 μm clipped RMS**.

**Fix:** Say “the NN in this configured chain” and “HLT-reference residual width.” Poor OT impact-parameter precision is a plausible limitation, but this comparison does not establish that it alone causes the NN performance.

**C. Supported as an algorithmic pilot; overstated if presented as demonstrated hardware performance.**

The saved flags reproduce:

| Nominal added rate | All SM HH: NN / pixel | Offline-selectable, \(m_{HH}<400\): NN / pixel |
|---|---:|---:|
| +2.5 kHz | 69.55% / 77.75% | 155/187 = 82.89% / 180/187 = 96.26% |
| +15 kHz | 77.68% / 86.26% | 173/187 = 92.51% / 185/187 = 98.93% |

Qualifications:

- Actual held-out added rates are **2.33/2.21 kHz** for NN/pixel at the nominal +2.5 point, and **16.28/14.04 kHz** at +15. These are target-budget labels, not identical measured rates.
- [make_l1ext_lists.py:27](/work/submit/novaka/l1pixels/analysis/make_l1ext_lists.py:27) extends **prompt four-parameter L1 tracks** into pixels; the OT-only comparison uses extended five-parameter tracks. “The same NN tracks, with pixels added” would be inaccurate.
- The headline classifier consumes eight **floating-point** summary features. A quantizer exists, but the headline `direct_curves.py` calculation does not establish that the result survives the proposed 64-bit representation.
- The tagging and readout configurations differ materially; see G.

**Fix:** Retain the efficiencies, report denominators and measured rates, and call this “pixel-assisted algorithm performance.” Quantized performance, resource use, and latency remain separate deliverables.

**D. Supported correction; “perfect-tag ceiling” needs qualification.**

- [perfect_ceiling.py:38](/work/submit/novaka/l1pixels/analysis/perfect_ceiling.py:38) correctly avoids treating empty minimum-bias flavour labels as absence of heavy flavour. It transfers QCD \(P(n_b\geq k\mid H_T,\text{menu class})\), with sparse-bin fallbacks.
- The model uses unweighted QCDFlat composition and does not supply a complete pileup heavy-flavour truth model.
- At nominal +2.5 kHz, the chosen oracle point actually costs only **0.327 kHz** in this model. That illustrates its coarse, model-dependent character.
- **The correction was not propagated everywhere:** `scouting.py:302–308` still constructs the perfect seed using the minimum-bias flavour arrays from `seed_plane.npz`.

**Fix:** Call it a “QCD-transferred oracle reference.” It is neither a validated background rate nor a strict global efficiency ceiling. Regenerate the scouting perfect-seed results consistently.

**E. Central numbers supported; physics conclusion overstated; ±0.1σ precision cannot be verified.**

- `scouting.json` reproduces the intervals: pixel **[0.450, 1.925]**, NN **[0.375, 2.025]**. The corresponding SM significances are **1.841 and 1.761**.
- [scouting.py:216](/work/submit/novaka/l1pixels/analysis/scouting.py:216) evaluates a fixed-background Asimov likelihood. Although squared background weights are calculated, their uncertainty is not profiled into the likelihood.
- I found no calculation establishing the advertised ±0.1σ uncertainty through repeated samples, bootstrap, or nuisance propagation.
- The current score-binned transfer is a reasonable regularization idea, but **it has not demonstrated closure**. It replaces a noisy conditional estimate with a broader population and potentially substantial bias. Details below.

**Fix:** Present these as illustrative results under the specified transfer model. Withdraw “pixel ahead” as an established analysis-sensitivity conclusion and withdraw the precision claim until background-transfer and finite-sample uncertainties are propagated.

**F. Overstated; some supporting “ceiling” calculations are wrong.**

- The tested combination adds negligible sensitivity: menu alone **1.609039σ**, menu plus pixel scouting **1.609293σ**.
- That supports “negligible gain in this implementation,” not “Path B adds no sensitivity.”
- [scouting.py:484](/work/submit/novaka/l1pixels/analysis/scouting.py:484) calls an offline-quality scouting calculation a ceiling, but retains only menu/not-menu categories. The triggered fit benefits from additional seed-score categories. The comparison discards useful information on the purported ceiling side.
- The perfect-scouting background also contains an artificial **\(6.21\times10^8\)-event four-tag contribution**, generated by the zero-fraction floor discussed below.
- [hh_ht_reach.py:27](/work/submit/novaka/l1pixels/analysis/hh_ht_reach.py:27) supports the **1.8–5.6%** fractions, conditional on the existing four-jet selection and mass window. It does not establish the reach of an optimized low-mass analysis.
- Pixel-assisted scouting still needs pixel data acquisition before the relevant data disappear. It need not finish tagging within the Global Trigger decision deadline.

**Fix:** “No useful incremental sensitivity was found for the tested scouting selection and background model.” Remove the universal lower-mass and sensitivity no-go.

**G. Arithmetic supported; physical payload calibration wrong; latency infeasibility cannot be verified.**

`chip_readout.json` reproduces approximately:

- **68.45 chips/event** at HT>140;
- **73.43 / 28.07 Gb/s** at HT>140 / 200;
- **9.24 μs median** maximum-chip serialization time with one lane;
- **2.31 μs median**, with **29.93% above 2.5 μs**, after dividing by four.

However:

1. The encoder used for calibration emits charge bits for unhit pixels.
2. The readout request differs from the tagging request.
3. Uniform one-lane and four-lane configurations are not the installed connectivity model.
4. Geometry validation establishes hit containment much better than electronics mapping.
5. Serialization alone does not establish an end-to-end deadline.

**Fix:** Replace “infeasible in the latency budget” with **“feasibility unresolved; present serialization estimates require correction.”** The detailed issues and decisive tests are below.

**H. Supported selection effect; overstated κλ-information and background interpretation.**

- `offline_lowmass.json`: changing to `pt20_chi2_w30_today` gives **2.112× signal-only information proxy** and **1.442× QCD proxy**.
- In the 250–300 GeV bin, the existing pairing retains **2.80%** of events versus **4.43%** for any pairing satisfying the window. That is a substantial, identifiable loss.
- [offline_lowmass.py:115](/work/submit/novaka/l1pixels/offline/offline_lowmass.py:115) computes signal-only information, not the information of a signal-plus-background likelihood.
- The QCD calculation is explicitly unweighted QCDFlat.
- There is an additional conditioning problem: `evaluate()` selects the four largest observed UParT scores, then the QCD proxy assigns inclusive, flavour-only tag probabilities to those selected jets. Those probabilities need not apply after selecting on the discriminator itself.

**Fix:** “A softer selection doubles the retained signal-only information proxy, with a 1.4× unweighted QCD proxy.” Validate actual tags, generator weights, mass sculpting and sidebands before claiming an analysis-information gain.

**I. Supported as an interpolated dedicated-seed comparison.**

- `rate_case.json`: rates matching the HT-seed HH efficiency are **3.371 kHz pixel**, **13.694 kHz NN**, **21.434 kHz HT-only**.
- [rate_case.py:44](/work/submit/novaka/l1pixels/analysis/rate_case.py:44) obtains these through interpolation between optimized working points. The 3.4 kHz number is not a directly measured single operating point.
- At nominal 20 kHz, the saved HT-only point has **HT>340, 18.89 kHz**; the pixel point has **HT>170, 21.37 kHz**.

**Fix:** Label interpolation and actual rates. This demonstrates efficiency of a dedicated HH-oriented seed; it does not demonstrate that the broad HT seeds can be replaced or that their menu bandwidth can be reclaimed.

**J. Supported performance trend; pileup attribution remains a hypothesis.**

- The recalibrated 3D summary improves the per-jet ROC but lowers all-HH acceptance at nominal +2.5 kHz from **77.75% to 75.68%**. The transverse-only recalibration reaches **78.61%**.
- Actual rates differ slightly: approximately **2.21, 2.12 and 2.30 kHz**, respectively.
- `ctag_charm.json` supports approximately **15.56→28.96→33.54% charm efficiency at 10% light mistag**. The final number includes the additional charm features; the recalibrated summary alone gives **33.06%**.
- [charm_feats2.py:47](/work/submit/novaka/l1pixels/analysis/charm_feats2.py:47) introduces longitudinal significance relative to the estimated vertex. Wrong-vertex/pileup contamination is plausible, but these results do not isolate it causally.

**Fix:** State the mistag working point and exact feature set. Compare at common event rate and diagnose vertex association with truth or controlled vertex variations before calling this an intrinsic 3D-IP limitation.

**2. Scrutiny of the limitation claims**

**E: the precision claim is too optimistic, and the current background model is not yet sound for quantitative inference.**

The central issue is not merely the number of minimum-bias events. Minimum bias supplies the inclusive rate and mass distribution; QCD supplies the rare flavour/tag probability. Uncertainty or bias in that transfer can dominate.

The present implementation has three specific problems:

- **The conditional population changes.** `scouting.py:365–379` forms QCD score deciles across the broad HT>150, offline-covered sample. It does not retain the added-seed HT/menu-class restrictions. Approximately 85% of that QCD baseline belongs to the menu-accepted population, whereas the additional pixel events explicitly fail the menu.
- **The relevant tail is heavily pooled.** All three added pixel score categories at +2.5 kHz receive the same highest-decile four-tag probability, **\(7.25\times10^{-5}\)**. Each contains 11 minimum-bias events and receives approximately **495,278 four-tag background events**. The directly selected 27 QCD events instead give **\(4.85\times10^{-4}\)**, about **6.7 times larger**.
- **Mass correlations are removed.** `background()` multiplies the untagged category mass shape by its mean tag probability. Dependence of heavy flavour and tagging on \(m_{4j}\), pairing and topology is assumed away.

The 27-event estimate is unstable. That does **not** establish that its discrepancy is a small-sample artefact. The broader score-bin estimate may also be biased. Model A, model B and the current model should be treated as competing, unvalidated approximations—not as a sequence converging demonstrably toward truth.

Additional inconsistencies matter:

- QCD offline tag probabilities refer to leading offline jets above 25 GeV; signal probabilities are applied to leading L1 jets above 20 GeV.
- The QCD transfer includes events used to train the classifier rather than consistently using predictions from a model that did not train on those events.
- `qcd_tagfrac.py` has only **12 observed three-tag events and zero four-tag events** in its inclusive validation. That cannot validate the seed-selected four-tag tail.
- Unweighted QCDFlat flavour composition has not been shown transferable to the minimum-bias population.

**What changes the verdict:** demonstrate conditional closure versus score, HT, mass and menu class; use appropriate QCD weights; propagate finite QCD and minimum-bias statistics and transfer uncertainty; compare seeds with paired event resampling and common operating points. A simultaneous likelihood with constrained background parameters is needed before attaching precision to the κλ intervals.

Improved offline mass resolution could strengthen sensitivity. Background uncertainties and omitted processes could weaken it. The existing calculation does not determine the net change.

**F: the no-gain claim is too pessimistic; the actual scouting prospects remain uncertain.**

Two concrete problems prevent using the existing ceilings to close this route:

1. **A fabricated zero-count floor.** In [scouting.py:192](/work/submit/novaka/l1pixels/analysis/scouting.py:192), a zero transferred tag fraction becomes \(1/N_{\text{accepted MB}}\). For perfect scouting this creates one minimum-bias event’s luminosity weight—**620,922,695 events**—as four-b background. A zero QCD heavy-flavour estimate must be handled through the QCD sample’s statistical model, not through an unrelated minimum-bias denominator.
2. **Unequal information content.** The offline-tag scouting “ceiling” loses score categories used by the triggered fit. With consistent signal/background models, a superset of events retaining the same observables could reproduce the triggered categories. The reported lower sensitivity therefore cannot establish a ceiling.

The low-HT result also has a narrower meaning than claimed. It measures the fraction below HT150 **after** four L1 jets and the existing mass window. That window was developed in the HT>150 region. Low \(m_{HH}\) and low HT are not interchangeable.

**What changes the verdict:** correct the background treatment, retain the same score categories, test continuous scores and alternative tag multiplicities, and evaluate softer jets/pairing with adequate low-HT background coverage. Until then, the defensible statement is that the particular simple scouting analysis performed poorly.

**G: the study is too pessimistic about serialization, but too optimistic about the completeness of its feasibility model.**

The most consequential finding is in the calibration source:

- [Phase2ITChip.cc:24](/cvmfs/cms.cern.ch/el9_amd64_gcc13/cms/cmssw/CMSSW_17_0_0_pre2/src/DataFormats/Phase2TrackerDigi/src/Phase2ITChip.cc:24) allocates 16 ADC entries for a quarter-core and fills only hit positions.
- [Phase2ITQCore.cc:158](/cvmfs/cms.cern.ch/el9_amd64_gcc13/cms/cmssw/CMSSW_17_0_0_pre2/src/DataFormats/Phase2TrackerDigi/src/Phase2ITQCore.cc:158) nevertheless emits four bits for **every entry**.
- A quarter-core with one hit therefore gets **64 charge bits instead of four**. The documented chip format suppresses unhit pixels. See the [RD53C CMS manual](https://cds.cern.ch/record/2890222/files/rd53cCMS1v92.pdf).

`itlinks/dump_bits.py` faithfully counts this emulator output; the subsequent calibration inherits the inflation. I cannot assign a corrected bandwidth without re-encoding the actual occupancy. The quoted numbers are not a reliable lower bound.

Other checks:

| Issue | Finding and implication |
|---|---|
| **Geometry** | `chip_geom.py:59–120` learns sensor extents and chip splits from hit distributions. The excellent containment validation is useful, but does not validate physical module grouping, chip orientation or link assignment. In particular, a TBPX-L1 sensor detID must not automatically be treated as a complete electronics module. |
| **Windows and layers** | `chip_readout.py:26` uses ±0.8 mm in \(r\phi\), ±8 mm longitudinally, with jets above 30 GeV. `l1ext.py:24` uses ±1.5 mm and ±15 mm, with list production accepting jets above 15 GeV. Readout requests span all learned intersected layers; the refit caps the candidate-bearing layers at four. The effects have opposite directions and cannot be corrected by one scale factor. |
| **Calibration** | The bits-per-cluster calibration comes from only 20 HH+PU200 crossings, transferred by detector region. Entirely outside-acceptance chips can receive zero extrapolation through `chip_readout_merge.py:125`. The 367/123 kHz request rates are hard-coded. |
| **Lanes** | Uniform one-lane operation is pessimistic for TBPX L1; uniform four-lane operation is not the actual system. Published CMS connectivity gives six uplinks per L1 module, while other regions have fewer/shared links. Use the real mapping. [CMS IT system-data-flow table](https://indico.cern.ch/event/1184921/contributions/5596422/attachments/2765161/4816369/hstd13_phase2_IT_v2.pdf) |
| **Request timing** | The studied RoIs use reconstructed jets. The clock must start when those particular seeds are available, not when OT tracks become available. An earlier jet/track seed requires a new efficiency-versus-cost study. |
| **Command distribution** | A regional request requires module addressing, BX/tag bookkeeping and scheduling over shared command links. It cannot be assumed to be an instantaneous arbitrary chip fetch. |
| **Early read versus later L1 accept** | Non-destructive rereading is not demonstrated. Establish the chip’s release semantics. If early readout consumes the fragment, retain it downstream and merge it with the eventual accepted event without holes or duplication. |
| **Buffers and queues** | RD53 has eight latency-memory entries per four-pixel region, a two-level trigger option with configurable retention up to 25.6 μs, and roughly 25 kB of downstream chip buffering. These are not unlimited stored crossings. Test occupancy, retention and loss under ordinary accepts plus regional requests. [RD53 architecture paper, §§5–6](https://iris.poliba.it/bitstream/11589/285601/3/2025_RD53_pixel_readout_integrated_circuits_for_ATLAS_and_CMS_HL-LHC_upgrades_pdfeditoriale.pdf) |
| **Backend and time multiplexing** | Include core-column extraction, framing, lpGBT aggregation, DTC queues, routing, clustering and refit. Time multiplexing can increase processing throughput; it does not divide front-end serialization time or extend hit retention. |

Whole-chip payload is a sensible starting assumption for ordinary chip readout, but the **request granularity may be coarser**, depending on command implementation.

**What changes the verdict:** one validated chip/link model, one common RoI configuration for physics and readout, and a timed end-to-end demonstrator including contention with normal readout. Quote late-event fractions and resulting physics losses, not just median serialization. Fewer layers, selective requests or truncation may help, but each needs its efficiency measured.

**3. Bugs and methodological flaws, ranked by impact**

1. **CROC-format mismatch in the payload calibration.** Directly undermines G’s absolute bandwidth, serialization times and latency no-go.
2. **Unvalidated rare-flavour transfer with no propagated uncertainty.** Can change the pixel-versus-NN κλ ranking in E. Calling model B an artefact is unsupported.
3. **Perfect-tag results remain inconsistent across scripts.** `perfect_ceiling.py` fixes missing minimum-bias truth; scouting still uses it for perfect-seed tuning. Its zero-probability floor fabricates a huge four-tag background.
4. **Scouting “ceilings” discard discriminating information.** They cannot establish F’s general no-sensitivity conclusion.
5. **Physics and hardware use different requests.** Different jet thresholds, windows and layer counts prevent assigning G’s cost to C’s gain.
6. **Offline QCD probabilities are conditioned incorrectly.** Selecting jets by observed UParT and then applying inclusive flavour-only tag probabilities compromises H’s background ratio.
7. **The proposed word size is not the tested headline implementation.** Eight floats plus a software BDT do not establish the quoted performance at 64 bits or within a firmware budget.
8. **Seed definitions differ between headline plots and fits.** `direct_curves.py` optimizes generator-fiducial efficiency; `scouting.py` and `rate_case.py` optimize all-HH efficiency. Equal nominal rate labels do not identify one common seed.
9. **Jet acceptance and weighting inconsistencies.** [train_sets.py:34](/work/submit/novaka/l1pixels/analysis/train_sets.py:34) excludes jets at or above 300 GeV; missing pixel scores can then be treated differently from available NN scores. Its reweighting bins start at 30 GeV although softer jets are included.
10. **Additional implementation defects:** the summary’s last feature is maximum **signed** IP, not maximum absolute IP; `Phase2ITQCoreProducer.cc:112` passes the hit list to `adjustEdges()` by value, so changes do not propagate. These deserve correction before further format validation.

**4. What this group can realistically deliver**

Ranked by expected CMS value relative to effort:

| Rank | Deliverable | Value / effort | Credible scope with present tools and samples |
|---|---|---|---|
| **1** | **A dedicated L1 multijet-seed optimization using available inputs** | High / moderate | Optimize NN scores, OT-track summaries and event topology at measured minimum-bias rates. Measure overlap with the full menu and acceptance after plausible offline selections. This can produce an actionable L1 proposal without depending on regional pixel readout. |
| **2** | **A low-mass HH trigger–HLT–offline acceptance study** | High / moderate | Quantify losses from jet thresholds, jet choice and pairing; shortlist softer selections and measure their trigger acceptance. Existing HH samples can support this. Weighted background and sideband closure are needed before claiming sensitivity or HLT bandwidth. |
| **3** | **A corrected IT regional-readout requirements study** | High / moderate, with IT experts | Deliver a reproducible encoder discrepancy, validated payload distributions, real chip/link mapping, and latency/queue requirements. This remains useful even if pixel-assisted L1 tagging is ultimately rejected. |
| **4** | **A validated compact impact-parameter/refit package** | High / moderate to substantial | Quantization, layer removal, hit loss, vertex robustness, tails and event-rate performance. Package the reference algorithm for CMS evaluation. The charm improvement is a useful additional target; FPGA implementation is a separate phase. |
| **5** | **Targeted flavour studies for VBF H→bb and charm-sensitive HLT/analyses** | Medium–high / moderate | Use existing samples to identify where flavour information actually limits acceptance. Deliver process-specific efficiency/rate comparisons and robust charm features, without assuming that all Higgs channels justify new front-end readout. |
| **6** | **A defensible scouting feasibility analysis** | Medium / substantial | Correct the ceilings, equalize observables/categories, and quantify background-transfer uncertainty. The present samples can establish methodological requirements and candidate selections; they cannot support a precise HH κλ projection. |

The strongest PI-level result presently available is **a substantial simulated improvement in dedicated HH trigger acceptance from pixel-assisted impact-parameter information**. Its deployment cost and its eventual κλ benefit remain open research questions.
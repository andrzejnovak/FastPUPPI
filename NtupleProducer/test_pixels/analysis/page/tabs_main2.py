# Tabs 1-5 of the summary page after the Codex conclusions audit (review/conclusions_2026-10-27); exec'd by build_story.py
# (needs img, prov, d_latency, d_roi, d_phase2, d_run3, legend_after).

terms = """
  <details class="more"><summary>Terms used on this page</summary>
    <ul class="bul">
      <li><b>L1 menu, seed:</b> the hardware trigger&#39;s list of rules (seeds); an event is kept if any seed fires. Budget 750&nbsp;kHz of 40&nbsp;MHz.</li>
      <li><b>H<sub>T</sub>:</b> scalar sum of jet p<sub>T</sub>. <b>m<sub>HH</sub>:</b> mass of the Higgs pair. <b>&kappa;<sub>&lambda;</sub>:</b> Higgs self-coupling / SM value (SM = 1); low m<sub>HH</sub> is most sensitive to it.</li>
      <li><b>b efficiency / mistag:</b> share of b jets tagged / of light-quark and gluon jets wrongly tagged.</li>
      <li><b>Offline-selectable:</b> would pass a later analysis selection (four jets, b tags, two Higgs-mass pairs), if the trigger kept it.</li>
      <li><b>Pixel hits:</b> the innermost tracker layers, the only ones that resolve b-hadron decay lengths (~0.5&nbsp;mm); today read out only after an L1 accept.</li>
      <li><b>+2.5 / +15&nbsp;kHz:</b> extra L1 rate for a new b-tagged seed on top of the HT seeds: this study&#39;s benchmark, and the rate of CMS&#39;s published b-tag NN seed (PoS(ICHEP2022)639). Neither is an official allocation.</li>
    </ul>
  </details>"""

tab_hh = f"""
<section class="panel" role="tabpanel" id="p-hh" aria-labelledby="t-hh">
<div class="callout"><b>Answer.</b> Two planned HT seeds miss 40% of simulated HH&rarr;4b, mostly at low m<sub>HH</sub>. A b-tagged seed with today&#39;s NN recovers part of it; adding pixel hits to the L1 tag recovers most of the rest in simulation (algorithm level).
Whether that sharpens &kappa;<sub>&lambda;</sub> beyond the NN depends on a QCD background we cannot yet model reliably. Reading the hits fast enough looks possible after correcting a CMSSW emulator bug, but needs readout features the pixel detector does not have. A simple scouting analysis gained nothing.</div>
{terms}

<div class="step">
  <h2><span class="n">1 · THE GAP</span>Two planned HT seeds miss the soft HH&rarr;4b events</h2>
  <div class="tiles">
    <div><span class="k">All simulated SM HH&rarr;4b</span><span class="v">40% missed</span><span class="s">15k of 37k in 3000&nbsp;fb<sup>&minus;1</sup></span></div>
    <div><span class="k">m<sub>HH</sub> &lt; 400&nbsp;GeV</span><span class="v">64% missed</span><span class="s">this region holds 78% of the &kappa;<sub>&lambda;</sub> information (signal-only measure)</span></div>
    <div><span class="k">Offline-selectable, m<sub>HH</sub> &lt; 400</span><span class="v">40% missed</span><span class="s">16% of all offline-selectable events</span></div>
  </div>
  <figure>{img("gap_mhh.png", "Expected SM HH to 4b events per 50 GeV of generator m_HH, kept and missed by the two planned L1 HT seeds, at trigger level and for offline-selectable events, with the kappa lambda information per bin")}
    <figcaption><b>Below 400&nbsp;GeV the HT seeds miss most events</b>, where the self-coupling information is (top strip). Grey kept, red missed.</figcaption>
    {prov("Signal: SM ggF HH&rarr;4b, Phase2Spring24 PU&nbsp;200, 36.7&nbsp;fb &times; 0.339, 3000&nbsp;fb<sup>&minus;1</sup>; 10,509 odd events (seeds later are tuned on even).",
          "Seeds: <code>PuppiHT450</code> or <code>PuppiHT400 + QuadJet70_55_40_40</code>; on CMSSW 17_0 jets the step1_2024 scalings give online cuts H<sub>T</sub> &gt; 361 / 316&nbsp;GeV (offline-equivalent 450 / 400): 19&nbsp;kHz (TDR: 20). The rest of the menu is not included, so this is not the full menu&#39;s inefficiency.",
          "Offline-selectable: four PUPPI jets &gt; 30&nbsp;GeV, UParT medium tags (4, or 3 + 1 loose), b-response-corrected Higgs window (<code>offline/offline_sel.py</code>).",
          "&kappa;<sub>&lambda;</sub> information per bin: (&part;s/&part;&kappa;<sub>&lambda;</sub>)<sup>2</sup>/s at the SM, signal only (no background). <code>analysis/plot_gap.py</code>.")}
  </figure>
</div>

<div class="step">
  <h2><span class="n">2 · TODAY&#39;S PLAN</span>A b-tagged seed with the L1 NN tagger</h2>
  <ul class="bul">
    <li><b>Its tracks already carry displacement:</b> the NN runs on the 5-parameter (displaced) Outer-Tracker fit. Their d0 differs from HLT pixel tracks by ~545&nbsp;&micro;m (robust width), about the b decay length.</li>
    <li><b>Per jet</b> (HH b jets vs QCD light jets, this configuration): 15% of b jets tagged at 1% mistag.</li>
    <li><b>As a seed</b> (H<sub>T</sub> + summed b scores of the 4 leading jets): all events 60 &rarr; 70% at +2.5&nbsp;kHz, &rarr; 78% at +15&nbsp;kHz.</li>
  </ul>
</div>

<div class="step">
  <h2><span class="n">3 · PATH A</span>Pixel hits in the real-time L1 b tag (simulation, algorithm level)</h2>
  <ul class="bul">
    <li>Prompt L1 tracks are extended into the pixel layers and refit; a BDT gets 8 displacement numbers per jet next to the NN scores (tab 3). Features are floating point: the 64-bit packing is not yet tested.</li>
    <li><b>Per jet: 47% of b jets tagged at 1% mistag</b> (NN 15%).</li>
    <li><b>All events:</b> NN &rarr; pixel 70 &rarr; 78% at +2.5&nbsp;kHz (measured 2.3 / 2.2&nbsp;kHz), 78 &rarr; 86% at +15&nbsp;kHz.</li>
    <li><b>Offline-selectable, m<sub>HH</sub> &lt; 400</b> (187 events): 83 &rarr; 96% at +2.5&nbsp;kHz, 93 &rarr; 99% at +15&nbsp;kHz.</li>
  </ul>
  <figure>{img("recovery.png", "Share kept by L1 for the HT seeds, lower HT cuts, the NN seed, the pixel seed and a QCD-transferred perfect tag, in four populations, at +2.5 and +15 kHz")}
    <figcaption><b>Each panel is one population;</b> filled +2.5&nbsp;kHz, open +15&nbsp;kHz. The perfect tag is a QCD-transferred oracle reference, not a strict ceiling.</figcaption>
    {prov("Seeds: H<sub>T</sub> + sum of the four leading jets&#39; b scores on top of the HT seeds; cuts chosen on even events, quoted on odd (<code>direct_curves.py</code>, which maximises generator-fiducial efficiency).",
          "Rate from 2.0M PU&nbsp;200 minimum-bias crossings (the 120,731 with high stored L1 H<sub>T</sub> re-simulated with pixels); H<sub>T</sub> cuts &ge; 150&nbsp;GeV.",
          "Perfect tag: generator flavour; minimum bias has no flavour record for pileup, so its rate uses unweighted QCD&#39;s P(n<sub>b</sub> | H<sub>T</sub>) (<code>perfect_ceiling.py</code>).",
          "&kappa;<sub>&lambda;</sub> information: signal only. <code>make_story_plots.py recovery</code>.")}
  </figure>
  <figure>{img("klw_vs_rate.png", "Share of offline-selectable events below 400 GeV kept against the extra L1 rate, with the 2.5 and 15 kHz benchmarks")}
    <figcaption><b>The extra rate as an axis:</b> a pixel seed at +1&nbsp;kHz keeps as much as the NN seed at +10&ndash;15&nbsp;kHz.</figcaption>
    {prov("Seeds at 0.5&ndash;15&nbsp;kHz added rate (<code>direct_curves.py</code>); softer offline: jets &gt; 20&nbsp;GeV, looser tags, 40&nbsp;GeV window. <code>make_page_plots.py</code> section 13.")}
  </figure>
  <details class="more"><summary>Efficiency vs m<sub>HH</sub>, cutflow</summary>
    <div class="moregrid">
      <figure>{img("mhh_eff.png", "Fraction kept by L1 against generator m_HH")}
        <figcaption>At +2.5&nbsp;kHz, below 400&nbsp;GeV the pixel seed keeps 66% vs 52% (1.27&times;), up to 1.5&times; in the lowest bin.</figcaption></figure>
      <figure>{img("cutflow.png", "Fraction kept by each L1 option, of all events and of offline-selectable events")}
        <figcaption>Most offline-selectable events are hard and already triggered.</figcaption></figure>
    </div>
  </details>
</div>

<div class="step">
  <h2><span class="n">4 · CHECK</span>The mock offline selection loses low-mass events</h2>
  <ul class="bul">
    <li>At m<sub>HH</sub> 250&ndash;300&nbsp;GeV only 41% have 4 jets above 30&nbsp;GeV, and the pairing rule keeps 2.8% where some pairing would keep 4.4%.</li>
    <li>Jets &gt; 20&nbsp;GeV with pairing by &chi;<sup>2</sup> to (125,&nbsp;125): 2.1&times; the signal-only &kappa;<sub>&lambda;</sub> information measure, for 1.4&times; a rough QCD proxy. The pixel seed&#39;s lead over the NN holds (1.31&times; vs 1.26&times;).</li>
    <li><b>Not yet an analysis gain:</b> the QCD proxy is unweighted and its tag probabilities ignore that jets were chosen by their tag score; background and sidebands need validation.</li>
  </ul>
  <figure>{img("lowmass_sel.png", "Offline selection efficiency vs generator m_HH by step, and kappa lambda information measure delivered with today's and a low-mass-friendly selection")}
    <figcaption><b>Jet thresholds and pairing limit the low-mass analysis more than the trigger.</b></figcaption>
    {prov("<code>offline/offline_lowmass.py</code>: 48k HH&rarr;4b events with offline jets; variants of jet p<sub>T</sub>, pairing, window, tags. QCD proxy: QCDFlat offline jets, H<sub>T</sub> 150&ndash;800, unweighted, inclusive flavour tag probabilities applied to the 4 highest-score jets (a known bias). <code>make_story_plots.py lowmass</code>.")}
  </figure>
</div>

<div class="step">
  <h2><span class="n">5 · WHAT IT BUYS</span>&kappa;<sub>&lambda;</sub>: not determined by this study</h2>
  <ul class="bul">
    <li>An illustrative m<sub>4j</sub>-shape fit at L1-object level, 3000&nbsp;fb<sup>&minus;1</sup>, statistical only, with the minimum bias as background.</li>
    <li><b>Robust:</b> a b-tagged seed removes the second allowed &kappa;<sub>&lambda;</sub> region near 5 that the HT seeds leave.</li>
    <li><b>Not robust:</b> pixel vs NN. The rare 4b QCD background must be transferred from a small, unweighted QCD sample; four transfer models give opposite orderings (table). No model is validated, and background uncertainties are not propagated.</li>
  </ul>
  <figure>{img("kl_scan.png", "Minus two delta log likelihood against kappa lambda and the allowed regions, score-binned background model")}
    <figcaption>One of the four background models (QCD 4b fraction binned in seed score); the ordering of NN and pixel seeds changes with the model.</figcaption>
    {prov("<code>analysis/scouting.py</code>: four leading L1 jets (p<sub>T</sub> &gt; 20), Higgs window, m<sub>4j</sub>, 4- and 3-tag categories, seed-added events in seed-score categories, L1 H<sub>T</sub> &gt; 150; triggered events get offline-like tag probabilities.",
          "Background: minimum bias (6.2&times;10<sup>8</sup> crossings per event) for rate and shape, multiplied by QCD 4b/3b fractions (tag rate assumed independent of m<sub>4j</sub>). Asimov likelihood with fixed background: finite-sample and transfer uncertainties are not included.",
          "Signal templates per &kappa;<sub>&lambda;</sub> from Run-3 generator m<sub>HH</sub> shapes and the &sigma;(&kappa;<sub>&lambda;</sub>) parabola.")}
  </figure>
  <div class="tablewrap"><table>
    <tr><th>+2.5&nbsp;kHz, background model for seed-added events</th><th class="n">Z<sub>SM</sub>: NN / pixel</th><th class="n">SM excluded if &kappa;<sub>&lambda;</sub> = 5: NN / pixel</th></tr>
    <tr><td>A: one inclusive QCD fraction</td><td class="n">1.9 / 2.0</td><td class="n">2.0 / 3.7&sigma;</td></tr>
    <tr><td>B: fraction from the 27&ndash;49 QCD events each seed adds</td><td class="n">2.0 / 1.6</td><td class="n">2.3 / 1.0&sigma;</td></tr>
    <tr><td>C: QCD binned in seed score, score categories</td><td class="n">1.8 / 1.8</td><td class="n">1.6 / 2.2&sigma;</td></tr>
    <tr><td>C with QCD H<sub>T</sub> &lt; 400 only</td><td class="n">1.7 / 1.7</td><td class="n">1.3 / 1.7&sigma;</td></tr>
  </table></div>
  <p class="note col" style="margin:0">Planned HT seeds alone: Z<sub>SM</sub> 1.6, SM excluded at 0.8&sigma; if &kappa;<sub>&lambda;</sub> = 5, in all models. Deciding pixel vs NN needs a validated background transfer (weighted QCD at low H<sub>T</sub>, closure in score, H<sub>T</sub> and mass) and propagated uncertainties.</p>
</div>

<div class="step">
  <h2><span class="n">6 · PATH B</span>Scouting: no useful gain in the simple analysis tested</h2>
  <ul class="bul">
    <li><b>The idea:</b> leave the real-time decision alone; record L1 objects at 40&nbsp;MHz and use the pixel tag there.</li>
    <li><b>Result:</b> HT seeds + pixel scouting 1.609 vs 1.609&sigma; for the HT seeds alone.</li>
    <li><b>Why, in this analysis:</b> scouted events keep L1-quality jets and tags (four L1 tags keep 23% of signal, four offline tags 50%), and every crossing above H<sub>T</sub> 150 competes.</li>
    <li><b>Not a general no-go:</b> softer selections, continuous scores and a corrected background treatment were not tried. It would still need the regional pixel readout, though not within the trigger-decision deadline.</li>
  </ul>
  <figure>{img("scout_why.png", "Per-jet tag curves with the scouting and offline working points, and signal and background after selection for the triggered pixel stream and scouting")}
    <figcaption>Scouted events carry only L1 tags; the background they face is ~14&times; larger.</figcaption>
    {prov("Left: per-jet ROC (HH b vs QCD light, <code>tag_chain.json</code>). Right: yields after the 4b/3b Higgs-window selection (<code>scouting.json</code>, model C).")}
  </figure>
  <figure>{img("scout_reach.png", "L1 HT distribution of HH to 4b events with four L1 jets in the Higgs window")}
    <figcaption>With four L1 jets &gt; 20&nbsp;GeV in this Higgs window, only 1.8&ndash;5.6% of signal lies below H<sub>T</sub> 150; a softer, optimised selection was not studied.</figcaption>
    {prov("<code>analysis/hh_ht_reach.py</code>, conditional on the current four-jet selection and window.")}
  </figure>
</div>

<div class="step">
  <h2><span class="n">7 · WHERE THIS LEAVES US</span>Verdict</h2>
  <div class="paths">
    <div><b>Shown in simulation</b><span class="v">acceptance gain</span><span>Pixel-assisted L1 tagging recovers most offline-selectable low-mass HH&rarr;4b at +2.5&nbsp;kHz (96% vs 83%).</span></div>
    <div><b>Not shown</b><span class="v">&kappa;<sub>&lambda;</sub> gain over NN</span><span>Depends on an unvalidated 4b QCD background model.</span></div>
    <div><b>Open</b><span class="v">hardware</span><span>Bandwidth and serialisation fit after the emulator fix; regional read commands, early seeds, buffering and queueing do not exist yet (tab 4).</span></div>
  </div>
</div>
</section>
"""

tab_deliver = f"""
<section class="panel" role="tabpanel" id="p-deliver" aria-labelledby="t-deliver" hidden>
  <div class="callout"><b>What we can deliver now, without new hardware, and what needs hardware experts.</b> Ranked by value for effort.</div>
  <div class="tablewrap"><table>
    <tr><th>Deliverable</th><th>To</th><th>What we have</th><th>What is still needed</th></tr>
    <tr class="hl"><td><b>1. CMSSW bug report: pixel chip-output emulator</b></td><td>IT / L1 software</td><td><code>Phase2ITQCore</code> writes 4 charge bits for all 16 pixels of a quarter core, hit or not (the chip sends them only for hit pixels): payloads 2.4&ndash;4&times; too large. Also <code>adjustEdges()</code> takes its hit list by value.</td><td>An issue or pull request with a minimal reproduction.</td></tr>
    <tr class="hl"><td><b>2. A dedicated b-tagged multijet seed with today&#39;s NN</b></td><td>L1 menu team</td><td>+2.5&nbsp;kHz: all HH&rarr;4b 60 &rarr; 70%, offline-selectable low-mass 60 &rarr; 83%, removes the second &kappa;<sub>&lambda;</sub> region; +15&nbsp;kHz: 78% / 93%. Standalone it matches the HT seeds&#39; HH efficiency at ~14&nbsp;kHz.</td><td>Overlap with the full menu; HLT emulation; other channels. (The planned 5-parameter tracks add nothing extra: an Outer-Tracker displacement summary on top of the NN gives 69.3% vs 69.5%.)</td></tr>
    <tr class="hl"><td><b>3. Low-mass HH&rarr;4b selection study</b></td><td>HH&rarr;4b Phase-2 projections</td><td>Jets &gt; 20&nbsp;GeV and &chi;<sup>2</sup> pairing double the signal-only &kappa;<sub>&lambda;</sub> information measure; the trigger then matters more.</td><td>Weighted QCD background with real tags, sidebands, mass sculpting.</td></tr>
    <tr><td><b>4. Pixel regional-readout requirements</b></td><td>IT DAQ, L1 architecture</td><td>Corrected payload: 25&ndash;46&nbsp;Gb/s (jet-based request) or ~200&nbsp;Gb/s (early, track-only request) at 367&nbsp;kHz; with the real uplinks per module ~1.2&ndash;1.3&nbsp;&micro;s per crossing, none above 2.5&nbsp;&micro;s.</td><td>Regional read commands; keeping the early-read data for the L1 accept; priority over normal readout in the chip buffers; confirmation of the link map.</td></tr>
    <tr><td><b>5. A compact pixel-refit tagging package</b></td><td>L1 tagger developers</td><td>Extension and refit emulator; 47% at 1% mistag; without barrel layer 1 still 39% (seed: offline-selectable low-mass 91% vs 96%).</td><td>64-bit quantisation, hit loss, vertex robustness, firmware latency.</td></tr>
    <tr><td><b>6. Menu calibration note</b></td><td>L1 menu / jet calibration</td><td>On CMSSW 17_0 jets the step1_2024 scalings give double-jet 95&nbsp;kHz vs 72 on the 14_0 jets they were made for (TDR 71).</td><td>Updated scalings.</td></tr>
    <tr><td><b>7. Minimum-bias flavour caveat</b></td><td>Anyone estimating flavour-tagged rates</td><td>Phase-2 minimum-bias samples carry no generator record for pileup: 99.5% of L1 jets unmatched; truth-flavour rates from them are wrong.</td><td>&mdash;</td></tr>
    <tr><td><b>8. VBF H&rarr;bb tagged seed</b></td><td>VBF Higgs analyses, menu</td><td>+2&nbsp;kHz VBF seed with two tagged jets: 51 &rarr; 56% (NN), 61% (pixels).</td><td>Background and HLT.</td></tr>
    <tr><td class="muted">9. Tools</td><td class="muted">FastPUPPI ntuples</td><td class="muted">Opt-in generator-boson table; chip geometry learned from hits; readout estimator.</td><td class="muted">Pull requests.</td></tr>
  </table></div>
  <ul class="bul">
    <li><b>Not deliverable as is:</b> a &kappa;<sub>&lambda;</sub> projection for pixel vs NN (background model), and pixel scouting (no gain found; a corrected study would be needed first).</li>
  </ul>
  {prov("Codex audit of all conclusions: <code>review/conclusions_2026-10-27/codex_conclusions_review.md</code>. Layer-1-less tagging: <code>l1ext.py</code> <code>SKIP_LIDS=1</code>, <code>run_lists_variant.sh</code>, <code>run_variants.sh</code>; Outer-Tracker summary: <code>MODE=otonly</code> lists. Readout: <code>chip_readout.py</code> (<code>REQ_WIN</code>, <code>REQ_JET_PTMIN</code>, <code>REQ_NOJET</code>), <code>chip_readout_merge.py</code> (<code>CHARGE_FIX</code>, real uplinks).")}
</section>
"""

tab_how = f"""
<section class="panel" role="tabpanel" id="p-how" aria-labelledby="t-how" hidden>
  <div class="callout"><b>In simulation, pixel hits triple the L1 b-tag efficiency at the same 1% mistag: 15 &rarr; 47%.</b> L1 tracks point to a few pixel hits each; refitting with them reveals the displaced tracks of b decays.</div>
  <div class="chain">
    <div><span class="n">1 · SEED</span><b>Prompt L1 track</b><span>4-parameter Outer-Tracker track, p<sub>T</sub> &gt; 2&nbsp;GeV, ~5&nbsp;&micro;s</span></div>
    <div><span class="n">2 · ASSOCIATE</span><b>Pick pixel hits</b><span>&plusmn;1.5&nbsp;mm &times; &plusmn;15&nbsp;mm windows; ~14 candidate clusters per track</span></div>
    <div><span class="n">3 · REFIT</span><b>Displacement from pixels</b><span>87% of picked hits correct; d0 residual vs HLT ~36&nbsp;&micro;m (robust width; tails to ~140)</span></div>
    <div><span class="n">4 · TAG</span><b>Feed the tagger</b><span>8 numbers per jet next to the NN scores (floating point today)</span></div>
  </div>
  <figure>{img("event_display.png", "Event display: tracker, L1 track extrapolated into the pixel layers, search windows, picked hits and refit")}
    <figcaption>One 2.3&nbsp;GeV track in a b jet: refit d0&nbsp;=&nbsp;498&nbsp;&micro;m (HLT pixel track: 532).</figcaption>
    {prov("<code>analysis/event_display.py</code> on <code>local_v3/perfNano_HH4b_0.root</code>, event 1, track 27; extension and refit in <code>analysis/l1ext.py</code>.")}
  </figure>
  <div class="figrow">
    <figure>{img("d0_resolution.png", "Transverse impact parameter residuals relative to HLT pixel tracks: outer-tracker 5-parameter fit vs L1 track with pixel hits")}
      <figcaption>d0 residual vs HLT pixel tracks: ~545&nbsp;&micro;m (Outer Tracker) &rarr; ~35&nbsp;&micro;m (with pixel hits). Different track populations; robust widths.</figcaption>
      {prov("Residual vs the matched HLT pixel track; HH&rarr;4b. <code>l1ext_validate.py</code>, <code>make_page_plots.py</code> section 5.")}
    </figure>
    <figure>{img("roc_chain.png", "b efficiency vs light mistag for the chain of taggers")}
      <figcaption>At 1% mistag: 15% (NN) &rarr; 19% (Outer Tracker) &rarr; <b>47%</b> (pixels); HLT pixel tracks 50%; offline 84%.</figcaption>
      {prov("HH b jets vs QCD light jets (reweighted to the b-jet p<sub>T</sub>, &eta;), L1 jets p<sub>T</sub> 15&ndash;300&nbsp;GeV; BDT, even/odd folds. <code>tag_compare.py</code>.")}
    </figure>
  </div>
  <div class="tablewrap"><table>
    <tr><th>What the tagger gets</th><th>Content</th><th class="n">b eff. at 1% / 10% mistag</th></tr>
    <tr><td>Today&#39;s L1 NN</td><td>16 particles &times; 21 features; displacement from the 5-parameter Outer-Tracker fit</td><td class="n">15 / 35%</td></tr>
    <tr><td>+ Outer-Tracker displacement summary</td><td>the same tracks&#39; d0, summarised per jet (no gain as a seed)</td><td class="n">19 / 44%</td></tr>
    <tr class="hl"><td><b>+ pixel summary</b></td><td>3 largest d0 significances, number of tracks, tracks above 3&sigma; and 5&sigma;, summed positive significance, largest signed d0</td><td class="n"><b>47 / 78%</b></td></tr>
    <tr><td>+ pixel summary, no barrel layer 1</td><td>same, layer 1 hits not used (readout option)</td><td class="n">39 / 70%</td></tr>
    <tr><td class="muted">Offline UParT (reference)</td><td class="muted">full offline tracking</td><td class="n muted">84 / 94%</td></tr>
  </table></div>
  <figure>{img("jet_eff.png", "Per-jet b efficiency and light mistag against L1 jet pT and eta at 10 percent inclusive mistag")}
    <figcaption><b>Pixels tag soft jets:</b> below 40&nbsp;GeV the NN tags at most ~10% of b jets.</figcaption>
    {prov("<code>seed_plane.py</code> per-jet scores (odd events), <code>make_page_plots.py</code> section 12.")}
  </figure>
  <details class="more"><summary>Alternatives tested</summary>
    <ul class="bul">
      <li><b>Recalibrated 3D displacement:</b> per jet 47 &rarr; 54% at 1%, but the seed keeps fewer events (75.7 vs 77.8% at ~2.1&nbsp;kHz); pileup in the longitudinal term is a likely, untested cause. The transverse part alone: 78.6%.</li>
      <li><b>A network on raw hits:</b> no gain at our training sizes; FPGA graph networks exceed 4&nbsp;&micro;s above ~900 hits (arXiv:2112.02048).</li>
    </ul>
  </details>
</section>
"""

tab_flow = f"""
<section class="panel" role="tabpanel" id="p-flow" aria-labelledby="t-flow" hidden>
  <div class="callout warn"><b>Can the pixel chips deliver one crossing&#39;s hits in time?</b> After correcting a CMSSW emulator bug and using the real links, bandwidth and serialisation fit (~1.2&nbsp;&micro;s per crossing). What the detector lacks: a regional read command, early seeds, and a way to keep the early-read data for the L1 accept.</div>
  <div class="tiles">
    <div><span class="k">Time for the pixel step</span><span class="v">~2.5&ndash;3 &micro;s</span><span class="s">between L1 tracks (~5&nbsp;&micro;s) and final jets (~9.5&nbsp;&micro;s)</span></div>
    <div><span class="k">Out of the pixel detector</span><span class="v">25&ndash;200&nbsp;Gb/s</span><span class="s">whole chips; jet-based to track-only request, at H<sub>T</sub> &gt; 140 (corrected)</span></div>
    <div><span class="k">Readout time per crossing</span><span class="v">~1.2&nbsp;&micro;s</span><span class="s">median, real links per module; none above 2.5&nbsp;&micro;s</span></div>
  </div>
  <div class="chain">
    <div><span class="n">1 · L1 TRACKS</span><b>Request seeds</b><span>outer tracker, ~5&nbsp;&micro;s; final jets come too late, so the request needs tracks (or early track jets)</span></div>
    <div style="border-color:var(--warn)"><span class="n" style="color:var(--warn)">2 · REQUEST · MISSING</span><b>Regional read command</b><span>&ldquo;send this crossing&rdquo; to ~80&ndash;360 modules</span></div>
    <div><span class="n">3 · READ</span><b>Whole chips</b><span>~1.2&nbsp;&micro;s with the real links</span></div>
    <div style="border-color:var(--warn)"><span class="n" style="color:var(--warn)">4 · KEEP · MISSING</span><b>Hold for the L1 accept</b><span>reading a crossing removes it from the chip</span></div>
    <div><span class="n">5 · REFIT + TAG</span><b>64 bits per jet</b><span>to the NN tagger</span></div>
  </div>
  <figure>{img("readout2.png", "Volume out of the pixel detector and readout time per crossing for the emulator payload and the corrected payload, with one link per chip or the real links per module, and three request definitions")}
    <figcaption><b>The emulator bug and a one-link model made it look impossible;</b> corrected, the time fits for every request definition tested.</figcaption>
    {prov("Emulator bug: <code>Phase2ITQCore::encodeQCore</code> writes 4 ToT bits for all 16 pixels of a 4&times;4 quarter core (<code>Phase2ITQCore.cc:158</code>); the CROC sends them only for hit pixels. Correction per module and crossing: quarter cores = bits / (64 + F), corrected = cores &times; F + 4 &times; hit pixels, F = 20 non-charge bits (12&ndash;30 scanned: payload &times;0.25&ndash;0.41).",
          "Links: CMS IT system data flow (hstd13 talk): uplinks per module TBPX L1&ndash;L4 6/2/2/1, TFPX rings 3/3/2/2 at 1.28&nbsp;Gb/s; time per module = its touched chips&#39; bits / its uplinks; crossing time = slowest module. Queueing behind normal readout is not modelled.",
          "Geometry learned from hits on HLT pixel tracks (<code>chipgeo.py</code>); requests: jets &gt; 30 + narrow windows, jets &gt; 15 + the tagging&#39;s windows, or every L1 track (<code>chip_readout.py</code>); 23,411 minimum-bias crossings.")}
  </figure>
  <figure>{d_latency}
    {legend_after("Phase-2 L1 latency budget")}
    <figcaption>Phase-2 L1 latency budget (L1 TDR, CERN-LHCC-2020-004).</figcaption></figure>
  <div class="tablewrap"><table>
    <tr><th>Per crossing (corrected payload)</th><th class="n">H<sub>T</sub> &gt; 140 (367&nbsp;kHz)</th><th class="n">H<sub>T</sub> &gt; 200 (123&nbsp;kHz)</th></tr>
    <tr><td>Into the tagger (64 bits per jet)</td><td class="n">0.06&nbsp;Gb/s</td><td class="n">0.02&nbsp;Gb/s</td></tr>
    <tr><td>Whole chips, jets &gt; 30, narrow windows (68 chips)</td><td class="n">25&nbsp;Gb/s</td><td class="n">10&nbsp;Gb/s</td></tr>
    <tr><td>Whole chips, as tagged: jets &gt; 15, wide windows (129 chips)</td><td class="n">46&nbsp;Gb/s</td><td class="n">17&nbsp;Gb/s</td></tr>
    <tr><td>Whole chips, early request: every L1 track (542 chips)</td><td class="n">200&nbsp;Gb/s</td><td class="n">65&nbsp;Gb/s</td></tr>
    <tr><td class="muted">For scale: full pixel readout at 750&nbsp;kHz (corrected)</td><td class="n muted" colspan="2">~6&nbsp;Tb/s: even the early request adds ~3%</td></tr>
  </table></div>
  <details class="more"><summary>What else must be true (from the audit)</summary>
    <ul class="bul">
      <li><b>Regional commands:</b> module addressing and crossing bookkeeping over shared command links.</li>
      <li><b>Early read vs later L1 accept:</b> the fragment read early must be kept downstream and merged into the accepted event.</li>
      <li><b>Buffers and queues:</b> the request must not wait behind normal readout in the chip output buffer; chip memories are finite.</li>
      <li><b>Back-end:</b> link aggregation, DTC queues, routing, clustering and refit add latency not modelled here.</li>
    </ul>
  </details>
  <details class="more"><summary>Diagrams: Phase-2 baseline, Run 3, and the earlier jet-cone concept</summary>
    <figure style="margin-top:10px">{d_phase2}<figcaption>Phase-2 L1 baseline as configured in CMSSW.</figcaption></figure>
    <figure style="margin-top:10px">{d_run3}<figcaption>Run-3 L1: calorimeters and muons only; first b tag at the software trigger (HLT).</figcaption></figure>
    <figure style="margin-top:10px">{d_roi}<figcaption><b>Earlier concept, superseded:</b> whole jet cones read and tracked locally.</figcaption></figure>
  </details>
</section>
"""

tab_rate = f"""
<section class="panel" role="tabpanel" id="p-rate" aria-labelledby="t-rate" hidden>
  <div class="callout"><b>A b tag buys rate or lower thresholds for a dedicated seed.</b> A pixel-tagged multijet seed matches the HT seeds&#39; HH&rarr;4b efficiency at ~3.4&nbsp;kHz (NN ~14, H<sub>T</sub> only ~21; interpolated), or at their rate lowers the H<sub>T</sub> cut from 340 to 170&nbsp;GeV. The HT seeds serve other physics, so this is a case for adding a seed, not for reclaiming theirs.</div>
  <div class="tiles">
    <div><span class="k">Rate for the HT seeds&#39; 60% of HH&rarr;4b</span><span class="v">~3.4&nbsp;kHz</span><span class="s">pixel; NN ~13.7; H<sub>T</sub> only ~21 (interpolated between optimised points)</span></div>
    <div><span class="k">At ~20&nbsp;kHz</span><span class="v">H<sub>T</sub> &gt; 170</span><span class="s">vs 340 (H<sub>T</sub> only, 18.9&nbsp;kHz): keeps 76% vs 57% (pixel point measured at 21.4&nbsp;kHz)</span></div>
    <div><span class="k">The whole L1 menu</span><span class="v">346 of 750&nbsp;kHz</span><span class="s">TDR (450 with margin); no seed uses a b tag</span></div>
  </div>
  <figure>{img("rate_case.png", "HH to 4b efficiency against the rate of a single seed, and the rate each needs to match the HT seeds")}
    <figcaption>Right: rate each seed type needs for the HT seeds&#39; efficiency. Left: the efficiency&ndash;rate trade-off.</figcaption>
    {prov("Standalone seeds: H<sub>T</sub> only, or H<sub>T</sub> + summed NN or pixel b scores; cuts chosen on even events (maximising all-HH efficiency), quoted on odd; H<sub>T</sub> &ge; 150. <code>analysis/rate_case.py</code>; <code>make_story_plots.py rate</code>.")}
  </figure>
  <figure>{img("menu_composition.png", "Phase-2 L1 menu by seed category from the L1 TDR table")}
    <figcaption><b>Context:</b> seeds overlap, so the bars do not add up to 346&nbsp;kHz.</figcaption>
    {prov("CMS-TDR-021 menu table at PU&nbsp;200, as reproduced in V. Rekovic, CEPC 2022, slide 21. Our 17_0 double-jet emulation: 95&nbsp;kHz (TDR 71; stored 14_0 jets 72, <code>rate_check.py</code>).")}
  </figure>
</section>
"""

# Tabs 1-4 of the summary page; exec'd by build_story.py (needs img, prov, d_latency, d_roi, d_phase2, d_run3, legend_after, roi_volume).

terms = """
  <details class="more" open><summary>Terms used on this page</summary>
    <ul class="bul">
      <li><b>L1 menu, seed:</b> the hardware trigger&#39;s list of rules (seeds); an event is kept if any seed fires. Budget 750&nbsp;kHz of 40&nbsp;MHz.</li>
      <li><b>H<sub>T</sub>:</b> scalar sum of jet p<sub>T</sub>. <b>m<sub>HH</sub>:</b> mass of the Higgs pair. <b>&kappa;<sub>&lambda;</sub>:</b> Higgs self-coupling / SM value (SM = 1); low m<sub>HH</sub> is most sensitive to it.</li>
      <li><b>b efficiency / mistag:</b> share of b jets tagged / of light-quark and gluon jets wrongly tagged.</li>
      <li><b>Offline-selectable:</b> would pass a later analysis selection (four jets, b tags, two Higgs-mass pairs), if the trigger kept it.</li>
      <li><b>Pixel hits:</b> the innermost tracker layers, the only ones that resolve b-hadron decay lengths (~0.5&nbsp;mm); today read out only after an L1 accept.</li>
    </ul>
  </details>"""

tab_hh = f"""
<section class="panel" role="tabpanel" id="p-hh" aria-labelledby="t-hh">
<div class="callout"><b>Answer.</b> The planned L1 trigger misses 40% of HH&rarr;4b, mostly at low m<sub>HH</sub>, where the self-coupling is measured.
Today&#39;s NN tagger recovers part of it; adding pixel hits to the real-time L1 b tag recovers most of the rest at the same extra rate.
Whether that sharpens &kappa;<sub>&lambda;</sub> beyond the NN depends on the b-rich QCD it also accepts, and on whether pixel chips can be read in time (tab 3). Scouting adds nothing.</div>
{terms}

<div class="step">
  <h2><span class="n">1 · THE GAP</span>The planned HT seeds miss the soft HH&rarr;4b events</h2>
  <div class="tiles">
    <div><span class="k">All SM HH&rarr;4b events</span><span class="v">40% missed</span><span class="s">15k of 37k in 3000&nbsp;fb<sup>&minus;1</sup></span></div>
    <div><span class="k">m<sub>HH</sub> &lt; 400&nbsp;GeV</span><span class="v">64% missed</span><span class="s">this region holds 78% of the &kappa;<sub>&lambda;</sub> information</span></div>
    <div><span class="k">Offline-selectable, m<sub>HH</sub> &lt; 400</span><span class="v">40% missed</span><span class="s">16% of all offline-selectable events</span></div>
  </div>
  <figure>{img("gap_mhh.png", "Expected SM HH to 4b events per 50 GeV of generator m_HH, kept and missed by the planned L1 HT seeds, at trigger level and for offline-selectable events, with the kappa lambda information per bin")}
    <figcaption><b>Below 400&nbsp;GeV the menu misses most events</b>, and that is where the self-coupling information is (top strip). Grey kept, red missed.</figcaption>
    {prov("Signal: SM ggF HH&rarr;4b, Phase2Spring24 PU&nbsp;200, 36.7&nbsp;fb &times; 0.339, 3000&nbsp;fb<sup>&minus;1</sup>; odd events (seeds later are tuned on even).",
          "&ldquo;Planned HT seeds&rdquo;: the HH&rarr;4b-relevant part of the menu, <code>PuppiHT450</code> or <code>PuppiHT400 + QuadJet70_55_40_40</code> (step1_2024 thresholds) on CMSSW 17_0 jets: 19&nbsp;kHz (TDR: 20). The rest of the menu (leptons, single jets&hellip;) is not included.",
          "Offline-selectable: four PUPPI jets &gt; 30&nbsp;GeV, UParT medium tags (4, or 3 + 1 loose), b-response-corrected Higgs window (<code>offline/offline_sel.py</code>).",
          "&kappa;<sub>&lambda;</sub> information per bin: (&part;s/&part;&kappa;<sub>&lambda;</sub>)<sup>2</sup>/s at the SM from Run-3 generator m<sub>HH</sub> shapes; signal only (no background).",
          "<code>analysis/plot_gap.py</code>.")}
  </figure>
</div>

<div class="step">
  <h2><span class="n">2 · TODAY&#39;S PLAN</span>A b-tagged seed with the L1 NN tagger</h2>
  <ul class="bul">
    <li><b>The NN already has displacement information:</b> its tracks come from the planned 5-parameter (displaced) L1 track fit. But that fit uses the outer tracker only: ~545&nbsp;&micro;m resolution, about the b decay length, so b decays are barely seen.</li>
    <li><b>Per jet:</b> 15% of b jets tagged at 1% mistag.</li>
    <li><b>As a seed</b> (H<sub>T</sub> + summed b scores of the 4 leading jets, +2.5&nbsp;kHz): recovers a quarter of the events the HT seeds miss (all events: 60 &rarr; 70%).</li>
  </ul>
</div>

<div class="step">
  <h2><span class="n">3 · PATH A</span>Pixel hits in the real-time L1 b tag</h2>
  <ul class="bul">
    <li>Each outer-tracker L1 track is extended into the pixel layers and refit; the tagger gets 8 displacement numbers per jet (tab 2).</li>
    <li><b>Per jet: 47% of b jets tagged at 1% mistag</b> (NN 15%).</li>
    <li><b>All events:</b> 70 &rarr; 78% (ceiling 82%): recovers 45% of the missed events, vs 25% for the NN.</li>
    <li><b>Offline-selectable, m<sub>HH</sub> &lt; 400:</b> 83 &rarr; 96%: recovers 91% of the missed events, vs 57% for the NN.</li>
  </ul>
  <figure>{img("recovery.png", "Share kept by L1 for the planned HT seeds, lower HT cuts, the NN seed, the pixel seed and a perfect b tag, in four populations: all events, m_HH below 400 GeV, offline-selectable below 400 GeV, and kappa lambda information")}
    <figcaption><b>Each panel is one population.</b> The pixel seed is close to a perfect tag at the same rate once events must also pass the offline selection.</figcaption>
    {prov("All seeds +2.5&nbsp;kHz on top of the HT seeds: H<sub>T</sub> + sum of the four leading jets&#39; b scores; cuts chosen on even events, quoted on odd (<code>direct_curves.py</code>).",
          "Rate from 2.0M PU&nbsp;200 minimum-bias crossings (the 120,731 with high stored L1 H<sub>T</sub> re-simulated with pixels); H<sub>T</sub> cuts &ge; 150&nbsp;GeV, where that sample is complete.",
          "Pixel tagger: BDT on the NN scores, jet p<sub>T</sub>, &eta; and the 8-number pixel summary, trained on even HH b jets vs QCD light jets.",
          "Perfect tag: generator flavour, its rate from QCD&#39;s share of true b jets per H<sub>T</sub> bin (minimum bias has no flavour record; <code>perfect_ceiling.py</code>).",
          "&kappa;<sub>&lambda;</sub> information: signal only. <code>make_story_plots.py recovery</code>.")}
  </figure>
  <details class="more"><summary>Efficiency vs m<sub>HH</sub>, softer offline selections, cutflow</summary>
    <div class="moregrid">
      <figure>{img("mhh_eff.png", "Fraction kept by L1 against generator m_HH, trigger level and offline-selectable, for all options")}
        <figcaption>Below 400&nbsp;GeV the pixel seed keeps 66% vs 52% (1.27&times;), up to 1.5&times; in the lowest bin.</figcaption></figure>
      <figure>{img("klw_vs_rate.png", "Share of offline-selectable events below 400 GeV kept against added rate")}
        <figcaption>A pixel seed at +1&nbsp;kHz keeps as much as the NN seed at +10&ndash;15&nbsp;kHz.</figcaption></figure>
      <figure>{img("cutflow.png", "Fraction kept by each L1 option, of all events and of offline-selectable events")}
        <figcaption>For the total yield most offline-selectable events are hard and already triggered.</figcaption></figure>
    </div>
  </details>
</div>

<div class="step">
  <h2><span class="n">4 · CHECK</span>Is the offline selection hiding the low-mass gain?</h2>
  <ul class="bul">
    <li><b>Yes, the mock selection loses low-mass events:</b> at m<sub>HH</sub> 250&ndash;300&nbsp;GeV only 41% have 4 jets above 30&nbsp;GeV, and the pairing rule discards a third of what remains.</li>
    <li><b>A low-mass-friendly selection</b> (jets &gt; 20&nbsp;GeV, pairing by &chi;<sup>2</sup> to (125,&nbsp;125)) captures 2.1&times; the &kappa;<sub>&lambda;</sub> information for 1.4&times; the QCD background.</li>
    <li><b>The pixel gain survives and grows:</b> with it, the pixel seed delivers 1.31&times; the NN seed&#39;s information (1.26&times; with today&#39;s selection).</li>
  </ul>
  <figure>{img("lowmass_sel.png", "Offline selection efficiency vs generator m_HH by step, and kappa lambda information delivered by each L1 option with today's and a low-mass-friendly selection")}
    <figcaption><b>Jet thresholds and pairing, not the L1, limit the low-mass analysis today.</b></figcaption>
    {prov("<code>offline/offline_lowmass.py</code> (<code>run_lowmass.sh</code>, tier3): 48k HH&rarr;4b events with offline jets; variants of jet p<sub>T</sub> (20/25/30), pairing (|m<sub>1</sub>&minus;m<sub>2</sub>| or &chi;<sup>2</sup> to 125), window (30/40/50&nbsp;GeV), tags.",
          "QCD proxy per variant: same kinematics on QCDFlat offline jets (H<sub>T</sub> 150&ndash;800, unweighted), truth-tag probabilities for the tags; ranked by information-weighted S/&radic;B.",
          "Right: information-weighted kept events &times; L1 decision (odd events), normalised to today&#39;s selection with the NN seed. <code>make_story_plots.py lowmass</code>.")}
  </figure>
</div>

<div class="step">
  <h2><span class="n">5 · WHAT IT BUYS</span>The self-coupling, with a QCD background</h2>
  <ul class="bul">
    <li>A fit of the m<sub>4j</sub> shape, 3000&nbsp;fb<sup>&minus;1</sup>, statistical only, at L1-jet resolution, with background from minimum bias.</li>
    <li><b>The NN seed removes the second allowed &kappa;<sub>&lambda;</sub> region</b> near 5.</li>
    <li><b>At the SM point the pixel and NN seeds tie</b> once we count the real bb&#772; QCD a better b tag also accepts. If &kappa;<sub>&lambda;</sub> is far from 1 the pixel seed is ahead (SM excluded at 1.75 vs 1.4&sigma; for &kappa;<sub>&lambda;</sub> = 5).</li>
    <li><b>Not yet a fair test:</b> the seeds were tuned for efficiency, not for this fit. The pixel inputs include the NN&#39;s, so a pixel seed tuned for sensitivity cannot do worse.</li>
  </ul>
  <figure>{img("kl_scan.png", "Minus two delta log likelihood against kappa lambda and the allowed regions, for the HT seeds, NN seed, pixel seed, HT seeds plus pixel scouting, and scouting alone")}
    <figcaption>Every allowed region is drawn; the gap at 2.5&ndash;4 is the usual &kappa;<sub>&lambda;</sub> degeneracy (same total yield at two values).</figcaption>
    {prov("<code>analysis/scouting.py</code> (<code>run_scouting.sh</code>, tier3): four leading L1 jets (p<sub>T</sub> &gt; 20, |&eta;| &lt; 2.4), Higgs-candidate window, m<sub>4j</sub> as m<sub>HH</sub>, 4- and 3-tag categories, L1 H<sub>T</sub> &gt; 150; triggered events get offline-like tags (b 0.84, c 0.12, light 0.01 per jet).",
          "Background: minimum bias (6.2&times;10<sup>8</sup> crossings per event at 3000&nbsp;fb<sup>&minus;1</sup>) for rate and shape. It has no flavour record, so the 4b/3b fraction comes from QCD: for HT-seed events from all accepted QCD; for seed-added events from QCD binned in the same seed score (deciles of ~650 events).",
          "Model A (one QCD fraction everywhere) gives the pixel seed more credit (Z 2.0 vs NN 1.9). An earlier model using only the 27&ndash;49 QCD events each seed adds made the pixel seed look worse: a small-sample artefact.",
          "Asimov likelihood, &sigma;(&kappa;<sub>&lambda;</sub>) parabola and Run-3 m<sub>HH</sub> shapes for &kappa;<sub>&lambda;</sub> = 0, 1, 2.45, 5. Not included: systematics, offline resolution, VBF HH, non-QCD backgrounds.")}
  </figure>
  <div class="tablewrap"><table>
    <tr><th>3000&nbsp;fb<sup>&minus;1</sup>, stat. only</th><th class="n">Significance of SM HH</th><th class="n">&kappa;<sub>&lambda;</sub> allowed (68%)</th><th class="n">SM excluded if &kappa;<sub>&lambda;</sub> = 5</th></tr>
    <tr><td>Planned HT seeds</td><td class="n">1.6&sigma;</td><td class="n">0.25&ndash;2.3 and 4.2&ndash;5.5</td><td class="n">0.8&sigma;</td></tr>
    <tr><td>+ NN seed</td><td class="n">1.7&sigma;</td><td class="n">0.35&ndash;2.1</td><td class="n">1.4&sigma;</td></tr>
    <tr class="hl"><td><b>+ pixel seed</b></td><td class="n">1.7&sigma;</td><td class="n">0.35&ndash;2.1</td><td class="n"><b>1.75&sigma;</b></td></tr>
  </table></div>
</div>

<div class="step">
  <h2><span class="n">6 · PATH B</span>Scouting: no added HH sensitivity in this study</h2>
  <ul class="bul">
    <li><b>The idea:</b> leave the real-time decision alone; record L1 objects at 40&nbsp;MHz and use the pixel tag there, as a fallback if real-time pixels are too hard.</li>
    <li><b>Result:</b> HT seeds + pixel scouting 1.6&sigma; = HT seeds alone; NN seed + pixel scouting 1.7&sigma; = NN seed alone.</li>
  </ul>
  <figure>{img("scout_why.png", "Left: per-jet b efficiency against light mistag for the L1 NN, L1 plus pixel and offline UParT, with the scouting and offline working points. Right: signal and background after selection for the triggered pixel stream and for scouting")}
    <figcaption><b>Why:</b> scouted events never get offline reconstruction, so four L1 tags (23% of signal) replace four offline tags (50%), and every crossing above H<sub>T</sub> 150 competes.</figcaption>
    {prov("Left: per-jet ROC (HH b jets vs QCD light, <code>tag_chain.json</code>); scouting working point = best of 0.2&ndash;5% mistag in <code>scouting.py</code>. Right: yields after the 4b/3b Higgs-window selection (<code>scouting.json</code>). <code>make_story_plots.py scout</code>.")}
  </figure>
  <figure>{img("scout_reach.png", "L1 HT distribution of HH to 4b events with four L1 jets in the Higgs window, for kappa lambda 1, 2.45 and 5, with the scouting floor, pixel-seed HT cut and menu HT thresholds")}
    <figcaption><b>Lower mass is not reachable either:</b> events with four jets &gt; 20&nbsp;GeV in the Higgs window sit above H<sub>T</sub> 150 (only 1.8&ndash;5.6% below), and the pixel seed already reaches down to 170.</figcaption>
    {prov("<code>analysis/hh_ht_reach.py</code>: four L1 jets &gt; 20&nbsp;GeV, |&eta;| &lt; 2.4, Higgs window as <code>scouting.py</code>; weighted to &kappa;<sub>&lambda;</sub> with the generator m<sub>HH</sub> shapes. The scouting floor is where our re-simulated minimum bias is complete. <code>make_story_plots.py reach</code>.")}
  </figure>
  <div class="tablewrap"><table>
    <tr><th>What each path needs</th><th class="n">Path A: real time</th><th class="n">Path B: scouting</th></tr>
    <tr><td>Regional pixel readout on request, before the chips&#39; buffers expire (tab 3)</td><td class="n">needed</td><td class="n">needed</td></tr>
    <tr><td>Track extension and tagger inside the ~2.5&ndash;3&nbsp;&micro;s budget</td><td class="n">needed</td><td class="n">not needed</td></tr>
    <tr><td>New b-tagged seed in the L1 menu</td><td class="n">needed</td><td class="n">not needed</td></tr>
    <tr><td>Full offline reconstruction of the recovered events</td><td class="n">yes</td><td class="n">no</td></tr>
  </table></div>
  <p class="note col" style="margin:0">So the fallback saves the latency-critical processing, not the readout, which is the hardest part.</p>
</div>

<div class="step">
  <h2><span class="n">7 · WHERE THIS LEAVES US</span>Verdict</h2>
  <div class="paths">
    <div><b>Path A: pixel seed</b><span class="v">recovers most events</span><span>45% of missed events overall, 91% of the offline-selectable low-mass ones. &kappa;<sub>&lambda;</sub> gain over the NN: tie at the SM, ahead if &kappa;<sub>&lambda;</sub> &ne; 1; a sensitivity-tuned seed is the next test.</span></div>
    <div><b>Path B: scouting</b><span class="v">no added sensitivity</span><span>Same significance as the trigger it accompanies, in both background models tested.</span></div>
    <div><b>Open</b><span class="v">readout in time</span><span>Whole chips must be read: 73&nbsp;Gb/s and ~9&nbsp;&micro;s per crossing on one e-link (tab 3). Plus: a low-mass-optimised analysis selection.</span></div>
  </div>
</div>
</section>
"""

tab_how = f"""
<section class="panel" role="tabpanel" id="p-how" aria-labelledby="t-how" hidden>
  <div class="callout"><b>Pixel hits triple the L1 b-tag efficiency at the same 1% mistag: 15 &rarr; 47%.</b> L1 tracks point to a few pixel hits each; refitting with them reveals the displaced tracks of b decays.</div>
  <div class="chain">
    <div><span class="n">1 · SEED</span><b>Outer-tracker L1 track</b><span>p<sub>T</sub> &gt; 2&nbsp;GeV, ready at ~5&nbsp;&micro;s</span></div>
    <div><span class="n">2 · ASSOCIATE</span><b>Pick pixel hits</b><span>~14 hit clusters per track window, of ~58k per crossing</span></div>
    <div><span class="n">3 · REFIT</span><b>Displacement from pixels</b><span>87% of picked hits correct; d0 within 35&nbsp;&micro;m of the HLT</span></div>
    <div><span class="n">4 · TAG</span><b>Feed the tagger</b><span>8 numbers per jet (64 bits) next to the NN scores</span></div>
  </div>
  <figure>{img("event_display.png", "Event display: tracker, L1 track extrapolated into the pixel layers, search windows, picked hits and refit")}
    <figcaption>One 2.3&nbsp;GeV track in a b jet: refit d0&nbsp;=&nbsp;498&nbsp;&micro;m (HLT pixel track: 532).</figcaption>
    {prov("<code>analysis/event_display.py</code> on <code>local_v3/perfNano_HH4b_0.root</code>, event 1, track 27; extension and refit in <code>analysis/l1ext.py</code>.")}
  </figure>
  <div class="figrow">
    <figure>{img("d0_resolution.png", "Transverse impact parameter residuals relative to HLT pixel tracks: outer-tracker 5-parameter fit vs L1 track with pixel hits")}
      <figcaption>Displacement resolution: 545&nbsp;&micro;m (outer tracker, what the NN gets) &rarr; 35&nbsp;&micro;m (with pixel hits).</figcaption>
      {prov("Residual vs the HLT pixel track matched to the same L1 track; HH&rarr;4b jets. <code>l1ext_validate.py</code>, <code>make_page_plots.py</code> section 5.")}
    </figure>
    <figure>{img("roc_chain.png", "b efficiency vs light mistag: L1 NN, plus outer-tracker displacement summary, plus pixel hits, HLT pixel tracks, offline UParT")}
      <figcaption>At 1% mistag: 15% (NN) &rarr; 19% (outer tracker) &rarr; <b>47%</b> (pixels); HLT pixel tracks 50%; offline 84%. Higher is better.</figcaption>
      {prov("b jets from HH&rarr;4b, light jets from QCD (reweighted to the b-jet p<sub>T</sub>, &eta;), L1 jets p<sub>T</sub> &gt; 15; BDT on NN scores + jet kinematics + summary, even/odd folds. <code>tag_compare.py</code>.")}
    </figure>
  </div>
  <div class="tablewrap"><table>
    <tr><th>What the tagger gets</th><th>Content</th><th class="n">b eff. at 1% / 10% mistag</th></tr>
    <tr><td>Today&#39;s L1 NN</td><td>16 particles per jet &times; 21 features each; displacement from the 5-parameter outer-tracker fit</td><td class="n">15 / 35%</td></tr>
    <tr><td>+ outer-tracker displacement summary</td><td>the same tracks&#39; d0, summarised per jet</td><td class="n">19 / 44%</td></tr>
    <tr class="hl"><td><b>+ pixel summary</b></td><td>3 largest d0 significances, number of tracks, tracks above 3&sigma; and above 5&sigma;, summed significance, largest |d0|</td><td class="n"><b>47 / 78%</b></td></tr>
    <tr><td class="muted">Offline UParT (reference)</td><td class="muted">full offline tracking</td><td class="n muted">84 / 94%</td></tr>
  </table></div>
  <figure>{img("jet_eff.png", "Per-jet b efficiency and light mistag against L1 jet pT and eta at 10 percent inclusive mistag")}
    <figcaption><b>Pixels tag soft jets:</b> below 40&nbsp;GeV the NN tags at most ~10% of b jets.</figcaption>
    {prov("<code>seed_plane.py</code> per-jet scores (odd events), <code>make_page_plots.py</code> section 12.")}
  </figure>
  <details class="more"><summary>Alternatives tested</summary>
    <ul class="bul">
      <li><b>Recalibrated 3D displacement:</b> per jet 47 &rarr; 54% at 1%, but the seed gets worse (75.7 vs 77.8% at +2.5&nbsp;kHz): pileup jets look displaced along z. The transverse part alone: +0.8 points.</li>
      <li><b>A network on raw hits:</b> no gain at our training sizes; a jet cone holds ~660 hit clusters at PU&nbsp;200, and FPGA graph networks exceed 4&nbsp;&micro;s above ~900 hits (arXiv:2112.02048).</li>
    </ul>
  </details>
</section>
"""

readout_block = (f"""
  <figure>{img("readout_volume.png", "Bits per crossing for what the tagger needs, the hits inside the track windows, and the whole pixel chips the windows touch, with the readout time per crossing")}
    <figcaption><b>Whole chips, not windows, set the volume, and barrel layer 1 sets the time:</b> its chips hold ~8&nbsp;kbit per crossing, ~6&nbsp;&micro;s on one 1.28&nbsp;Gb/s link.</figcaption>
    {prov("Geometry learned from 48M hits on HLT pixel tracks (module ID + position): module planes, 1, 2 or 4 chips per module as in the CMSSW chip emulator; hit-to-module assignment 100% correct on independent hits (<code>chipgeo.py</code>, <code>chip_geom.py</code>).",
          "Requesting L1 tracks and narrow windows as <code>bits_budget.py</code>; a chip is read if a window overlaps it; 23,411 minimum-bias crossings (<code>chip_readout.py</code>, <code>run_chip_readout.sh</code>, tier3).",
          "Bits per chip = its hit clusters &times; bits per cluster per layer and ring (145&ndash;220 barrel, ~135 disks), calibrated on the CMSSW chip emulator (chip medians reproduced to 5&ndash;20%). Payload only: lower bounds.",
          "Readout time = slowest touched chip&#39;s bits / link speed; the real link configuration is not in CMSSW, so 1 and 4 lanes per chip bracket it.")}
  </figure>""" if roi_volume else "")

tab_flow = f"""
<section class="panel" role="tabpanel" id="p-flow" aria-labelledby="t-flow" hidden>
  <div class="callout warn"><b>The open question: can the pixel chips deliver one crossing&#39;s hits in time?</b> The tagger needs little data, but a request has to read whole chips: ~73&nbsp;Gb/s and ~9&nbsp;&micro;s per crossing with one link per chip, against a ~2.5&ndash;3&nbsp;&micro;s budget.</div>
  <div class="tiles">
    <div><span class="k">Time for the pixel step</span><span class="v">~2.5&ndash;3 &micro;s</span><span class="s">between L1 tracks (~5&nbsp;&micro;s) and final jets (~9.5&nbsp;&micro;s)</span></div>
    <div><span class="k">Into the tagger</span><span class="v">64 bits per jet</span><span class="s">the jet word to the final trigger decision is unchanged</span></div>
    <div><span class="k">Out of the pixel detector</span><span class="v">73&nbsp;Gb/s</span><span class="s">~68 whole chips per crossing at H<sub>T</sub> &gt; 140 (28&nbsp;Gb/s at H<sub>T</sub> &gt; 200)</span></div>
  </div>
  <div class="chain">
    <div><span class="n">1 · L1 TRACKS</span><b>~15 tracks in jets</b><span>outer tracker, ready at ~5&nbsp;&micro;s, for crossings with H<sub>T</sub> &gt; 140 (367&nbsp;kHz)</span></div>
    <div><span class="n">2 · REQUEST (RoI)</span><b>Ask the chips around them</b><span>&ldquo;send me this crossing&rsquo;s hits&rdquo; before the trigger decides</span></div>
    <div style="border-color:var(--warn)"><span class="n" style="color:var(--warn)">3 · READ · UNPROVEN</span><b>Whole chips come back</b><span>~68 chips, 2&times;10<sup>5</sup> bits; ~9&nbsp;&micro;s on one link per chip</span></div>
    <div><span class="n">4 · REFIT</span><b>Extend tracks into pixels</b><span>picks ~14 hits per track</span></div>
    <div><span class="n">5 · TAG</span><b>64 bits per jet</b><span>to the NN tagger, then the L1 decision</span></div>
  </div>
  <figure>{d_latency}
    {legend_after("Phase-2 L1 latency budget")}
    <figcaption>Phase-2 L1 latency budget (L1 TDR, CERN-LHCC-2020-004): the pixel step must fit between L1 tracks and the jet tagger.</figcaption></figure>
  <div class="step">
    <h2><span class="n">WHAT IS AN ROI REQUEST</span>Asking for one crossing&#39;s hits, near L1 tracks</h2>
    <ul class="bul">
      <li><b>Today:</b> every pixel chip stores its hits for the 12.5&nbsp;&micro;s trigger latency, then sends them only if L1 accepts the crossing.</li>
      <li><b>A region-of-interest (RoI) request</b> asks only the chips near L1 tracks in jets to send a crossing&#39;s hits <i>before</i> the decision, for the ~1% of crossings that pass a loose H<sub>T</sub> pre-selection.</li>
      <li><b>Unknown:</b> whether chips can answer such a request mid-latency. Reading a crossing removes it from the chip, and the chip&#39;s two-level trigger mode is not a regional fetch.</li>
    </ul>
  </div>
  <div class="step">
    <h2><span class="n">TWO DIFFERENT DATA VOLUMES</span>What the tagger needs vs what must be read</h2>
    <ul class="bul">
      <li><b>Into the tagger: tiny,</b> 64 bits per jet (or one extra bit per particle).</li>
      <li><b>Out of the detector: large.</b> A pixel chip (2.2&nbsp;&times;&nbsp;1.7&nbsp;cm) cannot send a window: it sends <i>all</i> its hits for that crossing.</li>
    </ul>
  </div>{readout_block}
  <ul class="bul">
    <li><b>~68 chips</b> (45 modules) are read per crossing; only 46 of them hold a hit the refit uses.</li>
    <li><b>Time, not only volume:</b> median 9.2&nbsp;&micro;s with one link per chip (99.7% of crossings above 2.5&nbsp;&micro;s); 4.0&nbsp;&micro;s if barrel layer 1 is skipped; 2.3&nbsp;&micro;s with 4 links per chip (30% still above 2.5&nbsp;&micro;s).</li>
    <li><b>So path A needs</b> multi-link readout of the innermost chips, or a tagger without barrel layer 1 (its tagging cost is not yet measured).</li>
  </ul>
  <div class="tablewrap"><table>
    <tr><th>Per crossing</th><th>What it is</th><th class="n">Bits</th><th class="n">H<sub>T</sub> &gt; 140 (367&nbsp;kHz)</th><th class="n">H<sub>T</sub> &gt; 200 (123&nbsp;kHz)</th></tr>
    <tr><td>Request</td><td>~15 L1 tracks &times; 64 bits</td><td class="n">~1,000</td><td class="n">0.3&nbsp;Gb/s</td><td class="n">0.1&nbsp;Gb/s</td></tr>
    <tr><td>Into the tagger</td><td>64 bits per jet</td><td class="n">~170</td><td class="n">0.06&nbsp;Gb/s</td><td class="n">0.02&nbsp;Gb/s</td></tr>
    <tr><td>Hits inside the track windows</td><td>~210 hit clusters at the chip&#39;s encoding</td><td class="n">~32,000</td><td class="n">12&nbsp;Gb/s</td><td class="n">5&nbsp;Gb/s</td></tr>
    <tr class="hl"><td><b>Whole chips the windows touch</b></td><td>~68 chips, ~1,260 hit clusters</td><td class="n"><b>~200,000</b></td><td class="n"><b>73&nbsp;Gb/s</b></td><td class="n"><b>28&nbsp;Gb/s</b></td></tr>
    <tr><td class="muted">For scale: full pixel readout</td><td class="muted">every chip, per L1 accept</td><td class="n muted">24,000,000</td><td class="n muted" colspan="2">18&nbsp;Tb/s at 750&nbsp;kHz</td></tr>
  </table></div>
  <details class="more"><summary>What CMSSW says about the pixel readout</summary>
    <ul class="bul">
      <li>The whole pixel detector produces ~2.4&times;10<sup>7</sup> bits per crossing (~130 bits per hit cluster): 18&nbsp;Tb/s at 750&nbsp;kHz.</li>
      <li>The module &rarr; link &rarr; back-end cabling map exists (3,892 modules, 1,342 optical links, 28 boards); <b>the electrical link configuration and spare capacity do not</b>: a question for the pixel DAQ experts.</li>
      <li>Prompt L1 tracks carry d0 = 0; a pixel-refit d0 fits the existing 13-bit field, so the downstream formats can stay.</li>
    </ul>
  </details>
  <details class="more"><summary>Diagrams: Phase-2 baseline, Run 3, and the earlier jet-cone concept</summary>
    <figure style="margin-top:10px">{d_phase2}<figcaption>Phase-2 L1 baseline as configured in CMSSW.</figcaption></figure>
    <figure style="margin-top:10px">{d_run3}<figcaption>Run-3 L1: calorimeters and muons only; first b tag at the software trigger (HLT).</figcaption></figure>
    <figure style="margin-top:10px">{d_roi}<figcaption><b>Earlier concept, superseded:</b> whole jet cones read and tracked locally (~800 hit clusters per jet). The study now uses narrow windows around L1 tracks (above).</figcaption></figure>
  </details>
</section>
"""

tab_rate = f"""
<section class="panel" role="tabpanel" id="p-rate" aria-labelledby="t-rate" hidden>
  <div class="callout"><b>A b tag buys rate or lower thresholds.</b> One dedicated pixel-tagged multijet seed keeps the HT seeds&#39; HH&rarr;4b efficiency at 3.4&nbsp;kHz instead of 19, or at their rate lowers the H<sub>T</sub> cut from 340 to 170&nbsp;GeV. This is a standalone dedicated seed, not a saving on the whole menu.</div>
  <div class="tiles">
    <div><span class="k">Rate to keep the HT seeds&#39; 60% of HH&rarr;4b</span><span class="v">3.4&nbsp;kHz</span><span class="s">pixel-tagged seed; NN-tagged 13.7; H<sub>T</sub> only 21</span></div>
    <div><span class="k">At the same ~20&nbsp;kHz</span><span class="v">H<sub>T</sub> &gt; 170</span><span class="s">instead of 340 (H<sub>T</sub> only): keeps 76% instead of 57%</span></div>
    <div><span class="k">The whole L1 menu</span><span class="v">346 of 750&nbsp;kHz</span><span class="s">TDR (450 with margin); no seed uses a b tag</span></div>
  </div>
  <figure>{img("rate_case.png", "HH to 4b efficiency against the rate of a single seed for HT only, HT plus NN, HT plus pixel and perfect tag, with the HT seeds marked; and the rate each needs to match them")}
    <figcaption><b>Right panel first:</b> the rate each seed type needs for the HT seeds&#39; efficiency. Left: the full efficiency&ndash;rate trade-off.</figcaption>
    {prov("Standalone seeds (no other menu): H<sub>T</sub> only, or H<sub>T</sub> + summed NN or pixel b scores of the 4 leading jets; cuts chosen on even events, quoted on odd; H<sub>T</sub> &ge; 150. Perfect tag with flavour-aware rate.",
          "Our emulated HT seeds: 19&nbsp;kHz (TDR: 20). <code>analysis/rate_case.py</code> on <code>seed_plane.npz</code>; <code>make_story_plots.py rate</code>.")}
  </figure>
  <ul class="bul">
    <li>The HT seeds also serve other hadronic physics, so the case is for <b>adding</b> a dedicated tagged seed, not for removing them.</li>
    <li>On top of the full menu the saving is ~2&nbsp;kHz (&lt; 1% of the menu): there the case is efficiency at fixed rate (tab 1).</li>
  </ul>
  <figure>{img("menu_composition.png", "Phase-2 L1 menu by seed category from the L1 TDR table; overlapping seeds, bars do not add up to the total")}
    <figcaption><b>Context: where the L1 bandwidth goes.</b> Seeds overlap, so the bars do not add up to 346&nbsp;kHz. Jets and H<sub>T</sub>: ~200&nbsp;kHz, none flavour-aware.</figcaption>
    {prov("CMS-TDR-021 menu table at PU&nbsp;200, as reproduced in V. Rekovic, CEPC 2022, slide 21; per-seed rates summed by category. Our 17_0 emulation of the double-jet seed is 95&nbsp;kHz (TDR 71): 17_0 jets respond ~6% higher (stored 14_0 jets give 72, <code>rate_check.py</code>).")}
  </figure>
</section>
"""

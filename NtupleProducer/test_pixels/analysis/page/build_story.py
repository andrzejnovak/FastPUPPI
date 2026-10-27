#!/usr/bin/env python3
"""Build the summary page (tabs.html): the HH->4b story first, then how path A works, getting the hits, rate, beyond
HH->4b and code. Styles and diagrams come from the long pilot page (index.html), figures from ../analysis/plots_page.

    python3 build_story.py
Tabs 5 (beyond HH->4b) and 6 (code) are the templates sec_beyond.tmpl and sec_code.tmpl ({img(...)} placeholders).
"""
import base64
import os
import re

SRC = "index.html"
PLOTS = "../analysis/plots_page"
OUT = "tabs.html"

src = open(SRC).read()
css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
fonts = re.search(r'(<link rel="preconnect".*?display=swap">)', src, re.S).group(1)


def diagram(label_start):
    """The <div class="diagram">...</div> block whose svg aria-label starts with label_start."""
    i = src.index(f'aria-label="{label_start}')
    i = src.rindex('<div class="diagram">', 0, i)
    j = src.index("</svg></div>", i) + len("</svg></div>")
    return src[i:j]


def legend_after(block_end_marker):
    i = src.index(block_end_marker)
    i = src.index('<div class="legend">', i)
    return src[i:src.index("</div>", i) + 6]


d_latency = diagram("Phase-2 L1 latency budget")
d_phase2 = diagram("Phase-2 L1 baseline")
d_roi = diagram("Proposed: jet seeds")
d_run3 = diagram("Run 3 L1")


def img(name, alt):
    b = base64.b64encode(open(f"{PLOTS}/{name}", "rb").read()).decode()
    return f'<img src="data:image/png;base64,{b}" alt="{alt}">'


def prov(*items):
    """Collapsible provenance box under a figure: what was run on what."""
    lis = "".join(f"<li>{x}</li>" for x in items)
    return f'<details class="prov"><summary>How this was made +</summary><ul class="tight">{lis}</ul></details>'


def template(name):
    return eval('f"""' + open(name).read() + '"""', {"img": img, "prov": prov})


extra_css = """
.tabbar { display: flex; gap: 4px; flex-wrap: wrap; border-bottom: 1px solid var(--rule) }
.tabbar button { font: 600 15px/1.2 var(--display); color: var(--muted); background: none; border: 0; border-bottom: 3px solid transparent;
  padding: 10px 14px; cursor: pointer; margin-bottom: -1px }
.tabbar button[aria-selected="true"] { color: var(--ink); border-bottom-color: var(--accent) }
.tabbar button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px }
.panel { display: grid; gap: 26px }
.panel[hidden] { display: none }
.chain { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px }
.chain > div { background: var(--surface); border: 1px solid var(--rule); border-radius: 8px; padding: 12px 14px; display: grid; gap: 4px }
.chain .n { font: 600 11px/1 var(--mono); color: var(--accent); letter-spacing: .08em }
.chain b { font: 700 15.5px/1.25 var(--display) }
.chain span { font-size: 14px; color: var(--muted) }
.note { font-size: 14.5px; color: var(--muted) }
details.more { background: var(--surface); border: 1px solid var(--rule); border-radius: 8px; padding: 10px 16px }
details.more summary { cursor: pointer; font-weight: 600 }
details.more[open] summary { margin-bottom: 14px }
.moregrid { display: grid; gap: 22px; min-width: 0 }
details.prov { font-size: 13.5px; color: var(--muted); margin-top: 6px }
details.prov summary { cursor: pointer; font: 600 12.5px/1.4 var(--mono); color: var(--accent); list-style: none }
details.prov summary::-webkit-details-marker { display: none }
details.prov[open] { background: var(--surface); border: 1px solid var(--rule); border-radius: 8px; padding: 8px 14px }
details.prov ul { margin: 6px 0 2px }
.step { display: grid; gap: 14px }
.step > h2 { margin: 0; font: 700 21px/1.25 var(--display) }
.step > h2 .n { font: 600 12px/1 var(--mono); color: var(--accent); letter-spacing: .1em; display: block; margin-bottom: 6px }
.lead { font-size: 16.5px; margin: 0; max-width: 74ch }
ul.bul { margin: 0; padding-left: 20px; display: grid; gap: 5px; max-width: 80ch }
ul.bul li { font-size: 15.5px }
.paths { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px }
.paths > div { background: var(--surface); border: 1px solid var(--rule); border-radius: 8px; padding: 14px 16px; display: grid; gap: 6px }
.paths b { font: 700 16px/1.25 var(--display) }
.paths .v { font: 700 22px/1.1 var(--display) }
.paths span { font-size: 14px; color: var(--muted) }
"""

roi_volume = os.path.exists(f"{PLOTS}/readout_volume.png")

# ------------------------------------------------------------------------------------------------------------------
tab_hh = f"""
<section class="panel" role="tabpanel" id="p-hh" aria-labelledby="t-hh">

<div class="step">
  <h2><span class="n">1 · THE GAP</span>The planned menu has no b tag, and HH&rarr;4b pays for it at low m<sub>HH</sub></h2>
  <div class="tiles">
    <div><span class="k">Missed at trigger level</span><span class="v">40%</span><span class="s">15k of 37k SM HH&rarr;4b in 3000&nbsp;fb<sup>&minus;1</sup></span></div>
    <div><span class="k">Missed below m<sub>HH</sub> = 400&nbsp;GeV</span><span class="v">64%</span><span class="s">where 78% of the &kappa;<sub>&lambda;</sub> information is</span></div>
    <div><span class="k">Missed after offline 4b + 3b</span><span class="v">16%</span><span class="s">40% below 400&nbsp;GeV: 37% of the usable &kappa;<sub>&lambda;</sub> information</span></div>
  </div>
  <figure>{img("gap_mhh.png", "Expected SM HH to 4b events per 50 GeV of generator m_HH, kept and missed by the planned L1 menu, at trigger level and for offline-selectable events, with the kappa lambda information per bin")}
    <figcaption><b>The soft events carry the self-coupling, and the menu drops them.</b> Grey kept, red missed (share per bin).</figcaption>
    {prov("Signal: SM ggF HH&rarr;4b, Phase2Spring24 PU&nbsp;200, 36.7&nbsp;fb &times; 0.339, 3000&nbsp;fb<sup>&minus;1</sup>; odd events (seeds later are tuned on even).",
          "Menu: <code>PuppiHT450</code> or <code>PuppiHT400 + QuadJet70_55_40_40</code> (step1_2024 online thresholds) on CMSSW 17_0 seeded-cone jets: 19&nbsp;kHz (TDR: 20).",
          "Offline 4b + 3b: four PUPPI jets &gt; 30&nbsp;GeV, UParT medium (3 + 1 loose), b-response-corrected Higgs window (<code>offline/offline_sel.py</code>).",
          "&kappa;<sub>&lambda;</sub> information per bin: (&part;s/&part;&kappa;<sub>&lambda;</sub>)<sup>2</sup>/s at the SM from Run-3 generator m<sub>HH</sub> shapes (&kappa;<sub>&lambda;</sub> = 0, 1, 2.45); signal-dominated limit.",
          "<code>analysis/plot_gap.py</code> on <code>curves_flags.npz</code>, generator m<sub>HH</sub>.")}
  </figure>
</div>

<div class="step">
  <h2><span class="n">2 · TODAY&#39;S PLAN</span>A b-tagged seed with the L1 NN tagger</h2>
  <ul class="bul">
    <li><b>What it sees:</b> per jet, 16 PUPPI candidates &times; 21 features (p<sub>T</sub>, &Delta;&eta;, &Delta;&phi;, particle type, z<sub>0</sub>, d<sub>xy</sub>, PUPPI weight&hellip;).</li>
    <li><b>Its only displacement input is d<sub>xy</sub> from Outer-Tracker tracks</b> (8-bit &radic;|d<sub>xy</sub>|): too coarse for b decays (545&nbsp;&micro;m resolution, tab 2). No pixel information.</li>
    <li><b>Per jet:</b> 15% b efficiency at 1% light mistag, 35% at 10%.</li>
    <li><b>As a seed</b> (HT + sum of the 4 leading jets&#39; scores, +2.5&nbsp;kHz on top of the menu): 60 &rarr; 70% of all events, 60 &rarr; 83% of offline-selected below 400&nbsp;GeV. CMS shows the same trend (b-tag NN at 15&nbsp;kHz, PoS(ICHEP2022)639).</li>
  </ul>
</div>

<div class="step">
  <h2><span class="n">3 · PATH A</span>Pixel hits in the real-time L1 decision</h2>
  <ul class="bul">
    <li>Extend each Outer-Tracker L1 track into the 4 pixel layers, refit d0 and z0, give the tagger an 8-number displacement summary per jet (tab 2).</li>
    <li>Per jet: <b>47% b efficiency at 1% light</b> (NN: 15%; HLT pixel tracks with the same method: 50%).</li>
  </ul>
  <figure>{img("recovery.png", "Share of SM HH to 4b events kept by L1 for the planned menu, the same rate spent on lower HT cuts, the NN seed, the pixel seed and a perfect b tag: at trigger level for all events and below 400 GeV, and after offline selection below 400 GeV and in kappa lambda information")}
    <figcaption><b>The pixel seed closes most of the gap.</b> After offline selection it keeps 96% of events below 400&nbsp;GeV and 97% of the &kappa;<sub>&lambda;</sub> information, as much as a perfect tag at the same rate.</figcaption>
    {prov("All seeds: +2.5&nbsp;kHz on top of the menu; HT + sum of the four leading jets&#39; per-jet scores; cuts chosen on even events (HH and minimum bias), quoted on odd ones (<code>analysis/direct_curves.py</code>).",
          "Rate: 2.0M PU&nbsp;200 minimum-bias crossings; the 120,731 with high stored L1 HT re-simulated with pixels; HT cuts &ge; 150&nbsp;GeV, where that sample is complete.",
          "Pixel tagger: BDT on the NN scores, jet p<sub>T</sub>, &eta; and the 8-number pixel summary, trained on even HH b jets vs QCD light jets.",
          "Lower-HT control: both menu HT cuts lowered until +2.5&nbsp;kHz (<code>ht_control.py</code>).",
          "Perfect tag: generator flavour, with its minimum-bias rate from the QCD fraction of true b jets per HT bin (minimum bias carries no flavour truth; <code>perfect_ceiling.py</code>); still an upper bound.",
          "<code>analysis/make_story_plots.py recovery</code>.")}
  </figure>
  <figure>{img("mhh_eff.png", "Fraction of SM HH to 4b events kept by L1 against generator m_HH, at trigger level and after offline selection, for the menu, lower HT cuts, the NN seed, the pixel seed and a perfect b tag")}
    <figcaption><b>Where the gain sits:</b> below 400&nbsp;GeV the pixel seed keeps 1.5&times; the NN seed&#39;s events at trigger level.</figcaption>
    {prov("Same seeds and events as above, binned in generator m<sub>HH</sub>; ratio errors binomial, added in quadrature (conservative).", "<code>analysis/make_page_plots.py</code> section 9.")}
  </figure>
  <details class="more"><summary>More: softer offline selections, cutflow, which events are added</summary>
    <div class="moregrid">
      <div class="tablewrap"><table>
        <tr><th>Offline scenario (kept below 400&nbsp;GeV)</th><th class="n">Selected</th><th class="n">Menu</th><th class="n">NN</th><th class="n">Pixel</th><th class="n">Perfect</th></tr>
        <tr><td>Today&#39;s proxy</td><td class="n">7.9%</td><td class="n">60%</td><td class="n">83%</td><td class="n"><b>96%</b></td><td class="n">99%</td></tr>
        <tr><td>Jets &gt; 20&nbsp;GeV</td><td class="n">12.0%</td><td class="n">52%</td><td class="n">74%</td><td class="n"><b>92%</b></td><td class="n">97%</td></tr>
        <tr><td>+ &ge; 3 medium or 4 loose tags</td><td class="n">16.6%</td><td class="n">46%</td><td class="n">70%</td><td class="n"><b>85%</b></td><td class="n">93%</td></tr>
        <tr><td>+ 40&nbsp;GeV mass window</td><td class="n">23.0%</td><td class="n">47%</td><td class="n">70%</td><td class="n"><b>85%</b></td><td class="n">92%</td></tr>
      </table></div>
      <p class="note" style="margin:0">Softer offline selections keep more soft events, and then L1 matters more. <code>offline/offline_scenarios.py</code>, <code>scen_ana.py</code>.</p>
      <figure>{img("klw_vs_rate.png", "Share of offline-selected HH to 4b events below 400 GeV kept by L1 against added rate, NN, pixel and perfect seeds, today's and a softer offline selection")}
        <figcaption>A pixel seed at +1&nbsp;kHz keeps as much as the NN seed at +10&ndash;15&nbsp;kHz.</figcaption></figure>
      <figure>{img("cutflow.png", "Fraction kept by each L1 trigger level, of all SM HH to 4b events and of the events passing the offline 4b plus 3b selection")}
        <figcaption>For the total yield, most selected events are hard and already triggered.</figcaption></figure>
      <figure>{img("offline_eff.png", "Fraction of SM HH to 4b events kept by L1 against offline HT and against the offline b-tag sum")}
        <figcaption>The added events are soft and well tagged offline.</figcaption></figure>
    </div>
  </details>
</div>

<div class="step">
  <h2><span class="n">4 · WHAT IT BUYS</span>The self-coupling, with a background</h2>
  <ul class="bul">
    <li>m<sub>4j</sub>-shape fit at L1-object level, 3000&nbsp;fb<sup>&minus;1</sup>, statistical only; background = the minimum bias itself with QCD 4b / 3b tag fractions.</li>
    <li><b>The NN seed removes the menu&#39;s second &kappa;<sub>&lambda;</sub> minimum</b> (68%: [0.25, 2.30] + a region near 5 &rarr; [0.48, 1.80]).</li>
    <li><b>The pixel seed&#39;s further gain depends on the background it adds:</b> it collects real bb&#772; QCD, whose size we cannot pin down (two models below).</li>
    <li><b>If &kappa;<sub>&lambda;</sub> is far from 1, the low-mass reach pays most:</b> for &kappa;<sub>&lambda;</sub>&nbsp;=&nbsp;5 the SM is excluded at 0.8&sigma; (menu), 2.0&ndash;2.3&sigma; (NN), 1.0&ndash;3.7&sigma; (pixel).</li>
  </ul>
  <figure>{img("kl_scan.png", "Asimov minus two delta log likelihood against kappa lambda for the menu, NN seed, pixel seed, menu plus scouting, and scouting alone, with the 68 and 95 percent intervals")}
    <figcaption>Conservative background model (B). The double well is the usual &kappa;<sub>&lambda;</sub> degeneracy: with the menu alone, the selected yield at &kappa;<sub>&lambda;</sub>&nbsp;=&nbsp;5 equals the SM&#39;s.</figcaption>
    {prov("<code>analysis/scouting.py</code> (<code>run_scouting.sh</code>, tier3): four leading L1 jets (p<sub>T</sub> &gt; 20, |&eta;| &lt; 2.4), pairing by smallest |m<sub>1</sub> &minus; m<sub>2</sub>|, Higgs window, m<sub>4j</sub> as m<sub>HH</sub> proxy, 4- and 3-tag categories, L1 HT &gt; 150.",
          "Triggered streams: L1 accept, then offline-like tags per jet (b 0.84, c 0.12, light 0.01, as UParT medium).",
          "Background: minimum bias (6.2&times;10<sup>8</sup> crossings per event at 3000&nbsp;fb<sup>&minus;1</sup>) for shape and rate; it has no flavour truth, so 4b/3b fractions come from QCD events passing the same seeds (truth-tagged offline jets; closure on the measured 3-tag rate, <code>qcd_tagfrac.py</code>).",
          "Model A: one QCD fraction for all streams. Model B: separate fraction and category for menu-accepted and seed-added events (the pixel-added class has only 27 QCD events).",
          "Signal templates per &kappa;<sub>&lambda;</sub> from Run-3 m<sub>HH</sub> shapes (0, 1, 2.45, 5) and &sigma;(&kappa;<sub>&lambda;</sub>); Asimov Poisson likelihood; bins merged to &ge; 10 minimum-bias events.",
          "Not included: systematics, offline jet resolution and b regression, VBF HH, non-QCD backgrounds.")}
  </figure>
  <div class="tablewrap"><table>
    <tr><th>3000&nbsp;fb<sup>&minus;1</sup>, stat. only</th><th class="n">Z<sub>SM</sub> (A / B)</th><th class="n">&kappa;<sub>&lambda;</sub> 68% (B)</th><th class="n">SM excluded if &kappa;<sub>&lambda;</sub> = 5 (A / B)</th></tr>
    <tr><td>Planned menu</td><td class="n">1.6 / 1.6</td><td class="n">[0.25, 2.30] + 2nd</td><td class="n">0.8 / 0.8&sigma;</td></tr>
    <tr><td>+ NN seed</td><td class="n">1.9 / 2.0</td><td class="n">[0.48, 1.80]</td><td class="n">2.0 / 2.3&sigma;</td></tr>
    <tr class="hl"><td><b>+ pixel seed</b></td><td class="n">2.0 / 1.6</td><td class="n">[0.25, 2.28] + 2nd</td><td class="n"><b>3.7</b> / 1.0&sigma;</td></tr>
  </table></div>
</div>

<div class="step">
  <h2><span class="n">5 · PATH B</span>Scouting as a fallback recovers nothing</h2>
  <ul class="bul">
    <li><b>The idea:</b> leave the real-time decision alone; record L1 objects at 40&nbsp;MHz and use the pixel tag there.</li>
    <li><b>The result:</b> menu + pixel scouting 1.6&sigma; = menu alone; NN seed + pixel scouting 2.0&sigma; = NN seed alone; in both background models.</li>
    <li><b>Why:</b> scouted events never get offline reconstruction; they must be picked with L1 jets and L1 tags (~60% per b jet at 5% mistag vs 84% at 1% offline) out of every crossing above HT 150.</li>
    <li><b>Lower mass is not reachable either:</b> four L1 jets &gt; 20&nbsp;GeV in the Higgs window already imply HT &gt; ~150; only 1.8% (SM) to 5.6% (&kappa;<sub>&lambda;</sub>&nbsp;=&nbsp;5) of such signal lies below.</li>
    <li><b>It saves less than it seems:</b> it still needs the regional pixel readout (tab 3); only the tagger leaves the latency budget.</li>
  </ul>
</div>

<div class="step">
  <h2><span class="n">6 · WHERE THIS LEAVES US</span>Verdict</h2>
  <div class="paths">
    <div><b>Path A: pixel seed</b><span class="v">most of the gap</span><span>Trigger level 70 &rarr; 78% (ceiling 82%); offline-selected below 400&nbsp;GeV 83 &rarr; 96%. Analysis-level &kappa;<sub>&lambda;</sub> gain over the NN depends on the bb&#772; QCD it adds.</span></div>
    <div><b>Path B: scouting</b><span class="v">nothing</span><span>No gain over the trigger it accompanies, in any background model.</span></div>
    <div><b>Open</b><span class="v">feasibility</span><span>Can pixel chips answer a regional request mid-latency, and at what readout volume (tab 3)? Background flavour for the added events needs a larger low-HT QCD sample.</span></div>
  </div>
</div>
</section>
"""

# ------------------------------------------------------------------------------------------------------------------
tab_how = f"""
<section class="panel" role="tabpanel" id="p-how" aria-labelledby="t-how" hidden>
  <div class="chain">
    <div><span class="n">1 · SEED</span><b>Outer Tracker L1 track</b><span>p<sub>T</sub> &gt; 2&nbsp;GeV, ready at ~5&nbsp;&micro;s</span></div>
    <div><span class="n">2 · ASSOCIATE</span><b>Pick pixel hits</b><span>~14 clusters per track window, of ~58k per crossing</span></div>
    <div><span class="n">3 · REFIT</span><b>d0, z0 from pixels</b><span>87% hit purity; d0 within 35&nbsp;&micro;m of HLT</span></div>
    <div><span class="n">4 · TAG</span><b>Feed the tagger</b><span>8 numbers per jet (64 b) next to the NN scores</span></div>
  </div>
  <figure>{img("event_display.png", "Event display in four steps: tracker, L1 track extrapolated into the pixel layers, search windows with candidate clusters, picked hits and refit")}
    <figcaption>One 2.3&nbsp;GeV track in a b jet: refit d0&nbsp;=&nbsp;498&nbsp;&micro;m (HLT pixel track: 532).</figcaption>
    {prov("<code>analysis/event_display.py</code> on <code>local_v3/perfNano_HH4b_0.root</code>, event 1, track 27; extension and refit in <code>analysis/l1ext.py</code>.")}
  </figure>
  <div class="figrow">
    <figure>{img("d0_resolution.png", "Impact parameter residuals with respect to HLT pixel tracks, Outer-Tracker-only displaced L1 tracks vs L1 tracks with pixel hits")}
      <figcaption>Outer Tracker alone: 545&nbsp;&micro;m; with pixel hits: 35&nbsp;&micro;m.</figcaption>
      {prov("Residual vs the HLT pixel track matched to the same L1 track; HH&rarr;4b jets. <code>l1ext_validate.py</code>, <code>make_page_plots.py</code> section 5.")}
    </figure>
    <figure>{img("roc_chain.png", "ROC curves: L1 NN, plus Outer Tracker displaced tracks, plus L1 tracks with pixel hits, plus HLT pixel tracks, offline UParT")}
      <figcaption>b efficiency at 1% light: 15 &rarr; 19 (OT) &rarr; <b>47%</b> (pixels); HLT pixel tracks 50%.</figcaption>
      {prov("b jets from HH&rarr;4b, light jets from QCD (reweighted to the b-jet p<sub>T</sub>, &eta;), L1 jets p<sub>T</sub> &gt; 15; BDT on NN scores + jet kinematics + summary, even/odd folds. <code>tag_compare.py</code> &rarr; <code>tag_chain.json</code>.")}
    </figure>
  </div>
  <div class="tablewrap"><table>
    <tr><th>What the tagger gets</th><th>Content</th><th class="n">b-eff @ 1% / 10% light</th></tr>
    <tr><td>Today&#39;s L1 NN</td><td>16 PUPPI candidates &times; 21 features; d<sub>xy</sub> from Outer-Tracker tracks only</td><td class="n">15 / 35%</td></tr>
    <tr><td>+ OT displaced tracks</td><td>extended (5-parameter) L1 tracks</td><td class="n">19 / 44%</td></tr>
    <tr class="hl"><td><b>+ pixel summary</b></td><td>top-3 d0 significances, track counts above 3 and 5&sigma;, summed significance, max d0 (8 &times; 8 b)</td><td class="n"><b>47 / 78%</b></td></tr>
    <tr><td class="muted">Offline UParT</td><td class="muted">full tracking (reference)</td><td class="n muted">84 / 94%</td></tr>
  </table></div>
  <figure>{img("jet_eff.png", "Per-jet b efficiency and light mistag against L1 jet pT and eta at 10 percent inclusive light mistag, NN, HLT pixel and L1 pixel")}
    <figcaption><b>Pixels tag soft jets:</b> below 40&nbsp;GeV the NN tags almost no b jet.</figcaption>
    {prov("<code>seed_plane.py</code> (per-jet scores, odd events), <code>make_page_plots.py</code> section 12.")}
  </figure>
  <ul class="bul">
    <li><b>Better per-jet tags do not automatically make a better seed.</b> A recalibrated 3D impact parameter lifts the per-jet tag to 54 / 83%, but the seed gets worse (75.7 vs 77.8% at +2.5&nbsp;kHz): pileup jets in minimum bias look displaced in z. The transverse part alone: +0.8 points.</li>
    <li><b>Why tracks, not raw hits:</b> a network on loose hits gave no gain at our training sizes; a jet cone holds ~660 clusters at PU&nbsp;200, and FPGA graph networks exceed 4&nbsp;&micro;s above ~900 hits (arXiv:2112.02048).</li>
  </ul>
</section>
"""

# ------------------------------------------------------------------------------------------------------------------
readout_block = (f"""
  <figure>{img("readout_volume.png", "Bits per crossing for the data the tagger needs, the hits inside the track windows, and the full pixel chips the windows touch, with the readout time per crossing")}
    <figcaption><b>The readout is set by whole chips, not by windows.</b></figcaption>
    {prov("<code>analysis/chip_readout.py</code>: requesting L1 tracks and narrow windows as <code>bits_budget.py</code>; clusters assigned to pixel chips; chip payload calibrated on the CMSSW chip emulator (<code>itlinks/</code>); minimum bias PU&nbsp;200 with L1 HT &gt; 140 / 200.")}
  </figure>""" if roi_volume else """
  <p class="note col" style="margin:0"><b>Chip-level readout volume: being computed</b> (whole chips touched by the windows); the window-only numbers below are a lower bound.</p>""")

tab_flow = f"""
<section class="panel" role="tabpanel" id="p-flow" aria-labelledby="t-flow" hidden>
  <div class="tiles">
    <div><span class="k">Time for the pixel step</span><span class="v">~2.5&ndash;3 &micro;s</span><span class="s">L1 tracks ready at ~5&nbsp;&micro;s; jets must be final by ~9.5&nbsp;&micro;s</span></div>
    <div><span class="k">Into the tagger</span><span class="v">64 b per jet</span><span class="s">the jet word to the Global Trigger is unchanged</span></div>
    <div><span class="k">Out of the pixel detector</span><span class="v">&ge; 4&ndash;10 Gb/s</span><span class="s">hits in the windows only; whole chips are more (below)</span></div>
  </div>
  <figure>{d_latency}
    {legend_after("Phase-2 L1 latency budget")}
    <figcaption>Phase-2 L1 latency budget (L1 TDR, CERN-LHCC-2020-004): the pixel step must fit between L1 tracks and the jet tagger.</figcaption></figure>

  <div class="step">
    <h2><span class="n">WHAT IS AN ROI REQUEST</span>Ask the pixel chips for one crossing, around L1 tracks</h2>
    <ul class="bul">
      <li><b>Today the pixel detector is read only after an L1 accept:</b> every chip buffers its hits for the 12.5&nbsp;&micro;s latency, then sends them or drops them.</li>
      <li><b>A region-of-interest (RoI) request</b> would, for a crossing that passes a loose L1 pre-selection (HT &gt; 140: 367&nbsp;kHz), ask only the chips around the L1 tracks in jets to send that crossing&#39;s hits <i>before</i> the decision.</li>
      <li>The hits go to a track-extension board, which returns a 64-b displacement summary per jet to the tagger.</li>
      <li><b>Unknown, and the key feasibility question:</b> whether chips can answer such a request mid-latency. Reading a crossing is destructive, and the chip&#39;s two-level trigger mode is not a regional fetch.</li>
    </ul>
  </div>
  <figure>{d_roi}
    {legend_after("Proposed: jet seeds")}
    <figcaption>Proposed loop (blue): request buffered pixel hits around L1 objects, return a per-jet summary to the tagger.</figcaption></figure>

  <div class="step">
    <h2><span class="n">TWO DIFFERENT DATA VOLUMES</span>What the tagger needs vs what must be read out</h2>
    <ul class="bul">
      <li><b>Into the tagger: tiny.</b> 64 b per jet, or one extra sign bit per candidate (the existing 8-b d<sub>xy</sub> field).</li>
      <li><b>Out of the detector: much larger.</b> A pixel chip (CROC, 2.2&nbsp;&times;&nbsp;1.7&nbsp;cm) cannot send a window: it sends <i>all</i> its hits for the crossing. The volume is set by the chips the windows touch.</li>
    </ul>
  </div>{readout_block}
  <div class="tablewrap"><table>
    <tr><th>Per crossing (HT &gt; 140 / 200: 367 / 123&nbsp;kHz)</th><th>What it is</th><th class="n">Bits</th><th class="n">Rate</th></tr>
    <tr><td>Request</td><td>15&ndash;18 L1 tracks &times; 64 b</td><td class="n">~1 k</td><td class="n">0.3 / 0.1&nbsp;Gb/s</td></tr>
    <tr><td>Hits in the track windows</td><td>200&ndash;260 clusters at the real chip encoding (~130 b each)</td><td class="n">25&ndash;33 k</td><td class="n">10 / 4&nbsp;Gb/s</td></tr>
    <tr><td>Into the tagger</td><td>64 b per jet</td><td class="n">&lt; 0.5 k</td><td class="n">&mdash;</td></tr>
    <tr><td class="muted">For scale: a full pixel readout</td><td class="muted">every chip, per L1 accept</td><td class="n muted">2.4&times;10<sup>7</sup></td><td class="n muted">18&nbsp;Tb/s at 750&nbsp;kHz</td></tr>
  </table></div>
  {prov("Requesting tracks: L1 tracks p<sub>T</sub> &gt; 2&nbsp;GeV within &Delta;R &lt; 0.4 of L1 jets (p<sub>T</sub> &gt; 30) and |z<sub>0</sub> &minus; z<sub>vtx</sub>| &lt; 1.5&nbsp;cm; narrow windows 0.8&nbsp;mm r-&phi; &times; 8&nbsp;mm (same tagging performance as wide ones). <code>bits_budget.py</code> &rarr; <code>bits_mb.json</code>.",
        "Bits per cluster from the CMSSW chip-output emulator (<code>Phase2ITQCoreProducer</code>, 20 PU&nbsp;200 events, <code>itlinks/</code>).")}
  <details class="more"><summary>What CMSSW says about the pixel readout</summary>
    <ul class="bul">
      <li><b>~2.4&times;10<sup>7</sup> bits per crossing</b> for the whole pixel detector (~130 b per cluster): 18&nbsp;Tb/s at 750&nbsp;kHz.</li>
      <li><b>A chip returns all its hits:</b> median 1.1&nbsp;kbit, 1% above ~8&nbsp;kbit: 1&ndash;6&nbsp;&micro;s on one 1.28&nbsp;Gb/s e-link, comparable to the whole time window.</li>
      <li>Cabling map exists (3,892 modules, 1,342 lpGBT links, 28 back-end boards); <b>the e-link configuration and spare capacity do not</b>: a question for the pixel DAQ experts.</li>
      <li><b>Prompt L1 tracks carry d0 = 0</b>; a pixel-refit d0 fits the existing 13-b field (39&nbsp;&micro;m step), so correlator, tagger and Global Trigger formats can stay.</li>
    </ul>
  </details>
  <details class="more"><summary>Phase-2 baseline and Run-3 L1, for comparison</summary>
    <figure style="margin-top:10px">{d_phase2}<figcaption>Phase-2 L1 baseline as configured in CMSSW.</figcaption></figure>
    <figure style="margin-top:10px">{d_run3}<figcaption>Run-3 L1: calorimeters and muons only; first b tag at the HLT.</figcaption></figure>
  </details>
</section>
"""

# ------------------------------------------------------------------------------------------------------------------
tab_rate = f"""
<section class="panel" role="tabpanel" id="p-rate" aria-labelledby="t-rate" hidden>
  <div class="tiles">
    <div><span class="k">The whole L1 menu</span><span class="v">346 of 750&nbsp;kHz</span><span class="s">TDR, PU&nbsp;200 (450 with 30% margin); no seed uses a b tag</span></div>
    <div><span class="k">HH&rarr;4b-relevant seeds</span><span class="v">20&nbsp;kHz</span><span class="s">PuppiHT450 (11) and QuadJet + HT400 (9)</span></div>
    <div><span class="k">Their HH&rarr;4b efficiency for less rate</span><span class="v">3.4 vs 19&nbsp;kHz</span><span class="s">one pixel-tagged seed; the NN needs 13.7</span></div>
  </div>
  <figure>{img("menu_composition.png", "Phase-2 L1 menu by seed category, sum of seed rates at PU 200 from the L1 TDR table")}
    <figcaption><b>Where the bandwidth goes.</b> Jets and HT take ~200&nbsp;kHz in total, none of it flavour-aware.</figcaption>
    {prov("CMS-TDR-021 menu table at PU&nbsp;200, as reproduced in V. Rekovic, CEPC 2022, slide 21; per-seed rates summed by category (seeds overlap). Our 17_0 emulation: HT seeds 19&nbsp;kHz (TDR 20); double jet 95 (TDR 71: 17_0 jets respond ~6% higher; stored 14_0 jets give 72, <code>rate_check.py</code>).")}
  </figure>
  <div class="step">
    <h2><span class="n">THE RATE CASE</span>A b tag buys either rate or lower thresholds</h2>
    <ul class="bul">
      <li><b>Same efficiency, less rate:</b> to keep the HT seeds&#39; 60% of HH&rarr;4b, one seed needs 21&nbsp;kHz on HT alone, 13.7 with the NN, <b>3.4 with pixels</b>.</li>
      <li><b>Same rate, lower thresholds:</b> at ~20&nbsp;kHz the HT cut drops from 340 (HT only) to 240 (NN) to <b>170&nbsp;GeV (pixels)</b>, keeping 57 &rarr; 65 &rarr; <b>76%</b>.</li>
      <li>The HT seeds also serve other hadronic physics, so this is the case for a <b>dedicated tagged multijet seed</b>, not for removing them.</li>
      <li>On top of the full menu the saving is small (~2&nbsp;kHz, &lt; 1% of the menu): there the case is efficiency at fixed rate (tab 1).</li>
    </ul>
  </div>
  <figure>{img("rate_case.png", "HH to 4b efficiency against the rate of a single seed for HT only, HT plus NN, HT plus pixel and a perfect tag, with the menu HT seeds marked; and the rate each needs to match the menu efficiency")}
    <figcaption><b>Pixels make a tagged multijet seed ~6&times; cheaper than the HT seeds</b> for the same HH&rarr;4b efficiency.</figcaption>
    {prov("Standalone seeds (no menu): HT only, or HT + sum of the four leading jets&#39; NN or pixel scores; cuts chosen on even events, quoted on odd; HT &ge; 150. Perfect tag with flavour-aware rate (<code>perfect_ceiling.py</code>).",
          "<code>analysis/rate_case.py</code> (<code>run_rate_case.sh</code>) on <code>seed_plane.npz</code>; <code>make_story_plots.py rate</code>.")}
  </figure>
  <details class="more"><summary>The seed plane</summary>
    <figure>{img("seed_plane.png", "Seed plane of L1 HT against the sum of b scores, iso-rate lines, NN and pixel")}
      <figcaption>Pixels pull HH&rarr;4b away from minimum bias in the (HT, b-score) plane.</figcaption></figure>
  </details>
</section>
"""

tab_more = template("sec_beyond.tmpl")
tab_code = template("sec_code.tmpl")

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>L1 Pixel b-Tag Pilot</title>
{fonts}
<style>{css}{extra_css}</style>
</head>
<body>
<div class="wrap">
<header class="col" style="display:grid;gap:12px">
  <div class="eyebrow">Pilot study · Phase-2 L1 trigger · October 2026</div>
  <h1>L1 Pixel b-Tag Pilot</h1>
  <p class="lede" style="margin:0">The planned Phase-2 L1 menu has no b tag. How many HH&rarr;4b events does that cost, and can pixel information recover them, in the real-time decision (path A) or in 40&nbsp;MHz scouting (path B)?</p>
</header>
<nav class="tabbar" role="tablist" aria-label="Sections">
  <button role="tab" id="t-hh" aria-controls="p-hh" aria-selected="true">1 · HH&rarr;4b</button>
  <button role="tab" id="t-how" aria-controls="p-how" aria-selected="false" tabindex="-1">2 · How path A works</button>
  <button role="tab" id="t-flow" aria-controls="p-flow" aria-selected="false" tabindex="-1">3 · Getting the hits</button>
  <button role="tab" id="t-rate" aria-controls="p-rate" aria-selected="false" tabindex="-1">4 · Rate</button>
  <button role="tab" id="t-more" aria-controls="p-more" aria-selected="false" tabindex="-1">5 · Beyond HH&rarr;4b</button>
  <button role="tab" id="t-code" aria-controls="p-code" aria-selected="false" tabindex="-1">6 · Code</button>
</nav>
{tab_hh}
{tab_how}
{tab_flow}
{tab_rate}
{tab_more}
{tab_code}
<p class="foot">Simulation: Phase2Spring24 PU&nbsp;200 (HH&rarr;4b SM, QCD, 2.0M minimum bias), CMSSW 17_0_0_pre2 + FastPUPPI. Code: tab 6. Long-form notes: the pilot page.</p>
</div>
<script>
(() => {{
  const tabs = [...document.querySelectorAll('[role="tab"]')];
  const show = (t, focus) => {{
    tabs.forEach(b => {{
      const on = b === t;
      b.setAttribute('aria-selected', on);
      b.tabIndex = on ? 0 : -1;
      document.getElementById(b.getAttribute('aria-controls')).hidden = !on;
    }});
    if (focus) t.focus();
    try {{ history.replaceState(null, '', '#' + t.id.slice(2)); }} catch (e) {{}}
  }};
  tabs.forEach((b, i) => {{
    b.addEventListener('click', () => show(b));
    b.addEventListener('keydown', e => {{
      const d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (d) {{ e.preventDefault(); show(tabs[(i + d + tabs.length) % tabs.length], true); }}
    }});
  }});
  const h = location.hash.slice(1);
  const start = tabs.find(b => b.id === 't-' + h);
  if (start) show(start);
}})();
</script>
</body>
</html>
"""
open(OUT + ".new", "w").write(html)
os.replace(OUT + ".new", OUT)
print(f"wrote {OUT}: {len(html) / 1e6:.2f} MB")

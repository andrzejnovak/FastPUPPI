#!/usr/bin/env python3
"""Build the tabbed summary page (tabs.html) from the long pilot page (styles and diagrams) and plots_page/ PNGs.

    python3 build_tabs.py
"""
import base64
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


extra_css = """
.tabbar { display: flex; gap: 4px; flex-wrap: wrap; border-bottom: 1px solid var(--rule) }
.tabbar button { font: 600 15px/1.2 var(--display); color: var(--muted); background: none; border: 0; border-bottom: 3px solid transparent;
  padding: 10px 14px; cursor: pointer; margin-bottom: -1px }
.tabbar button[aria-selected="true"] { color: var(--ink); border-bottom-color: var(--accent) }
.tabbar button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px }
.panel { display: grid; gap: 28px }
.panel[hidden] { display: none }
.chain { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px }
.chain > div { background: var(--surface); border: 1px solid var(--rule); border-radius: 8px; padding: 12px 14px; display: grid; gap: 4px }
.chain .n { font: 600 11px/1 var(--mono); color: var(--accent); letter-spacing: .08em }
.chain b { font: 700 15.5px/1.25 var(--display) }
.chain span { font-size: 14px; color: var(--muted) }
.note { font-size: 14.5px; color: var(--muted) }
details.more { background: var(--surface); border: 1px solid var(--rule); border-radius: 8px; padding: 10px 16px }
details.more summary { cursor: pointer; font-weight: 600 }
"""

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

<header class="col" style="display:grid; gap:10px">
  <div class="eyebrow">Pilot study · Phase-2 L1 trigger · October 2026</div>
  <h1>L1 Pixel b-Tag Pilot</h1>
  <p class="lede" style="margin:0">Pixel hits make a much better L1 b-tagger, and L1 tracks can pick them up. For SM HH&rarr;4b the analysis gain is small (&times;1.05&ndash;1.11), because the signal is mostly lost offline. The case is soft signals (self-coupling) and rate.</p>
</header>

<div>
<div class="tabbar" role="tablist" aria-label="Sections">
  <button role="tab" id="t-hh" aria-controls="p-hh" aria-selected="true">1 · HH&rarr;4b</button>
  <button role="tab" id="t-flow" aria-controls="p-flow" aria-selected="false" tabindex="-1">2 · Information flow</button>
  <button role="tab" id="t-tag" aria-controls="p-tag" aria-selected="false" tabindex="-1">3 · Tagging</button>
  <button role="tab" id="t-rate" aria-controls="p-rate" aria-selected="false" tabindex="-1">4 · Rate</button>
  <button role="tab" id="t-code" aria-controls="p-code" aria-selected="false" tabindex="-1">5 · Code</button>
  <button role="tab" id="t-more" aria-controls="p-more" aria-selected="false" tabindex="-1">6 · Beyond HH&rarr;4b</button>
</div>
</div>

<!-- ============ TAB 1: HH->4b ============ -->
<section class="panel" role="tabpanel" id="p-hh" aria-labelledby="t-hh">
  <div class="tiles">
    <div><span class="k">Trigger level, SM</span><span class="v">69.5% &rarr; 77.8%</span><span class="s">of all HH&rarr;4b events kept, NN seed &rarr; pixel seed; of offline-selected events: 92.6% &rarr; 97.5%</span></div>
    <div><span class="k">Analysis level, SM</span><span class="v">&times;1.05&ndash;1.11</span><span class="s">equivalent luminosity (offline 4b + 3b); perfect L1 b-tag: &times;1.08</span></div>
    <div><span class="k">Analysis level, &kappa;<sub>&lambda;</sub> = 5</span><span class="v">&times;1.2&ndash;1.5</span><span class="s">soft events the planned menu misses</span></div>
  </div>
  <div class="tablewrap"><table>
    <tr><th>Level</th><th>L1 seeds</th><th class="n">Rate</th></tr>
    <tr><td><b>Current-style</b> <span class="muted">(Run-3 logic: no L1 b-tag)</span></td><td><code>PuppiHT400 and QuadJet70_55_40_40</code> OR <code>PuppiHT450</code> (CMSSW Phase-2 menu)</td><td class="n">19 kHz</td></tr>
    <tr><td><b>Planned</b></td><td>+ HT and &Sigma; of the 4 leading jets&#39; L1 NN b scores</td><td class="n">+2.5 kHz</td></tr>
    <tr><td><b>Potential</b></td><td>same seed, b score from L1 tracks + pixel hits (tab 3)</td><td class="n">+2.5 kHz</td></tr>
    <tr><td class="muted">Ceiling</td><td class="muted">perfect L1 b-tag</td><td class="n muted">+2.5 kHz</td></tr>
  </table></div>
  <figure>{img("cutflow.png", "Fraction kept by each L1 trigger level, of all SM HH to 4b events and of the events passing the offline 4b plus 3b selection")}
    <figcaption><b>The trigger is not the bottleneck for SM.</b> Light bars: share of all events L1 keeps. Dark bars: share of the 7.9% that pass the offline selection. The dark bars are higher because events L1 misses are mostly soft ones the offline selection drops anyway. On the analysed events the planned seeds already keep 92.6%, so even a perfect L1 b-tag adds at most &times;1.08.</figcaption></figure>
  <figure>{img("mhh_categories.png", "Generator m_HH of SM and kappa lambda 5 events, split by which trigger level keeps them, at trigger level and after offline selection")}
    <figcaption><b>What is missed is soft.</b> The gain sits at low m<sub>HH</sub>, which dominates for large &kappa;<sub>&lambda;</sub>. &kappa;<sub>&lambda;</sub>&nbsp;=&nbsp;5 is reweighted from the SM sample; its lowest bins rest on few events.</figcaption></figure>
  <details class="more"><summary>Selection and caveats</summary>
    <p style="margin-top:8px">Offline: PUPPI jets p<sub>T</sub>&nbsp;&gt;&nbsp;30&nbsp;GeV, |&eta;|&nbsp;&lt;&nbsp;2.5; UParT medium (1% light mistag on QCD, 84% on b); four highest-b jets corrected for b-jet response (regression stand-in), paired, mass window 30&nbsp;GeV around (125,&nbsp;120); 4b = all medium, 3b = three medium + one loose. Rates from 2.0M minimum-bias events; thresholds tuned on even events, quoted on odd. Not included: HLT (can only lower the gain), real b regression. Equivalent luminosity: efficiency ratio (background gains equally) to its square (background unchanged).</p>
  </details>
</section>

<!-- ============ TAB 2: information flow ============ -->
<section class="panel" role="tabpanel" id="p-flow" aria-labelledby="t-flow" hidden>
  <div class="tiles">
    <div><span class="k">Window for pixel information</span><span class="v">~2.5&ndash;3 &micro;s</span><span class="s">L1 tracks at 5 &micro;s &rarr; correlator done by 9.5 &micro;s</span></div>
    <div><span class="k">Extra data</span><span class="v">~4&ndash;10 Gb/s</span><span class="s">pixel hits in L1-track windows, 0.3&ndash;1% of crossings, real chip encoding; more if chips can only return all their hits</span></div>
    <div><span class="k">Pixels in L1 today</span><span class="v">None</span><span class="s">read out only after an L1 accept</span></div>
  </div>
  <figure>{d_latency}
    {legend_after("Phase-2 L1 latency budget")}
    <figcaption>Latency budget (Phase-2 L1 TDR, CERN-LHCC-2020-004). Finished jets come too late; L1 tracks and seeds leave a gap of ~2.5&ndash;3&nbsp;&micro;s.</figcaption></figure>
  <figure>{d_roi}
    {legend_after("Proposed: jet seeds")}
    <figcaption>Proposed loop (blue): request buffered pixel hits around L1 objects, return a compact per-jet summary to the tagger. The jet word to the Global Trigger is unchanged. Tab 3 uses L1 tracks as the seeds.</figcaption></figure>
  <div class="col"><h3>Bit budget</h3><p class="note" style="margin:0">Per crossing passing a loose pre-selection (L1 HT &gt; 140 / 200 GeV: 367 / 123 kHz), measured on minimum bias at PU&nbsp;200.</p></div>
  <div class="tablewrap"><table>
    <tr><th>Step</th><th>Content</th><th class="n">Bits / crossing</th><th class="n">HT &gt; 140</th><th class="n">HT &gt; 200</th></tr>
    <tr><td>Request</td><td>15&ndash;18 L1 tracks &times; 64 b (&phi;, &eta;, z<sub>0</sub>, 1/R)</td><td class="n">0.9&ndash;1.2 k</td><td class="n">0.3 Gb/s</td><td class="n">0.1 Gb/s</td></tr>
    <tr><td>Hits back, compact clusters</td><td>200&ndash;260 clusters in the track windows &times; ~36 b</td><td class="n">7&ndash;9 k</td><td class="n">2.7 Gb/s</td><td class="n">1.2 Gb/s</td></tr>
    <tr class="hl"><td><b>Hits back, real chip encoding</b></td><td>the same clusters at ~130 b each (CMSSW chip emulator, below)</td><td class="n">25&ndash;33 k</td><td class="n"><b>~10 Gb/s</b></td><td class="n"><b>~4 Gb/s</b></td></tr>
    <tr><td>Result to correlator</td><td>32 b per track (pixel d0, z0, quality)</td><td class="n">0.5 k</td><td class="n">0.2 Gb/s</td><td class="n">0.1 Gb/s</td></tr>
    <tr><td>Into the tagger</td><td>+1 sign bit per candidate (reusing the 8-bit dxy field), or a 64 b per-jet summary</td><td class="n">&le; 64 / jet</td><td class="n">&ndash;</td><td class="n">&ndash;</td></tr>
    <tr><td>To the Global Trigger</td><td>128-bit jet word, unchanged</td><td class="n">0</td><td class="n">0</td><td class="n">0</td></tr>
    <tr><td class="muted">For scale: whole-cone readout</td><td class="muted">~800 clusters per jet &times; 40 b</td><td class="n muted">~90 k</td><td class="n muted">32 Gb/s</td><td class="n muted">12 Gb/s</td></tr>
    <tr><td class="muted">For scale: L1 track stream (TDR)</td><td class="muted">185 tracks &times; 96 b per &phi; sector, 9 sectors, every crossing</td><td class="n muted">160 k</td><td class="n muted" colspan="2">2 &times; 25 Gb/s fibres per sector</td></tr>
  </table></div>
  <details class="more"><summary>Where the bit widths come from</summary>
    <p style="margin-top:8px">CMSSW 17_0_0_pre2: L1 track word 96 b with a 13-b d0 (39&nbsp;&micro;m step, about our pixel resolution; <code>TTTrack_TrackWord.h</code>); PUPPI candidate 61 b with an 8-b dxy stored as &radic;|dxy|, unsigned (<code>l1ct::PuppiObj</code>, <code>datatypes.h</code>); Global Trigger jet 128 b (<code>gt_datatypes.h</code>). Cluster size: pixel-chip quarter-core encoding (<code>Phase2ITQCore</code>): 6 + 2 + 8 address bits, hit map, 4-b charge per pixel, about 30&ndash;40 b per cluster. Window clusters: narrow windows (0.8&nbsp;mm r-&phi; &times; 8&nbsp;mm), same purity and d0 as the default (87%, 36&nbsp;&micro;m). Track counts: L1 tracks above 2&nbsp;GeV in jets above 30&nbsp;GeV. No design document for a pixel-to-L1 path is in CMSSW; these are to be checked against one.</p>
  </details>
  <div class="col"><h3>What CMSSW says about the pixel readout</h3>
    <p class="note" style="margin:0">From running the emulators and maps in CMSSW 17_0_0_pre2 on 20 PU&nbsp;200 events (<code>itlinks/</code>, tab 5).</p></div>
  <div class="tablewrap"><table>
    <tr><th>Finding</th><th>What it means</th></tr>
    <tr><td><b>Chip output is ~2.4&times;10<sup>7</sup> bits per crossing</b> for the whole pixel detector (emulated chip data stream, <code>Phase2ITQCoreProducer</code>): ~130 b per cluster, 18&nbsp;Tb/s at 750&nbsp;kHz</td><td>3.6&times; the 36 b per cluster assumed in the bit budget: hits back ~10 / 4 Gb/s, not 2.7 / 1.2</td></tr>
    <tr><td><b>A chip returns all its hits</b> for a crossing, not a window: median 1.1&nbsp;kbit, 1% of chips above ~8&nbsp;kbit</td><td>~1&ndash;6 &micro;s per crossing on one 1.28&nbsp;Gb/s e-link: comparable to the whole 2.5&ndash;3&nbsp;&micro;s window</td></tr>
    <tr><td>Module &rarr; lpGBT &rarr; back-end map exists (3,892 modules, 1,342 lpGBTs, 28 boards); <b>the e-link configuration and link capacity do not</b></td><td>Spare bandwidth per link cannot be settled from CMSSW: a question for the pixel DAQ experts</td></tr>
    <tr><td><b>Prompt L1 tracks carry d0 = 0</b> (13-b field always empty); the NN tagger runs on the extended chain, whose d0 comes from the Outer Tracker alone</td><td>A pixel-refit d0 fits in the existing 13-b field (39 &micro;m step &asymp; its resolution): correlator, tagger and Global Trigger formats unchanged</td></tr>
  </table></div>
  <div class="tablewrap"><table>
    <tr><th>Question</th><th>Status</th></tr>
    <tr><td>L1 tracks (Outer Tracker) available at ~5 &micro;s</td><td><span class="pill base">Settled</span> in CMSSW / TDR</td></tr>
    <tr><td>Hits &rarr; displacement in the window (track extension, tab 3)</td><td><span class="pill good">Works in software</span> firmware cost unknown</td></tr>
    <tr><td>Pixel front-ends answer a regional request mid-latency</td><td><span class="pill warn">Needs insiders</span> baseline sends hits only after L1 accept; readout is destructive; the chip&#39;s two-level mode is not a regional fetch</td></tr>
    <tr><td>Request + readout + fit inside ~2.5&ndash;3 &micro;s</td><td><span class="pill warn">Needs insiders</span></td></tr>
  </table></div>
  <details class="more"><summary>Phase-2 baseline and Run-3 diagrams</summary>
    <figure style="margin-top:10px">{d_phase2}<figcaption>Phase-2 L1 baseline as configured in CMSSW.</figcaption></figure>
    <figure style="margin-top:10px">{d_run3}<figcaption>Run-3 L1: calorimeters and muons only; first b-tag at the HLT.</figcaption></figure>
  </details>
</section>

<!-- ============ TAB 3: tagging ============ -->
<section class="panel" role="tabpanel" id="p-tag" aria-labelledby="t-tag" hidden>
  <div class="chain">
    <div><span class="n">1 · SEED</span><b>Outer Tracker L1 track</b><span>p<sub>T</sub> &gt; 2 GeV, at ~5 &micro;s; d0 assumed 0</span></div>
    <div><span class="n">2 · ASSOCIATE</span><b>Pick pixel hits</b><span>~14 clusters in a narrow window per track (of ~58k per event); best helix fit</span></div>
    <div><span class="n">3 · REFIT</span><b>d0, z0 from pixels</b><span>d0 within 35 &micro;m of HLT; 87% hit purity</span></div>
    <div><span class="n">4 · TAG</span><b>Feed the tagger</b><span>8-number displacement summary per jet next to the NN scores</span></div>
  </div>
  <figure>{img("event_display.png", "Event display in four steps: the tracker in 3D; the Outer Tracker L1 track in a transverse slice, extrapolated into the pixel layers; the search windows in the four pixel layers with candidate clusters; the picked hits and the pixel refit with d0 of 498 micrometres")}
    <figcaption>One 2.3&nbsp;GeV track in a 70&nbsp;GeV b jet, zooming in. <b>1</b> tracker; <b>2</b> the Outer Tracker L1 track, extrapolated into the pixels assuming it comes from the beam line; <b>3</b> a &plusmn;1.5&nbsp;mm window per pixel layer holds 29 candidates; <b>4</b> the best-fitting combination is the same 4 hits as the HLT pixel track, and the refit puts the track 498&nbsp;&micro;m from the beam line (HLT: 532&nbsp;&micro;m).</figcaption></figure>
  <div class="figrow">
    <figure>{img("d0_resolution.png", "Impact parameter residuals with respect to HLT pixel tracks for Outer-Tracker-only displaced L1 tracks and for L1 tracks with pixel hits")}
      <figcaption>The Outer Tracker alone cannot see b displacements (545&nbsp;&micro;m); pixel hits bring it to 35&nbsp;&micro;m.</figcaption></figure>
    <figure>{img("roc_chain.png", "ROC curves: L1 NN baseline, plus Outer Tracker displaced tracks, plus L1 tracks with pixel hits, plus HLT pixel tracks, and offline UParT")}
      <figcaption>b efficiency at 1% light mistag: 15% &rarr; 19% (OT) &rarr; <b>47%</b> (pixels), close to HLT pixel tracks (50%).</figcaption></figure>
  </div>
  <div class="tablewrap"><table>
    <tr><th>Tagger</th><th class="n">b-eff @ 1% light</th><th class="n">@ 10%</th><th>What it is</th></tr>
    <tr><td><b>Baseline: L1 NN</b></td><td class="n">15%</td><td class="n">35%</td><td>SC4NG tagger v2_0_0 (TrainTagger), backported to CMSSW 17_0_0_pre2; may lag the newest development. No pixel information.</td></tr>
    <tr><td>+ Outer Tracker displaced tracks</td><td class="n">19%</td><td class="n">44%</td><td>extended (5-parameter) L1 tracks; routing to the correlator less settled</td></tr>
    <tr class="hl"><td><b>+ L1 tracks with pixel hits</b></td><td class="n"><b>47%</b></td><td class="n"><b>78%</b></td><td>this pilot (steps 1&ndash;4)</td></tr>
    <tr><td>+ HLT pixel tracks</td><td class="n">50%</td><td class="n">76%</td><td>same method on HLT pixel tracks (not the HLT&#39;s own b-tagger)</td></tr>
    <tr><td class="muted">Offline UParT</td><td class="n muted">84%</td><td class="n muted">94%</td><td class="muted">offline jets, full tracking; reference only</td></tr>
  </table></div>
  <p class="note col">"+" rows: a small BDT on the NN&#39;s 8 scores plus the pixel summary; the same BDT without pixels reproduces the NN (15% / 36%). b jets from HH&rarr;4b, light jets from QCD, L1 jets p<sub>T</sub>&nbsp;&gt;&nbsp;15&nbsp;GeV.</p>
  <div class="callout"><b>Why not a network on raw hits?</b> Tried: a network on loose hits gave no gain up to the training sizes we had (22&ndash;45k jets); grouping hits into tracks is what recovers displacement. A jet cone holds ~660 pixel clusters at PU&nbsp;200 (1,400 at 90%), and FPGA graph networks exceed 4&nbsp;&micro;s above ~900 hits (arXiv:2112.02048). Seeding on L1 tracks avoids the pattern recognition.</div>
</section>

<!-- ============ TAB 4: rate ============ -->
<section class="panel" role="tabpanel" id="p-rate" aria-labelledby="t-rate" hidden>
  <div class="tiles">
    <div><span class="k">On top of the planned menu</span><span class="v">~0.3 vs 2.3 kHz</span><span class="s">for the same HH&rarr;4b efficiency (pixel vs NN seed)</span></div>
    <div><span class="k">Standalone seed</span><span class="v">2.7 vs 9.6 kHz</span><span class="s">same efficiency, ~3.5&times; less rate</span></div>
  </div>
  <figure>{img("rate_curves.png", "HH to 4b efficiency for offline-selected events versus L1 rate for the NN, HLT-pixel and L1-pixel seeds")}
    <figcaption><b>Same signal, much less rate.</b> The rate freed could go to other triggers. Lowest-rate points rest on few minimum-bias events (order of magnitude only).</figcaption></figure>
</section>

<!-- ============ TAB 5: code ============ -->
<section class="panel" role="tabpanel" id="p-code" aria-labelledby="t-code" hidden>
  <div class="col">
    <p style="margin:0">Everything is on the branch <code>andrzejnovak/FastPUPPI:17_0_X_pixelTracks</code>, in <code>NtupleProducer/test_pixels/</code>; paths below are relative to it. Start with <code>HANDOFF.md</code> there. The working copies on subMIT are in <code>/work/submit/novaka/l1pixels/</code> (<code>analysis/</code> mirrors <code>test_pixels/analysis/</code>; <code>offline/</code> is <code>test_pixels/analysis/offline/</code>). Scripts carry absolute <code>/work</code> and <code>/ceph</code> paths; anything longer than a minute runs on Slurm (<code>--partition=submit</code>), not on the login node.</p>
  </div>
  <pre><span class="c"># environment: CMSSW python with uproot, awkward, matplotlib, sklearn</span>
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/hitdev/CMSSW_17_0_0_pre2/src &amp;&amp; cmsenv     <span class="c"># analysis</span>
cd /work/submit/novaka/l1pixels/ngv2/CMSSW_17_0_0_pre2/src &amp;&amp; cmsenv      <span class="c"># ntuple production</span>
cd /work/submit/novaka/l1pixels/analysis                                   <span class="c"># run analysis scripts from here</span></pre>

  <div class="col"><h3>Every number on this page, and where it comes from</h3></div>
  <div class="tablewrap"><table>
    <tr><th>Result</th><th>Script</th><th>Output</th></tr>
    <tr><td>Tab 1: L1 kept, all events vs offline-selected</td><td><code>analysis/direct_curves.py</code> (seeds at +2.5&nbsp;kHz, perfect tag) on <code>offline/offline_sel.py</code> flags</td><td><code>curves.json</code>, <code>curves_flags.npz</code>, <code>offline_flags2.npz</code></td></tr>
    <tr><td>Tab 1: equivalent luminosity, &kappa;<sub>&lambda;</sub> split, m<sub>HH</sub> categories</td><td><code>analysis/kl_direct.py</code> (<code>SEL=offline_flags2.npz:resolved_4b</code>), <code>kl_reweight.py</code></td><td><code>kl_direct2.json</code>, <code>klreweight/nano_mhh_kl*.npz</code></td></tr>
    <tr><td>Tab 1: offline selection (UParT, b response, pairing)</td><td><code>offline/dump_offline.py</code> (MINIAOD), <code>offline_sel.py</code></td><td><code>offline/b_response.json</code>, <code>offline_flags2.npz</code></td></tr>
    <tr><td>Tab 2: bit budget</td><td><code>analysis/bits_budget.py</code></td><td><code>bits_mb.json</code></td></tr>
    <tr><td>Tab 3: hit association, purity, d0 resolution</td><td><code>analysis/l1ext.py</code> (the extension and refit), <code>l1ext_validate.py</code></td><td><code>l1ext_val/scan_0.json</code></td></tr>
    <tr><td>Tab 3: tagging chain ROC</td><td><code>analysis/make_l1ext_lists.py</code> (<code>MODE=otonly</code> for OT-only), <code>make_lists.py</code> (HLT pixel tracks), <code>tag_compare.py</code></td><td><code>lists_l1ext_*.npz</code>, <code>tag_chain.json</code></td></tr>
    <tr><td>Tab 3: event display</td><td><code>analysis/event_display.py &lt;HH4b ntuple&gt; &lt;png&gt;</code></td><td><code>plots_page/event_display.png</code></td></tr>
    <tr><td>Tab 4: efficiency vs rate</td><td><code>analysis/direct_rate.py</code>, <code>direct_curves.py</code></td><td><code>direct_rate2.json</code>, <code>direct_rate_l1ext.json</code>, <code>curves.json</code></td></tr>
    <tr><td>Tab 6: charm tagging</td><td><code>analysis/ctag_compare.py</code></td><td><code>ctag_chain.json</code></td></tr>
    <tr><td>Tab 6: VBF menu efficiency</td><td><code>analysis/vbf_menu.py</code></td><td><code>vbf_menu.json</code></td></tr>
    <tr><td>Tab 6: boosted H (first look)</td><td><code>analysis/fatjet_first.py</code>; R = 0.8 jet tables: <code>addSC8Jets()</code> in <code>../python/runPerformanceNTuple.py</code></td><td><code>fatjet_first.json</code></td></tr>
    <tr><td>Tab 2: pixel link study</td><td><code>itlinks/bitstream_cfg.py</code>, <code>dump_bits.py</code>, <code>occupancy.py</code></td><td><code>occupancy.json</code></td></tr>
    <tr><td>Private samples (ggH + jet, ZH(&nu;&nu;); Pythia8, Spring24 recipe)</td><td><code>privgen/</code>: fragments, <code>run_privgen.sh</code> (Slurm), <code>run_privgen_osg.sh</code> (OSG)</td><td><code>privgen/*.root</code> on CMS scratch</td></tr>
    <tr><td>VBF-like minimum-bias selection</td><td><code>mbsel/scan_jets.py</code>, <code>mbsel/select_vbf.py</code></td><td><code>select_vbf_loose.json</code></td></tr>
    <tr><td>All plots; this page</td><td><code>analysis/make_page_plots.py</code>; <code>analysis/page/build_tabs.py</code> (run in <code>pilot_page/</code>, reads <code>index.html</code> for styles and diagrams)</td><td><code>plots_page/*.png</code>, <code>tabs.html</code></td></tr>
  </table></div>

  <div class="col"><h3>Pipeline</h3></div>
  <div class="tablewrap"><table>
    <tr><th>Step</th><th>Code</th><th>Slurm runner</th></tr>
    <tr><td>Pixel tables in the ntuples: HLT pixel tracks and hits, all clusters, L1 tracks, L1 vertex</td><td><code>../plugins/PixelTrackTableProducer.cc</code>, <code>../python/runInputs151X.py</code> (<code>addPixelTracks</code>)</td><td>&ndash;</td></tr>
    <tr><td>Ntuples: input step, then FastPUPPI + tagger</td><td><code>step1_cfg.py clusters=True</code>, <code>step2_cfg.py extended=True</code></td><td><code>production/local/slurm_array_v3.sh</code></td></tr>
    <tr><td>Minimum-bias pre-selection (stored L1 HT), targeted re-simulation</td><td><code>production/mbsel/scan_ht.py</code>, <code>select_new.py</code></td><td><code>slurm_scan.sh</code>, <code>run_mbnew.sh</code></td></tr>
    <tr><td>Per-jet input lists</td><td><code>analysis/make_lists.py</code>, <code>make_l1ext_lists.py</code>, <code>merge_lists.py</code></td><td><code>run_direct2.sh</code>, <code>run_l1ext_lists.sh</code>, <code>run_ot_lists.sh</code></td></tr>
    <tr><td>Association settings scan</td><td><code>analysis/l1ext_validate.py</code></td><td><code>run_l1ext_scan.sh</code></td></tr>
    <tr><td>Direct rate test, &kappa;<sub>&lambda;</sub></td><td><code>analysis/direct_rate.py</code>, <code>kl_direct.py</code></td><td><code>run_l1ext_direct.sh</code>, <code>run_offline2.sh</code></td></tr>
    <tr><td>Efficiency vs rate</td><td><code>analysis/direct_curves.py</code></td><td><code>run_curves.sh</code></td></tr>
    <tr><td>Offline jets and selection</td><td><code>offline/dump_offline.py</code>, <code>offline_sel.py</code></td><td><code>offline/slurm_offline.sh</code></td></tr>
    <tr><td>Tagging chain</td><td><code>analysis/tag_compare.py</code></td><td><code>run_tagcmp.sh</code></td></tr>
    <tr><td>Bit budget</td><td><code>analysis/bits_budget.py</code></td><td><code>run_bits.sh</code></td></tr>
    <tr><td class="muted">Earlier steps (seed scan, learning curves, hit regression, minimum-bias mistag)</td><td class="muted"><code>l1_seed.py</code>, <code>train_sets.py</code>, <code>regress_hits.py</code>, <code>mb_mistag.py</code></td><td class="muted">their <code>run_*.sh</code></td></tr>
  </table></div>

  <div class="col"><h3>Data on subMIT</h3></div>
  <div class="tablewrap"><table>
    <tr><th>What</th><th>Where</th></tr>
    <tr><td>Ntuples with clusters, L1 tracks, vertex, PUPPI candidates (HH&rarr;4b, QCD; 21k events each)</td><td><code>/scratch/submit/cms/novaka/l1pixels/local_v3/</code></td></tr>
    <tr><td>Minimum bias with pixels (120,731 high-HT events of 1,999,360)</td><td><code>.../l1pixels/local_mbsel_ext/</code> (official, L1 HT &gt; 90) + <code>.../local_mbnew/</code> (stored HT &gt; 60)</td></tr>
    <tr><td>Offline jets from MINIAOD</td><td><code>.../l1pixels/offline/</code></td></tr>
    <tr><td>Generator m<sub>HH</sub>; Run-3 &kappa;<sub>&lambda;</sub> shapes</td><td><code>.../l1pixels/genmhh/</code>; <code>analysis/klreweight/</code></td></tr>
    <tr><td>Input RAW (needs a grid proxy)</td><td>Phase2Spring24 GEN-SIM-DIGI-RAW-MINIAOD via xrootd, lists in <code>l1pixels/local/jobs_v3.txt</code></td></tr>
  </table></div>

  <div class="col"><h3>Other branches</h3>
    <ul class="tight">
      <li>L1 jet tagger v2_0_0 backported to 17_0_0_pre2: <code>andrzejnovak/cmssw:L1PF_17_0_X_NGJetModel_v2</code> (the v0 model in <code>L1PF_17_0_X</code> is bad).</li>
      <li>Earlier pixel-track tables (2025, hit positions broken): Marc Huwiler&#39;s <code>devPixelsForL1</code> branches.</li>
    </ul>
  </div>
  <div class="callout warn"><b>Gotchas.</b> L1 track curvature sign: <code>l1ext.CURV_SIGN = +1</code> (&minus;1 gives 31% hit purity). Outer-Tracker displaced-track d0 has the opposite sign to the CMS d<sub>xy</sub> convention (flipped in <code>MODE=otonly</code>); keep |d0|&nbsp;&lt;&nbsp;1&nbsp;cm there. Offline PUPPI b jets need the response correction (0.73 at 25&nbsp;GeV to 0.96 at 150&nbsp;GeV) or the Higgs candidates peak near 105&nbsp;GeV. The stored L1 HT in minimum-bias RAW runs low against our emulation, so rate scans use HT cuts &ge;&nbsp;150&nbsp;GeV. <code>direct_rate.py</code> picks thresholds on even events and quotes odd ones; the minimum-bias weight uses <code>MB_TOTAL=1999360</code>.</div>
</section>

<!-- ============ TAB 6: beyond HH->4b ============ -->
<section class="panel" role="tabpanel" id="p-more" aria-labelledby="t-more" hidden>
  <div class="tiles">
    <div><span class="k">L1 charm tag, c vs light at 10%</span><span class="v">16% &rarr; 29%</span><span class="s">today&#39;s NN &rarr; + L1 tracks with pixel hits (same as HLT pixel tracks)</span></div>
    <div><span class="k">VBF H&rarr;cc kept by the planned menu</span><span class="v">57%</span><span class="s">of events in a generator VBF + cc acceptance (H&rarr;bb: 53%)</span></div>
    <div><span class="k">Boosted ggH&rarr;cc, R = 0.8 jets</span><span class="v">In progress</span><span class="s">private samples and minimum bias with large jets are being produced</span></div>
  </div>
  <figure>{img("ctag_roc.png", "ROC curves for L1 charm tagging, c versus light and c versus b, for the L1 NN, Outer-Tracker-only displaced tracks, L1 tracks with pixel hits and HLT pixel tracks")}
    <figcaption><b>Pixels make L1 charm tagging possible.</b> Charm decay lengths (D<sup>0</sup> ~120&nbsp;&micro;m) are below the Outer Tracker&#39;s d0 resolution (545&nbsp;&micro;m), so today&#39;s NN is close to random for charm; pixel hits nearly double the c efficiency at loose working points. Inputs are the 8-number summary built for b; charm-specific inputs should do better.</figcaption></figure>
  <div class="col"><h3>VBF H&rarr;cc and H&rarr;bb: the trigger is a real bottleneck</h3>
    <p class="note" style="margin:0">Generator acceptance: two jets of the Higgs flavour with p<sub>T</sub>&nbsp;&gt;&nbsp;30&nbsp;GeV, |&eta;|&nbsp;&lt;&nbsp;2.4, and two other jets with m<sub>jj</sub>&nbsp;&gt;&nbsp;500&nbsp;GeV, |&Delta;&eta;|&nbsp;&gt;&nbsp;3. Menu seeds emulated with the CMSSW online thresholds (muon seeds not included). Phase2Spring24 PU&nbsp;200, ~20k events per sample.</p></div>
  <div class="tablewrap"><table>
    <tr><th>Fraction of accepted events kept</th><th class="n">VBF H&rarr;cc</th><th class="n">VBF H&rarr;bb</th></tr>
    <tr><td>Acceptance (of all events)</td><td class="n">12.9%</td><td class="n">14.8%</td></tr>
    <tr class="hl"><td><b>Planned menu (any hadronic seed)</b></td><td class="n"><b>57%</b></td><td class="n"><b>53%</b></td></tr>
    <tr><td>VBF seed <code>DoublePuppiJet160_35_mass620</code></td><td class="n">39%</td><td class="n">36%</td></tr>
    <tr><td>SingleJet230 / DoubleJet112 / HT seeds</td><td class="n">28 / 34 / 23%</td><td class="n">26 / 32 / 22%</td></tr>
    <tr><td>Only the VBF seed fires</td><td class="n">12%</td><td class="n">10%</td></tr>
  </table></div>
  <p class="note col" style="margin:0">For comparison, HH&rarr;4b events passing an offline selection are 84% triggered by the menu alone. A VBF seed with lower thresholds plus two flavour-tagged central jets is the natural L1 use of pixels here; its rate is being measured on a VBF-like minimum-bias production (105k events selected from all 2.0M with the stored L1 jets).</p>
  <div class="col"><h3>Boosted ggH&rarr;cc in one large jet (in progress)</h3>
    <ul class="tight">
      <li>Phase-2 L1 already builds R&nbsp;=&nbsp;0.8 seeded-cone jets (own Global Trigger collection) and runs a two-prong tagger on them; no menu seed uses either yet. Its tracks carry d0&nbsp;=&nbsp;0, so it has no flavour information: pixels would turn it into an L1 X&rarr;cc / bb tag.</li>
      <li>Private samples (no Phase-2 ggH&rarr;bb/cc exists): Pythia8 H + jet with top-mass dependence, p&#770;<sub>T</sub>&nbsp;&gt;&nbsp;150&nbsp;GeV, and ZH with Z&rarr;&nu;&nu;, through the official Spring24 GEN-SIM &rarr; PU&nbsp;200 DIGI/L1/HLT recipe.</li>
      <li>Next: efficiency of today&#39;s menu against Higgs p<sub>T</sub>; large-jet mass from PUPPI constituents (the L1 jet mass is not filled); a pixel summary in the R&nbsp;=&nbsp;0.8 cone; H&rarr;cc vs QCD ROC; rate of "large jet + cc tag" seeds.</li>
    </ul>
  </div>
</section>

<p class="foot">Simulation: Phase2Spring24 PU&nbsp;200 (HH&rarr;4b SM, QCD, 2.0M minimum bias), CMSSW 17_0_0_pre2 + FastPUPPI. Code: tab 5. Long-form notes: the pilot page.</p>
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
open(OUT, "w").write(html)
print(f"wrote {OUT}: {len(html) / 1e6:.2f} MB")

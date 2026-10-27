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
details.more[open] summary { margin-bottom: 14px }
.moregrid { display: grid; gap: 22px; min-width: 0 }
.story p { font-size: 18px; margin: 0 }
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
  <p class="lede" style="margin:0">Pixel hits at L1 keep the soft, low-m<sub>HH</sub> HH&rarr;4b events that measure the Higgs self-coupling: 96% instead of 83% after offline selection.</p>
</header>

<div>
<div class="tabbar" role="tablist" aria-label="Sections">
  <button role="tab" id="t-hh" aria-controls="p-hh" aria-selected="true">1 · HH&rarr;4b</button>
  <button role="tab" id="t-flow" aria-controls="p-flow" aria-selected="false" tabindex="-1">2 · Information flow</button>
  <button role="tab" id="t-tag" aria-controls="p-tag" aria-selected="false" tabindex="-1">3 · Tagging</button>
  <button role="tab" id="t-rate" aria-controls="p-rate" aria-selected="false" tabindex="-1">4 · Rate</button>
  <button role="tab" id="t-code" aria-controls="p-code" aria-selected="false" tabindex="-1">5 · Code</button>
  <button role="tab" id="t-more" aria-controls="p-more" aria-selected="false" tabindex="-1">6 · Beyond HH&rarr;4b</button>
  <button role="tab" id="t-kl" aria-controls="p-kl" aria-selected="false" tabindex="-1">7 · &kappa;<sub>&lambda;</sub> fit &amp; scouting fallback</button>
</div>
</div>

<!-- ============ TAB 1: HH->4b ============ -->
<section class="panel" role="tabpanel" id="p-hh" aria-labelledby="t-hh">
  <div class="tiles">
    <div><span class="k">Low m<sub>HH</sub>, where &kappa;<sub>&lambda;</sub> is measured</span><span class="v">83% &rarr; 96%</span><span class="s">offline-selected events below 400&nbsp;GeV kept by L1, NN &rarr; pixel seed</span></div>
    <div><span class="k">Bandwidth for the same &kappa;<sub>&lambda;</sub> reach</span><span class="v">1 vs 15 kHz</span><span class="s">pixel seed at +1&nbsp;kHz &asymp; NN seed at +15&nbsp;kHz, for low-m<sub>HH</sub> events</span></div>
    <div><span class="k">Total SM yield</span><span class="v">&times;1.05&ndash;1.11</span><span class="s">most selected events are hard and already triggered</span></div>
  </div>
  <figure>{img("mhh_eff.png", "Fraction of SM HH to 4b events kept by L1 against generator m_HH, at trigger level and after offline selection, for the Run-3-style menu, lower HT cuts, the NN seed, the pixel seed and a perfect b tag, with the share of the kappa lambda information per m_HH bin and ratios")}
    <figcaption><b>Pixels pay below 400&nbsp;GeV, where 78% of the &kappa;<sub>&lambda;</sub> information is</b> (top strip). Dotted: the same rate spent on lower HT.</figcaption></figure>
  <figure>{img("klw_vs_rate.png", "Share of offline-selected HH to 4b events with m_HH below 400 GeV kept by L1 against the added rate, for the NN, pixel and perfect seeds, with today's and a softer offline selection")}
    <figcaption><b>A pixel seed at +1&nbsp;kHz keeps as much as the NN seed at +10&ndash;15&nbsp;kHz.</b> Softer offline: 20&nbsp;GeV jets, looser tags, wider mass window.</figcaption></figure>
  <div class="tablewrap"><table>
    <tr><th>Kept by L1 (seeds at +2.5&nbsp;kHz)</th><th class="n">All events</th><th class="n">m<sub>HH</sub>&nbsp;&lt;&nbsp;400</th><th class="n">Offline, m<sub>HH</sub>&nbsp;&lt;&nbsp;400</th><th class="n">Softer offline, m<sub>HH</sub>&nbsp;&lt;&nbsp;400</th></tr>
    <tr><td><b>Run-3-style menu</b> <span class="muted">(no L1 b tag, 19&nbsp;kHz)</span></td><td class="n">59.6%</td><td class="n">36.2%</td><td class="n">60.4%</td><td class="n">46.7%</td></tr>
    <tr><td>+ the same 2.5&nbsp;kHz on lower HT cuts</td><td class="n">61.8%</td><td class="n">38.6%</td><td class="n">62.6%</td><td class="n">48.8%</td></tr>
    <tr><td><b>+ NN seed</b> <span class="muted">(planned)</span></td><td class="n">69.5%</td><td class="n">52.3%</td><td class="n">82.9%</td><td class="n">69.7%</td></tr>
    <tr class="hl"><td><b>+ pixel seed</b> <span class="muted">(L1 tracks + pixel hits)</span></td><td class="n"><b>77.8%</b></td><td class="n"><b>65.5%</b></td><td class="n"><b>96.3%</b></td><td class="n"><b>84.9%</b></td></tr>
    <tr><td class="muted">+ perfect b tag (ceiling)</td><td class="n muted">82.2%</td><td class="n muted">71.5%</td><td class="n muted">98.9%</td><td class="n muted">92.3%</td></tr>
  </table></div>
  <figure>{img("offline_eff.png", "Fraction of SM HH to 4b events kept by L1 against offline HT and against the sum of the offline UParT b scores of the four leading jets, for all events and for m_HH below 400 GeV, with ratios")}
    <figcaption><b>The added events are soft, and well b-tagged offline.</b> Right panel: m<sub>HH</sub>&nbsp;&lt;&nbsp;400&nbsp;GeV.</figcaption></figure>
  <details class="more"><summary>More: offline scenarios, total yield, which events each level keeps</summary>
    <div class="moregrid">
      <div class="tablewrap"><table>
        <tr><th>Offline scenario</th><th class="n">Signal selected</th><th class="n">NN seed</th><th class="n">Pixel seed</th><th class="n">Perfect</th></tr>
        <tr><td>Today&#39;s proxy: jets &gt; 30&nbsp;GeV; 4 medium, or 3 medium + 1 loose; 30&nbsp;GeV window</td><td class="n">7.9%</td><td class="n">82.9%</td><td class="n">96.3%</td><td class="n">98.9%</td></tr>
        <tr><td>Jets &gt; 20&nbsp;GeV</td><td class="n">12.0%</td><td class="n">74.3%</td><td class="n">91.9%</td><td class="n">96.5%</td></tr>
        <tr><td>+ &ge; 3 medium (4th any) or 4 loose</td><td class="n">16.6%</td><td class="n">69.8%</td><td class="n">85.2%</td><td class="n">93.2%</td></tr>
        <tr><td>+ 40&nbsp;GeV mass window</td><td class="n">23.0%</td><td class="n">69.7%</td><td class="n">84.9%</td><td class="n">92.3%</td></tr>
      </table></div>
      <p class="note" style="margin:0"><b>Perfect-tag ceiling, corrected.</b> Minimum-bias jets carry no flavour truth, so a seed on generator flavour used to cost no rate (old ceiling: 92.6% of all events, 99.5% of offline-selected below 400&nbsp;GeV). Its rate now comes from the QCD probability of n<sub>b</sub> true b jets among the four leading L1 jets per HT bin (<code>perfect_ceiling.py</code>): at +2.5&nbsp;kHz the best perfect seed is HT&nbsp;&gt;&nbsp;150 with &ge;&nbsp;3 b jets (0.33&nbsp;kHz; &ge;&nbsp;2 b would cost 4.3&nbsp;kHz). Pileup b jets are invisible in QCD too, so this is still an upper bound. The pixel seed closes two thirds of the NN-to-perfect gap (all events 69.5 &rarr; 77.8 of 82.2%).</p>
      <p class="note" style="margin:0">L1 columns: share of selected events with m<sub>HH</sub>&nbsp;&lt;&nbsp;400&nbsp;GeV kept, seeds at +2.5&nbsp;kHz. Background not modelled.</p>
  <figure>{img("cutflow.png", "Fraction kept by each L1 trigger level, of all SM HH to 4b events and of the events passing the offline 4b plus 3b selection")}
    <figcaption><b>For the total yield, L1 already keeps 93% of offline-selected events.</b> Light: all events. Dark: offline-selected.</figcaption></figure>
  <figure>{img("mhh_categories.png", "Generator m_HH of SM and kappa lambda 5 events, split by which trigger level keeps them, at trigger level and after offline selection")}
    <figcaption>Which trigger level keeps each event, for SM and &kappa;<sub>&lambda;</sub>&nbsp;=&nbsp;5.</figcaption></figure>
    </div>
  </details>
  <details class="more"><summary>Selection and caveats</summary>
    <p style="margin-top:8px">Offline: PUPPI jets p<sub>T</sub>&nbsp;&gt;&nbsp;30&nbsp;GeV, |&eta;|&nbsp;&lt;&nbsp;2.5; UParT medium (1% light mistag on QCD, 84% on b); four highest-b jets corrected for b-jet response (regression stand-in), paired, mass window 30&nbsp;GeV around (125,&nbsp;120); 4b = all medium, 3b = three medium + one loose. Rates from 2.0M minimum-bias events; thresholds tuned on even events, quoted on odd. Not included: HLT (can only lower the gain), real b regression. Equivalent luminosity: efficiency ratio (background gains equally) to its square (background unchanged).</p>
    <p><b>&kappa;<sub>&lambda;</sub> information.</b> Per m<sub>HH</sub> bin, the SM-sample yield is reweighted to &kappa;<sub>&lambda;</sub>&nbsp;=&nbsp;0, 1, 2.45 (Run-3 generator shapes, LHC HH WG cross section &sigma;(&kappa;<sub>&lambda;</sub>) &prop; 70.38 &minus; 51.85&kappa;<sub>&lambda;</sub> + 11.42&kappa;<sub>&lambda;</sub><sup>2</sup>), fitted with a quadratic, and differentiated at &kappa;<sub>&lambda;</sub>&nbsp;=&nbsp;1. The information share is (&part;s<sub>i</sub>/&part;&kappa;<sub>&lambda;</sub>)<sup>2</sup>/s<sub>i</sub>; each event is weighted by (&part;&nbsp;ln&nbsp;s<sub>i</sub>/&part;&kappa;<sub>&lambda;</sub>)<sup>2</sup>. This is the signal-dominated limit: QCD background also peaks at low m<sub>HH</sub>, which lowers the weight of those bins; tab 7 repeats the comparison as an m<sub>4j</sub>-shape fit with a minimum-bias background: there the pixel-vs-NN gain depends on the b content of the QCD the seeds add (from 17% narrower to none). Uncertainty on the &kappa;<sub>&lambda;</sub>-weighted pixel/NN ratio (bootstrap, offline-selected): 1.25 [1.18, 1.35]. HLT pixel tracks vs L1 tracks with pixel hits: on offline-selected events below 400&nbsp;GeV they agree within statistics (L1 ahead by 1.6&nbsp;&plusmn;&nbsp;2.1%; the larger gap in the &kappa;<sub>&lambda;</sub>-weighted column comes from a few heavily weighted events); at trigger level the L1 version is ahead by 2.9&nbsp;&plusmn;&nbsp;0.6%, as the 2&nbsp;GeV L1 track threshold keeps soft pileup tracks out of the minimum-bias rate (the same holds for HLT tracks cut at 2&nbsp;GeV). Lower-HT control: both menu HT cuts lowered until the added rate on even minimum-bias events reaches 2.5&nbsp;kHz (3.0&nbsp;kHz on odd ones, which favours the control).</p>
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
  <div class="col"><h3>Open questions</h3></div>
  <div class="tablewrap"><table>
    <tr><th>Question</th><th>Status</th></tr>
    <tr><td>L1 tracks (Outer Tracker) available at ~5 &micro;s</td><td><span class="pill base">Settled</span> in CMSSW / TDR</td></tr>
    <tr><td>Hits &rarr; displacement in the window (track extension, tab 3)</td><td><span class="pill good">Works in software</span> firmware cost unknown</td></tr>
    <tr><td>Pixel front-ends answer a regional request mid-latency</td><td><span class="pill warn">Needs insiders</span> baseline sends hits only after L1 accept; readout is destructive; the chip&#39;s two-level mode is not a regional fetch</td></tr>
    <tr><td>Request + readout + fit inside ~2.5&ndash;3 &micro;s</td><td><span class="pill warn">Needs insiders</span></td></tr>
  </table></div>
  <details class="more"><summary>Bit budget: ~4&ndash;10 Gb/s of extra data</summary>
    <div class="moregrid">
  <p class="note" style="margin:0">Per crossing after a loose L1 HT pre-selection, minimum bias at PU&nbsp;200.</p>
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

    <p style="margin-top:8px">CMSSW 17_0_0_pre2: L1 track word 96 b with a 13-b d0 (39&nbsp;&micro;m step, about our pixel resolution; <code>TTTrack_TrackWord.h</code>); PUPPI candidate 61 b with an 8-b dxy stored as &radic;|dxy|, unsigned (<code>l1ct::PuppiObj</code>, <code>datatypes.h</code>); Global Trigger jet 128 b (<code>gt_datatypes.h</code>). Cluster size: pixel-chip quarter-core encoding (<code>Phase2ITQCore</code>): 6 + 2 + 8 address bits, hit map, 4-b charge per pixel, about 30&ndash;40 b per cluster. Window clusters: narrow windows (0.8&nbsp;mm r-&phi; &times; 8&nbsp;mm), same purity and d0 as the default (87%, 36&nbsp;&micro;m). Track counts: L1 tracks above 2&nbsp;GeV in jets above 30&nbsp;GeV. No design document for a pixel-to-L1 path is in CMSSW; these are to be checked against one.</p>
  
    </div>
  </details>
  <details class="more"><summary>What CMSSW says about the pixel readout</summary>
    <div class="moregrid">
  <p class="note" style="margin:0">From the CMSSW 17_0_0_pre2 emulators and maps on 20 PU&nbsp;200 events.</p>
  <div class="tablewrap"><table>
    <tr><th>Finding</th><th>What it means</th></tr>
    <tr><td><b>Chip output is ~2.4&times;10<sup>7</sup> bits per crossing</b> for the whole pixel detector (emulated chip data stream, <code>Phase2ITQCoreProducer</code>): ~130 b per cluster, 18&nbsp;Tb/s at 750&nbsp;kHz</td><td>3.6&times; the 36 b per cluster assumed in the bit budget: hits back ~10 / 4 Gb/s, not 2.7 / 1.2</td></tr>
    <tr><td><b>A chip returns all its hits</b> for a crossing, not a window: median 1.1&nbsp;kbit, 1% of chips above ~8&nbsp;kbit</td><td>~1&ndash;6 &micro;s per crossing on one 1.28&nbsp;Gb/s e-link: comparable to the whole 2.5&ndash;3&nbsp;&micro;s window</td></tr>
    <tr><td>Module &rarr; lpGBT &rarr; back-end map exists (3,892 modules, 1,342 lpGBTs, 28 boards); <b>the e-link configuration and link capacity do not</b></td><td>Spare bandwidth per link cannot be settled from CMSSW: a question for the pixel DAQ experts</td></tr>
    <tr><td><b>Prompt L1 tracks carry d0 = 0</b> (13-b field always empty); the NN tagger runs on the extended chain, whose d0 comes from the Outer Tracker alone</td><td>A pixel-refit d0 fits in the existing 13-b field (39 &micro;m step &asymp; its resolution): correlator, tagger and Global Trigger formats unchanged</td></tr>
  </table></div>
    </div>
  </details>
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
    <figcaption>One 2.3&nbsp;GeV track in a b jet: <b>1</b> tracker, <b>2</b> L1 track into the pixels, <b>3</b> &plusmn;1.5&nbsp;mm windows, <b>4</b> refit d0&nbsp;=&nbsp;498&nbsp;&micro;m (HLT: 532).</figcaption></figure>
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
  <p class="note col">"+" rows: small BDT on the NN scores plus the pixel summary. b jets from HH&rarr;4b, light jets from QCD.</p>
  <div class="callout"><b>Better per-jet tags do not automatically mean a better seed.</b> Recalibrating the refit impact-parameter error (tab 6) lifts the per-jet tag to 54% / 83%, but the HH&rarr;4b seed at +2.5&nbsp;kHz keeps 75.7% of events instead of 77.8%: the longitudinal term makes pileup jets in minimum bias look displaced, and the seed rate is set by minimum-bias jets, not by the QCD light jets of the ROC. The transverse recalibration alone gives 78.6% (+0.8 points, at the statistical precision). The page keeps the original summary.</div>
  <figure>{img("jet_eff.png", "Per-jet b efficiency and light mistag against L1 jet pT and eta at a fixed 10 percent inclusive light mistag, for today's NN, HLT pixel tracks and L1 tracks with pixel hits")}
    <figcaption><b>Pixels tag soft jets.</b> At 10% light mistag the NN tags almost no b jet below 40&nbsp;GeV.</figcaption></figure>
  <details class="more"><summary>Why not a network on raw hits?</summary><p style="margin:0">Tried: a network on loose hits gave no gain up to the training sizes we had (22&ndash;45k jets); grouping hits into tracks is what recovers displacement. A jet cone holds ~660 pixel clusters at PU&nbsp;200 (1,400 at 90%), and FPGA graph networks exceed 4&nbsp;&micro;s above ~900 hits (arXiv:2112.02048). Seeding on L1 tracks avoids the pattern recognition.</p></details>
</section>

<!-- ============ TAB 4: rate ============ -->
<section class="panel" role="tabpanel" id="p-rate" aria-labelledby="t-rate" hidden>
  <div class="tiles">
    <div><span class="k">On top of the planned menu</span><span class="v">~0.3 vs 2.3 kHz</span><span class="s">for the same HH&rarr;4b efficiency (pixel vs NN seed)</span></div>
    <div><span class="k">Standalone seed</span><span class="v">2.7 vs 9.6 kHz</span><span class="s">same efficiency, ~3.5&times; less rate</span></div>
    <div><span class="k">For scale: the whole L1 menu</span><span class="v">346 of 750 kHz</span><span class="s">TDR menu at PU&nbsp;200 (450 with 30% margin); HT + quad-jet seeds: 20&nbsp;kHz</span></div>
  </div>
  <p class="note col" style="margin:0">Saving a few kHz is ~1% of the menu. The case for pixels is efficiency at fixed rate (tab 1), not bandwidth.</p>
  <figure>{img("seed_plane.png", "Seed plane of L1 HT against the sum of the four leading jets' b scores, with lines of equal minimum-bias rate at 2, 5, 10 and 20 kHz and the best HH to 4b efficiency on each, for today's NN and for L1 tracks with pixel hits")}
    <figcaption><b>Pixels pull HH&rarr;4b away from minimum bias.</b> Standalone: 49% vs 30% at 2&nbsp;kHz, 63% vs 47% at 10&nbsp;kHz.</figcaption></figure>
  <figure>{img("rate_curves.png", "HH to 4b efficiency for offline-selected events versus L1 rate for the NN, HLT-pixel and L1-pixel seeds")}
    <figcaption><b>Same signal, much less rate.</b> The lowest-rate points rest on few minimum-bias events.</figcaption></figure>
</section>

<!-- ============ TAB 5: code ============ -->
<section class="panel" role="tabpanel" id="p-code" aria-labelledby="t-code" hidden>
  <div class="col">
    <p style="margin:0">Everything is on the branch <code>andrzejnovak/FastPUPPI:17_0_X_pixelTracks</code>, in <code>NtupleProducer/test_pixels/</code>; paths below are relative to it. Start with <code>HANDOFF.md</code> there. The working copies on subMIT are in <code>/work/submit/novaka/l1pixels/</code> (<code>analysis/</code> mirrors <code>test_pixels/analysis/</code>; <code>offline/</code> is <code>test_pixels/analysis/offline/</code>). Scripts carry absolute <code>/work</code> and <code>/ceph</code> paths; anything longer than a minute runs on Slurm (<code>--partition=submit</code>), not on the login node.</p>
  </div>
  <pre><span class="c"># analysis (no CMSSW): pixi environment from analysis/pixi.toml (pinned numpy, awkward, uproot, sklearn, matplotlib)</span>
cd /work/submit/novaka/l1pixels/analysis &amp;&amp; pixi run python &lt;script&gt;.py  <span class="c"># also on tier3 (no x86-64-v3 needed)</span>
<span class="c"># CMSSW only for ntuple production and FWLite scans of RAW</span>
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /work/submit/novaka/l1pixels/ngv2/CMSSW_17_0_0_pre2/src &amp;&amp; cmsenv      <span class="c"># ntuple production</span></pre>

  <div class="col"><h3>Every number on this page, and where it comes from</h3></div>
  <div class="tablewrap"><table>
    <tr><th>Result</th><th>Script</th><th>Output</th></tr>
    <tr><td>Tab 1: L1 kept, all events vs offline-selected</td><td><code>analysis/direct_curves.py</code> (seeds at +2.5&nbsp;kHz, perfect tag) on <code>offline/offline_sel.py</code> flags</td><td><code>curves.json</code>, <code>curves_flags.npz</code>, <code>offline_flags2.npz</code></td></tr>
    <tr><td>Tab 1: equivalent luminosity, &kappa;<sub>&lambda;</sub> split, m<sub>HH</sub> categories</td><td><code>analysis/kl_direct.py</code> (<code>SEL=offline_flags2.npz:resolved_4b</code>), <code>kl_reweight.py</code></td><td><code>kl_direct2.json</code>, <code>klreweight/nano_mhh_kl*.npz</code></td></tr>
    <tr><td>Tab 1: efficiency vs m<sub>HH</sub>, &kappa;<sub>&lambda;</sub> information per bin, table</td><td><code>analysis/make_page_plots.py</code> (section 9) on <code>curves_flags.npz</code>, genmhh, <code>klreweight/</code>; lower-HT control: <code>analysis/ht_control.py</code> (<code>run_ht_control.sh</code>, tier3)</td><td><code>plots_page/mhh_eff.png</code>, <code>ht_control_flags.npz</code></td></tr>
    <tr><td>Tab 1: softer offline scenarios; &kappa;<sub>&lambda;</sub>-weighted efficiency vs rate</td><td><code>offline/offline_scenarios.py</code> (<code>run_scenarios.sh</code>, tier3), <code>analysis/scen_ana.py</code>, <code>make_page_plots.py</code> (section 13)</td><td><code>offline_scenarios.npz</code>, <code>scen_ana.json</code>, <code>plots_page/klw_vs_rate.png</code></td></tr>
    <tr><td>Tab 1: efficiency vs offline H<sub>T</sub> and offline b-tag sum</td><td><code>analysis/make_page_plots.py</code> (section 10) on the offline dumps (<code>.../l1pixels/offline/HH4b_*.npz</code>)</td><td><code>plots_page/offline_eff.png</code></td></tr>
    <tr><td>Tab 3: jet efficiency vs p<sub>T</sub>, &eta;; tab 4: seed plane</td><td><code>analysis/seed_plane.py</code> (<code>run_seed_plane.sh</code>, tier3; same training as <code>direct_curves.py</code>), <code>make_page_plots.py</code> (sections 11, 12)</td><td><code>seed_plane.npz</code>, <code>plots_page/seed_plane.png</code>, <code>jet_eff.png</code></td></tr>
    <tr><td>Tab 1: offline selection (UParT, b response, pairing)</td><td><code>offline/dump_offline.py</code> (MINIAOD), <code>offline_sel.py</code></td><td><code>offline/b_response.json</code>, <code>offline_flags2.npz</code></td></tr>
    <tr><td>Tab 7: &kappa;<sub>&lambda;</sub> fit with background, triggered and scouting streams</td><td><code>analysis/scouting.py</code> (<code>run_scouting.sh</code>, tier3), <code>qcd_tagfrac.py</code> (QCD 4b / 3b fractions), <code>plot_scouting.py</code></td><td><code>scouting.json</code>, <code>qcd_tagfrac.json</code>, <code>plots_page/kl_scan.png</code></td></tr>
    <tr><td>Tab 7: BSM truths; signal below the HT reach; tab 3: recalibrated summary in the seed</td><td><code>analysis/scouting.py</code> (<code>TRUTHS</code>), <code>hh_ht_reach.py</code>; <code>run_v2.sh</code>, <code>run_v2xy.sh</code> (<code>PIXSUM=v2|v2xy</code> in <code>train_sets.pixel_summary</code>)</td><td><code>hh_ht_reach.json</code>, <code>.../derived/analysis_v2/</code></td></tr>
    <tr><td>Tab 6: menu rates from stored 14_0 jets</td><td><code>analysis/rate_check.py</code> (<code>run_rate_check.sh</code>) on <code>.../l1pixels/mbjscan</code> (<code>production/mbsel/scan_jets.py</code>)</td><td><code>rate_check.json</code></td></tr>
    <tr><td>Tab 6: charm-oriented summary, recalibrated 3D impact parameter</td><td><code>analysis/charm_feats2.py</code> (resolution table, words), <code>ctag_charm.py</code> (<code>run_ctag_charm.sh</code>), <code>vbf_ctag_charm.py</code>, <code>btag_v2check.py</code></td><td><code>ctag_charm.json</code>, <code>ctag_charm_out/</code></td></tr>
    <tr><td>Tab 1: perfect-tag ceiling with flavour-aware rate</td><td><code>analysis/perfect_ceiling.py</code> (<code>run_perfect_ceiling.sh</code>; QCD P(n<sub>b</sub>&nbsp;|&nbsp;HT)), used by <code>make_page_plots.py</code> and <code>scen_ana.py</code> (<code>perfect_fix</code>)</td><td><code>perfect_ceiling.json</code>, <code>perfect_ceiling_flags.npz</code></td></tr>
    <tr><td>Tab 2: bit budget</td><td><code>analysis/bits_budget.py</code></td><td><code>bits_mb.json</code></td></tr>
    <tr><td>Tab 3: hit association, purity, d0 resolution</td><td><code>analysis/l1ext.py</code> (the extension and refit), <code>l1ext_validate.py</code></td><td><code>l1ext_val/scan_0.json</code></td></tr>
    <tr><td>Tab 3: tagging chain ROC</td><td><code>analysis/make_l1ext_lists.py</code> (<code>MODE=otonly</code> for OT-only), <code>make_lists.py</code> (HLT pixel tracks), <code>tag_compare.py</code></td><td><code>lists_l1ext_*.npz</code>, <code>tag_chain.json</code></td></tr>
    <tr><td>Tab 3: event display</td><td><code>analysis/event_display.py &lt;HH4b ntuple&gt; &lt;png&gt;</code></td><td><code>plots_page/event_display.png</code></td></tr>
    <tr><td>Tab 4: efficiency vs rate</td><td><code>analysis/direct_rate.py</code>, <code>direct_curves.py</code></td><td><code>direct_rate2.json</code>, <code>direct_rate_l1ext.json</code>, <code>curves.json</code></td></tr>
    <tr><td>Tab 6: charm tagging</td><td><code>analysis/ctag_compare.py</code></td><td><code>ctag_chain.json</code></td></tr>
    <tr><td>Tab 6: VBF menu efficiency</td><td><code>analysis/vbf_menu.py</code></td><td><code>vbf_menu.json</code></td></tr>
    <tr><td>Tab 6: VBF seed + flavour tags at fixed rate</td><td><code>analysis/vbf_ctag.py</code> (<code>run_vbf_ctag.sh</code>, <code>WHICH=cc|bb</code>); pixel lists of the VBF samples and VBF-like minimum bias: <code>make_l1ext_lists.py</code> via <code>run_l1ext_lists2.sh</code></td><td><code>vbf_ctag_cc.json</code>, <code>vbf_ctag_bb.json</code></td></tr>
    <tr><td>Tab 6: boosted ggH, menu vs Higgs p<sub>T</sub>; large-jet mass and seeds</td><td><code>analysis/fatjet_parts.py</code> (<code>run_fatjet_parts.sh</code>), <code>fatjet_ana.py</code>; R = 0.8 jet tables: <code>addSC8Jets()</code> in <code>../python/runPerformanceNTuple.py</code></td><td><code>derived/fatjet_parts/</code>, <code>fatjet_ana.json</code></td></tr>
    <tr><td>Tab 6: ZH(&nu;&nu;), menu vs generator MET</td><td><code>analysis/zh_met.py</code></td><td><code>zh_met.json</code></td></tr>
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
    <tr><td>VBF-like minimum bias (105,272 events: stored jets lead &gt; 30, sub &gt; 15, m<sub>jj</sub> &gt; 200); same events with R&nbsp;=&nbsp;0.8 jets</td><td><code>.../l1pixels/local_mbvbf/</code>; <code>.../local_mbnew_v2/</code>, <code>.../local_mbsel_v2/</code></td></tr>
    <tr><td>Private ggH + jet, ZH(&nu;&nu;) samples</td><td><code>.../l1pixels/privgen/</code></td></tr>
    <tr><td>Derived per-jet lists and large-jet tables (new outputs)</td><td><code>.../l1pixels/derived/</code></td></tr>
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
    <div><span class="k">L1 charm tag, c vs light at 10%</span><span class="v">16% &rarr; 29% &rarr; 34%</span><span class="s">today&#39;s NN &rarr; + L1 tracks with pixel hits &rarr; + recalibrated 3D impact parameter and a charm word</span></div>
    <div><span class="k">VBF H&rarr;cc kept by the planned menu</span><span class="v">57%</span><span class="s">of events in a generator VBF + cc acceptance (H&rarr;bb: 53%); a pixel-tagged VBF seed at +2&nbsp;kHz: 62% (H&rarr;bb: 51&nbsp;&rarr;&nbsp;61%)</span></div>
    <div><span class="k">Boosted ggH, Higgs p<sub>T</sub> &gt; 200&nbsp;GeV, kept by the planned menu</span><span class="v">98&ndash;100%</span><span class="s">SingleJet230 or HT450 already fire: L1 is not the bottleneck, the HLT is (ZH(&nu;&nu;) above 150&nbsp;GeV: 96&ndash;98%)</span></div>
  </div>
  <figure>{img("ctag_roc.png", "ROC curves for L1 charm tagging, c versus light and c versus b, for the L1 NN, Outer-Tracker-only displaced tracks, L1 tracks with pixel hits and HLT pixel tracks")}
    <figcaption><b>Pixels make L1 charm tagging possible:</b> 16% &rarr; 29% c efficiency at 10% light mistag.</figcaption></figure>
  <div class="tablewrap"><table>
    <tr><th>c efficiency (QCD jets)</th><th class="n">vs light 1%</th><th class="n">vs light 10%</th><th class="n">vs b 30%</th><th class="n">Bits</th></tr>
    <tr><td>Today&#39;s L1 NN</td><td class="n">5.1%</td><td class="n">15.6%</td><td class="n">40.7%</td><td class="n">&mdash;</td></tr>
    <tr><td>+ pixel summary (8 numbers)</td><td class="n">6.7%</td><td class="n">29.0%</td><td class="n">61.1%</td><td class="n">64</td></tr>
    <tr><td>+ charm word on the same inputs</td><td class="n">7.0%</td><td class="n">29.0%</td><td class="n">62.3%</td><td class="n">+61</td></tr>
    <tr class="hl"><td><b>Recalibrated 3D impact parameter + charm word</b></td><td class="n"><b>10.4%</b></td><td class="n"><b>33.5%</b></td><td class="n"><b>66.2%</b></td><td class="n">125</td></tr>
    <tr><td>Same, one combined word</td><td class="n">9.8%</td><td class="n">32.8%</td><td class="n">65.4%</td><td class="n">62</td></tr>
  </table></div>
  <p class="note col" style="margin:0"><b>The lever is the inputs, not more features.</b> The refit used a d0 error fitted to HLT pixel tracks (88&nbsp;&micro;m floor); minimum-bias negative-IP tails give 17&ndash;85&nbsp;&micro;m, and the refit z<sub>0</sub> adds a longitudinal significance. Charm word: track counts in significance bands, vertex and two-track mass, displaced p<sub>T</sub> fractions, decay length and its significance, vertex charge (<code>charm_feats2.py</code>, <code>ctag_charm.py</code>). Bootstrap &plusmn;0.5 points at 10% light. The VBF H&rarr;cc seed does not move (62% at +2&nbsp;kHz): only ~50 events separate the seeds there. Same recalibration lifts the b tag from 48/78% to 55/83% at 1%/10% light (not yet propagated to tabs 1&ndash;4, 7).</p>
  <div class="col"><h3>VBF H&rarr;cc and H&rarr;bb: the trigger is a real bottleneck</h3>
    <p class="note" style="margin:0">Acceptance: two Higgs-flavour jets (p<sub>T</sub>&nbsp;&gt;&nbsp;30, |&eta;|&nbsp;&lt;&nbsp;2.4) plus a VBF pair (m<sub>jj</sub>&nbsp;&gt;&nbsp;500, |&Delta;&eta;|&nbsp;&gt;&nbsp;3).</p></div>
  <div class="tablewrap"><table>
    <tr><th>Fraction of accepted events kept</th><th class="n">VBF H&rarr;cc</th><th class="n">VBF H&rarr;bb</th></tr>
    <tr><td>Acceptance (of all events)</td><td class="n">12.9%</td><td class="n">14.8%</td></tr>
    <tr class="hl"><td><b>Planned menu (any hadronic seed)</b></td><td class="n"><b>57%</b></td><td class="n"><b>53%</b></td></tr>
    <tr><td>VBF seed <code>DoublePuppiJet160_35_mass620</code></td><td class="n">39%</td><td class="n">36%</td></tr>
</table></div>
  <details class="more"><summary>Which planned seeds fire on VBF events</summary><div class="tablewrap"><table>
    <tr><th>Fraction of accepted events</th><th class="n">VBF H&rarr;cc</th><th class="n">VBF H&rarr;bb</th></tr>
    <tr><td>SingleJet230 / DoubleJet112 / HT seeds</td><td class="n">28 / 34 / 23%</td><td class="n">26 / 32 / 22%</td></tr>
    <tr><td>Only the VBF seed fires</td><td class="n">12%</td><td class="n">10%</td></tr>
    </table></div></details>
  <div class="col"><h3>A flavour-tagged VBF seed: what it adds at fixed rate</h3>
    <p class="note" style="margin:0">A looser VBF pair plus two tagged central jets, on top of the planned menu. Cuts chosen on even events, quoted on odd.</p></div>
  <figure>{img("vbf_tag_rate.png", "Fraction of VBF H to cc and H to bb events in the acceptance kept by the planned menu plus a looser VBF seed, against the added L1 rate; no tag, today's NN tag and the pixel tag")}
    <figcaption><b>Tags help, lower thresholds do not.</b> At +2&nbsp;kHz: H&rarr;cc 58&nbsp;&rarr;&nbsp;62%, H&rarr;bb 51&nbsp;&rarr;&nbsp;61%.</figcaption></figure>
  <div class="tablewrap"><table>
    <tr><th>Kept, of events in the acceptance (odd events)</th><th class="n">VBF H&rarr;cc</th><th class="n">VBF H&rarr;bb</th></tr>
    <tr><td>Planned menu</td><td class="n">58.0%</td><td class="n">51.4%</td></tr>
    <tr><td>+ looser VBF seed, no tag (+2.1&nbsp;kHz)</td><td class="n">59.3%</td><td class="n">52.5%</td></tr>
    <tr><td>+ VBF seed with two tagged jets, today&#39;s NN (~+2&nbsp;kHz)</td><td class="n">61.4%</td><td class="n">55.7%</td></tr>
    <tr class="hl"><td><b>+ VBF seed with two tagged jets, L1 tracks with pixel hits (~+2&nbsp;kHz)</b></td><td class="n"><b>62.1%</b></td><td class="n"><b>60.8%</b></td></tr>
    <tr><td>Same, ~+5&nbsp;kHz: NN / pixels</td><td class="n">63.3 / 64.1%</td><td class="n">57.9 / 64.6%</td></tr>
  </table></div>
  <p class="note col" style="margin:0">Our emulated seed rates vs the TDR menu table (PU&nbsp;200): HT seeds 19 vs 20&nbsp;kHz, double jet 95 vs 71, VBF 22 vs 40. The stored 14_0 emulator jets of all 2.0M minimum-bias events, with the same thresholds, give double jet 72 and VBF 15&nbsp;kHz (<code>rate_check.py</code>): the double-jet excess is the ~6% higher 17_0 jet response, and the VBF seed differs from the TDR one in both. Comparisons at fixed added rate are unaffected.</p>
  <div class="col"><h3>The Run-3 VBF H&rarr;cc trigger, as it is in CMSSW</h3>
    <p class="note" style="margin:0">In the 2024&ndash;25 GRun menu (<code>HLT_GRun_cff.py</code>, CMSSW_17_0_0_pre2):</p></div>
  <div class="tablewrap"><table>
    <tr><th>Stage</th><th>Requirement</th></tr>
    <tr><td>Paths</td><td><code>HLT_QuadPFJet100_88_70_30_PNet1CvsAll0p5_VBF3Tight</code>, <code>&hellip;105_88_75_30_PNet1CvsAll0p5_VBF3Tight</code>, <code>&hellip;111_90_80_30_PNet1CvsAll0p6_VBF3Tight</code></td></tr>
    <tr><td>L1 seed (OR)</td><td><code>L1_DoubleJet_110_35_DoubleJet35_Mass_Min800</code> (to <code>Min1200</code>): the Run-3 VBF seeds; <code>L1_TripleJet_95_75_65_DoubleJet_75_65_er2p5</code>, <code>_100_80_70_&hellip;</code>, <code>L1_QuadJet_95_75_65_20_DoubleJet_75_65_er2p5_Jet20_FWD3p0</code>; <code>L1_SingleJet180</code>/<code>200</code>; <code>L1_HTT280er</code>/<code>360er</code>. No flavour at L1.</td></tr>
    <tr><td>HLT jets</td><td>Four PF jets (loose ID) above 100 / 88 / 70 / 30&nbsp;GeV; two central (|&eta;|&nbsp;&lt;&nbsp;2.5, tight ID) above 30&nbsp;GeV</td></tr>
    <tr><td>HLT charm tag</td><td>At least one central jet with ParticleNet CvsAll &gt; 0.5 (0.6 in the tightest version)</td></tr>
    <tr><td>VBF topology</td><td><code>HLTPFJetSortedVBFFilter</code>, mode <code>2BTagAndPt</code> with the CvsAll score: of the four leading jets, the two with the highest CvsAll are the Higgs candidates, the other two the VBF pair; m<sub>qq</sub>&nbsp;&gt;&nbsp;460&nbsp;GeV, |&Delta;&eta;<sub>qq</sub>|&nbsp;&gt;&nbsp;3.5</td></tr>
  </table></div>
  <ul class="tight col">
    <li><b>Phase-2 has nothing like it yet:</b> no VBF or charm path in the Phase-2 HLT menu, and no flavour in the L1 VBF seed.</li>
    <li>Run 3 tags charm only at the HLT. At Phase-2, L1 already loses 43% of VBF H&rarr;cc events before any tag.</li>
  </ul>
  <div class="col"><h3>Boosted ggH and ZH(&nu;&nu;): the planned menu already keeps them</h3></div>
  <figure>{img("menu_vs_pt.png", "Fraction of events kept by the planned Phase-2 L1 menu: left, boosted ggH to cc and bb against Higgs pT, reaching 98 to 100 percent above 200 GeV; right, ZH with Z to neutrinos against generator MET, reaching 93 to 100 percent above 150 GeV")}
    <figcaption><b>L1 is not the limit here.</b> Boosted ggH above 200&nbsp;GeV and ZH(&nu;&nu;) above 150&nbsp;GeV MET: 96&ndash;100% kept.</figcaption></figure>
  <details class="more"><summary>Large-jet tools and private samples</summary>  <ul class="tight">
    <li>The large-jet tools are in place should the 100&ndash;200&nbsp;GeV region matter: L1 R&nbsp;=&nbsp;0.8 seeded-cone jets with a mass from their PUPPI constituents (the L1 jet mass is not filled; merged H&rarr;cc jets peak at ~125&nbsp;GeV above a Higgs p<sub>T</sub> of 250&nbsp;GeV, minimum-bias jets at ~23&nbsp;GeV) and the two-prong score (median 0.99 for merged H&rarr;cc, 0.94 for minimum bias).</li>
    <li>Private samples (no Phase-2 ggH&rarr;bb/cc exists): Pythia8 H + jet with top-mass dependence, p&#770;<sub>T</sub>&nbsp;&gt;&nbsp;150&nbsp;GeV, and ZH with Z&rarr;&nu;&nu;, through the official Spring24 GEN-SIM &rarr; PU&nbsp;200 DIGI/L1/HLT recipe.</li>
  </ul></details>
</section>

<!-- ============ TAB 7: kappa_lambda fit with background, scouting as a fallback ============ -->
<section class="panel" role="tabpanel" id="p-kl" aria-labelledby="t-kl" hidden>
  <div class="tiles">
    <div><span class="k">Pixel tags only in scouting (fallback)</span><span class="v">recovers nothing</span><span class="s">menu 1.61&nbsp;&rarr;&nbsp;1.61&sigma;; NN seed 1.99&nbsp;&rarr;&nbsp;1.99&sigma;, in every background model</span></div>
    <div><span class="k">Real-time pixel seed vs NN seed, &kappa;<sub>&lambda;</sub></span><span class="v">model-dependent</span><span class="s">from 17% narrower to no gain: depends on how b-rich the QCD it adds is</span></div>
    <div><span class="k">Signal below L1 HT 150</span><span class="v">1.8% (SM), 5.6% (&kappa;<sub>&lambda;</sub>&nbsp;=&nbsp;5)</span><span class="s">four 20&nbsp;GeV jets in the Higgs window already imply HT&nbsp;&gt;&nbsp;~150: scouting cannot go lower in mass</span></div>
  </div>
  <figure>{img("kl_scan.png", "Left: Asimov minus two delta log likelihood against kappa lambda for the planned menu, the NN seed, the pixel seed, the menu plus pixel tags in scouting, and scouting alone. Right: the 68 and 95 percent intervals")}
    <figcaption><b>Pixel tags used only in scouting add nothing:</b> the fallback curve lies on the menu&#39;s. Conservative background model (below).</figcaption></figure>
  <div class="col"><h3>Why the fallback fails</h3>
  <ul class="tight">
    <li><b>Scouted events never get offline reconstruction.</b> They must be selected with L1 jets and L1 tags (at best ~60% per b jet at 5% light mistag; offline 84% at 1%), among every crossing with HT&nbsp;&gt;&nbsp;150. Scouting alone: Z&nbsp;=&nbsp;0.14.</li>
    <li><b>The value of the real-time seed is the readout it triggers,</b> not the tag itself: accepted events get full tracking and offline tags.</li>
    <li><b>It saves less than it seems.</b> Scouting still needs the pixel hits of every scouted crossing, read regionally on request (~370&nbsp;kHz at HT&nbsp;&gt;&nbsp;140) before the front-end buffers expire: only the track extension and tagger leave the latency budget.</li>
    <li><b>Lower mass is not reachable either</b> (third tile): the low-m<sub>HH</sub> reach is set by jet thresholds and acceptance.</li>
  </ul></div>
  <div class="tablewrap"><table>
    <tr><th>Stream (3000&nbsp;fb<sup>&minus;1</sup>, SM truth)</th><th class="n">Z<sub>SM</sub> A</th><th class="n">Z<sub>SM</sub> B</th><th class="n">&kappa;<sub>&lambda;</sub> 68%, B</th><th class="n">SM excluded if &kappa;<sub>&lambda;</sub>&nbsp;=&nbsp;5, A / B</th></tr>
    <tr><td><b>Planned menu</b> <span class="muted">(no L1 b tag)</span></td><td class="n">1.59</td><td class="n">1.61</td><td class="n">[0.25, 2.30]*</td><td class="n">0.8 / 0.8&sigma;</td></tr>
    <tr><td>Menu + pixel tags in scouting <span class="muted">(fallback)</span></td><td class="n">1.60</td><td class="n">1.61</td><td class="n">[0.25, 2.30]*</td><td class="n">0.8 / 0.8&sigma;</td></tr>
    <tr><td><b>+ NN seed</b> <span class="muted">(real time, +2.4&nbsp;kHz)</span></td><td class="n">1.90</td><td class="n">1.99</td><td class="n">[0.48, 1.80]</td><td class="n">2.0 / 2.3&sigma;</td></tr>
    <tr><td>NN seed + pixel tags in scouting <span class="muted">(fallback)</span></td><td class="n">1.91</td><td class="n">1.99</td><td class="n">[0.48, 1.80]</td><td class="n">2.0 / 2.3&sigma;</td></tr>
    <tr class="hl"><td><b>+ pixel seed</b> <span class="muted">(real time, +2.2&nbsp;kHz)</span></td><td class="n"><b>2.01</b></td><td class="n"><b>1.62</b></td><td class="n">[0.25, 2.28]*</td><td class="n"><b>3.7 / 1.0&sigma;</b></td></tr>
    <tr><td>Scouting alone, L1 pixel tags</td><td class="n">0.26</td><td class="n">0.14</td><td class="n">[&minus;3.3, 8.3]</td><td class="n">0.3 / 0.2&sigma;</td></tr>
  </table></div>
  <p class="note col" style="margin:0">* plus a second 68% region near &kappa;<sub>&lambda;</sub>&nbsp;&asymp;&nbsp;5. <b>A:</b> one QCD 4b/3b tag fraction for every stream (optimistic for b-tagged seeds). <b>B:</b> each L1 class (menu-accepted, added by the seed, not accepted) its own QCD fraction and its own analysis category. The pixel seed adds b-rich QCD: in QCD its added events have a 4-tag fraction 40&times; the menu&#39;s (4.9&times;10<sup>&minus;4</sup>, from only 27 events), which removes their value in B. The NN-added fraction (9&times;10<sup>&minus;6</sup>, 49 events) is low even though 10 of those events hold &ge;&nbsp;2 true b jets: with these statistics the A/B spread is the uncertainty.</p>
  <div class="callout warn"><b>The minimum bias carries no flavour truth.</b> 99.5% of its L1 jets have no generator-jet match (the pileup interactions have no generator record), so its background flavour content cannot be measured directly, and a seed on generator flavour pays almost no minimum-bias rate. Tab 1&#39;s perfect-tag ceiling now uses a QCD-based flavour-aware rate (82.2% instead of 92.6% of all events); this tab leaves the perfect seed out, since its background has the same problem. Resolving model A vs B needs a QCD sample with many events at L1 HT&nbsp;150&ndash;400 (or a b-enriched one) and the analysis background model of the HH&rarr;4b group.</div>
  <details class="more"><summary>Method and caveats</summary>
    <p style="margin-top:8px"><b>Analysis at L1-object level</b> (<code>analysis/scouting.py</code>). Four leading L1 jets (p<sub>T</sub>&nbsp;&gt;&nbsp;20, |&eta;|&nbsp;&lt;&nbsp;2.4) paired by smallest |m<sub>1</sub>&nbsp;&minus;&nbsp;m<sub>2</sub>|, window radius 1.6&sigma; around (124,&nbsp;114)&nbsp;GeV, m<sub>4j</sub> as the m<sub>HH</sub> proxy; categories 4 and exactly 3 tags. All streams require L1 HT&nbsp;&gt;&nbsp;150&nbsp;GeV, where the re-simulated minimum bias is complete and where the pixel region-of-interest request would fire. Triggered stream: L1 accept, then offline-like tags (b 0.84, c 0.12, light 0.01 per jet, as UParT medium). Scouting stream: L1 tag scores only.</p>
    <p><b>Background.</b> Shape and normalisation from the minimum bias itself (each of 120,731 re-simulated events stands for 6.2&times;10<sup>8</sup> crossings at 3000&nbsp;fb<sup>&minus;1</sup>); 4b / 3b fractions from QCD events passing the same L1 seeds: offline jets truth-tagged (closure on QCD: P(3) predicted 1.3&times;10<sup>&minus;3</sup>, measured 1.2&times;10<sup>&minus;3</sup>, <code>qcd_tagfrac.py</code>) for the triggered streams, the minimum-bias L1 tag maps on QCD flavour for scouting. Bins merged until each holds &ge;&nbsp;10 minimum-bias events.</p>
    <p><b>&kappa;<sub>&lambda;</sub>.</b> Per bin, the SM yield reweighted with the Run-3 generator m<sub>HH</sub> shapes (&kappa;<sub>&lambda;</sub>&nbsp;=&nbsp;0, 1, 2.45, 5) and &sigma;(&kappa;<sub>&lambda;</sub>) = 70.39 &minus; 50.41&kappa;<sub>&lambda;</sub> + 11.06&kappa;<sub>&lambda;</sub><sup>2</sup> (13&nbsp;TeV, LHC HH WG), a quadratic per bin; Asimov Poisson likelihood. Truths &kappa;<sub>&lambda;</sub>&nbsp;=&nbsp;1, 2.45, 5. <b>Not included:</b> systematic uncertainties, offline jet resolution and b regression, VBF HH, non-QCD backgrounds, a 4-offline-jet requirement on the signal. Signal from odd events, where the taggers and seed thresholds were not tuned. Signal below L1 HT&nbsp;150: <code>hh_ht_reach.py</code>.</p>
  </details>
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

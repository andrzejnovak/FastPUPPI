#!/usr/bin/env python3
"""Render the pixel information-budget page.

    python3 make_budget_report.py BUDGETDIR OUT.html "sample description"

Reads BUDGETDIR/budget.json (train_sets.py) and BUDGETDIR/clusters.json (cluster occupancy).
"""
import json
import os
import sys

bdir, outname, sample_note = sys.argv[1], sys.argv[2], sys.argv[3]
B = json.load(open(os.path.join(bdir, "budget.json")))
C = json.load(open(os.path.join(bdir, "clusters.json")))
M, R = B["meta"], B["results"]
by = {r["name"]: r for r in R}
ng = by["NN tagger only"]
summ = by["NN + jet summary (BDT)"]
BX = 40e6  # bunch crossings per second (40 MHz)


def pct(x):
    return f"{100 * x:.0f}%"


def rate(bits_per_bx):
    v = bits_per_bx * BX
    for unit, f in (("Tb/s", 1e12), ("Gb/s", 1e9), ("Mb/s", 1e6)):
        if v >= f:
            return f"{v / f:,.1f} {unit}" if v / f < 100 else f"{v / f:,.0f} {unit}"
    return f"{v:,.0f} b/s"


def bits(n):
    return f"{n:,.0f}"


kinds = {"ng": "NN tagger only", "summary": "NN + jet summary", "trk": "NN + top-k pixel tracks",
         "trkhit": "NN + top-k tracks + their hits", "hit": "NN + hits of top-k tracks (no track fit)",
         "trkhit_nonn": "pixel only, no NN (16 tracks + hits)"}
rows = ""
for r in R:
    best = r["name"] == summ["name"]
    b = "<b>" if best else ""
    e = "</b>" if best else ""
    cls = ' class="hl"' if best else ""
    rows += (f"<tr{cls}><td>{b}{r['name']}{e}</td><td class='n'>{bits(r['bits_per_jet'])}</td>"
             f"<td class='n'>{r['auc']:.3f}</td><td class='n'>{pct(r['beff_1pct'])}</td><td class='n'>{pct(r['beff_10pct'])}</td></tr>\n")

ntrk = C["pixel_tracks_per_event"]
ncl = C["clusters_per_event"]
vol = [
    ("Per-jet summary, 4 leading jets", 4 * M["bits_summary"], "64 b × 4 jets"),
    ("Per-jet summary, all 16 tagged jets", 16 * M["bits_summary"], "64 b × 16 jets"),
    ("Top-8 tracks per jet, 4 leading jets", 4 * 8 * M["bits_track"], "8 × 64 b × 4 jets"),
    ("Today's NN inputs, 16 jets (reference)", 16 * M["bits_puppi_jet"], "16 PUPPI × 64 b × 16 jets"),
    ("Every HLT pixel track in the event", ntrk * M["bits_track"], f"{ntrk:,.0f} tracks × 64 b"),
    ("Every pixel cluster in the event", ncl * M["bits_hit"], f"{ncl:,.0f} clusters × 40 b"),
]
volrows = "".join(f"<tr><td>{a}</td><td class='mono'>{c}</td><td class='n'>{bits(b)}</td><td class='n'>{rate(b)}</td></tr>\n" for a, b, c in vol)

html = f"""<title>L1 Pixel Information Budget</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Layout: one reading column (~74ch) with full-width figures and tables; answer first, method last. */
:root {{
  --bg: #f5f7f6; --surface: #ffffff; --ink: #16211d; --muted: #586660; --rule: #d6dedb;
  --accent: #1f6f5c; --accent-soft: #e1efea; --warn: #9a5b00; --hl: #f0f7f3;
  --display: "Archivo", "Helvetica Neue", Arial, sans-serif;
  --body: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
  --mono: "JetBrains Mono", ui-monospace, Menlo, monospace;
  --plot-bg: #ffffff;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #101614; --surface: #17201d; --ink: #e2ebe7; --muted: #98a8a1; --rule: #2a3631;
  --accent: #6fd0b4; --accent-soft: #163029; --warn: #f0b05a; --hl: #1a2b25; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #101614; --surface: #17201d; --ink: #e2ebe7; --muted: #98a8a1; --rule: #2a3631;
  --accent: #6fd0b4; --accent-soft: #163029; --warn: #f0b05a; --hl: #1a2b25; color-scheme: dark }}
* {{ box-sizing: border-box }}
body {{ background: var(--bg); color: var(--ink); font: 400 17px/1.55 var(--body) }}
.wrap {{ max-width: 1080px; margin: 0 auto; padding-inline: 20px; padding-block: 40px 80px; display: grid; gap: 44px }}
.col {{ max-width: 74ch }}
h1 {{ font: 800 clamp(30px, 5vw, 46px)/1.05 var(--display); letter-spacing: -0.01em; margin: 0; text-wrap: balance }}
h2 {{ font: 700 25px/1.2 var(--display); margin: 0 0 12px; text-wrap: balance }}
p {{ margin: 0 0 12px }}
.eyebrow {{ font: 600 12px/1 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--accent); margin-bottom: 10px }}
.lede {{ font-size: 19px }}
.muted {{ color: var(--muted) }}
code, .mono {{ font-family: var(--mono); font-size: .85em }}
code {{ background: var(--accent-soft); padding: 1px 5px; border-radius: 4px; overflow-wrap: anywhere }}
a {{ color: var(--accent) }}
a:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px }}
section {{ display: grid; gap: 10px; min-width: 0 }}
.answer {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1px; background: var(--rule); border: 1px solid var(--rule); border-radius: 8px; overflow: hidden }}
.answer > div {{ background: var(--surface); padding: 16px 18px; display: grid; gap: 6px; align-content: start; min-width: 0 }}
.answer .k {{ font: 600 11px/1.2 var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted) }}
.answer .v {{ font: 700 24px/1.15 var(--display); font-variant-numeric: tabular-nums }}
.answer .s {{ font-size: 14.5px; color: var(--muted) }}
.tablewrap {{ overflow-x: auto; border: 1px solid var(--rule); border-radius: 8px; background: var(--surface) }}
table {{ border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; font-size: 15px }}
th, td {{ text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--rule); vertical-align: top }}
th {{ font: 600 11.5px/1.3 var(--mono); letter-spacing: .05em; text-transform: uppercase; color: var(--muted) }}
td.n, th.n {{ text-align: right; white-space: nowrap }}
tr:last-child td {{ border-bottom: 0 }}
tr.hl td {{ background: var(--hl) }}
figure {{ margin: 0; display: grid; gap: 8px; min-width: 0 }}
figure img {{ background: var(--plot-bg); border: 1px solid var(--rule); border-radius: 6px; width: 100%; height: auto; padding: 6px }}
figcaption {{ font-size: 15px; color: var(--muted); max-width: 80ch }}
ul.tight {{ margin: 0; padding-left: 20px; display: grid; gap: 7px }}
.callout {{ border-left: 3px solid var(--accent); background: var(--surface); padding: 14px 18px; border-radius: 0 8px 8px 0 }}
.callout.warn {{ border-left-color: var(--warn) }}
.foot {{ font-size: 14px; color: var(--muted); border-top: 1px solid var(--rule); padding-top: 16px }}
</style>

<div class="wrap">

<header class="col">
  <div class="eyebrow">Phase-2 L1 · pixel tracks for b-tagging</div>
  <h1>L1 Pixel Information Budget</h1>
  <p class="lede" style="margin-top:14px">Adding pixel information to the L1 jet tagger raises the b-tag efficiency a lot. But at L1 every bit sent upstream costs bandwidth. This page answers two questions: how many extra bits per jet are needed to get the gain, and do the pixel hits themselves add anything beyond the fitted pixel tracks.</p>
</header>

<section>
  <div class="answer">
    <div><span class="k">Cheapest thing that works</span><span class="v">64 bits / jet</span><span class="s">8 impact-parameter features of the pixel tracks in the jet: b-eff at 10% light mistag {pct(ng['beff_10pct'])} &rarr; {pct(summ['beff_10pct'])}</span></div>
    <div><span class="k">Sending more tracks</span><span class="v">no clear gain</span><span class="s">1 to 16 tracks per jet (64&ndash;1024 bits) land at or below the 64-bit summary on this sample</span></div>
    <div><span class="k">Hits on top of tracks</span><span class="v">no measurable gain</span><span class="s">hits without the track fit do not help at all</span></div>
    <div><span class="k">Raw clusters</span><span class="v">~{C['cone_all_median']:,.0f} per jet</span><span class="s">only {pct(C['frac_on_track'])} of all pixel clusters are on a pixel track; not a realistic input</span></div>
  </div>
</section>

<section>
  <div class="col">
    <div class="eyebrow">The measurement</div>
    <h2>b-tag performance versus extra bits per jet</h2>
    <p>Each point is a classifier that sees the current L1 NN tagger's class scores plus one block of pixel information. Bits per jet count only the extra pixel information, using the word sizes below. The dotted line marks what the NN tagger already receives per jet today.</p>
  </div>
  <figure><img src="budget.png" alt="b-jet efficiency at 10% and 1% light mistag versus extra bits per jet for each information block">
    <figcaption>Left: b-jet efficiency at 10% light-jet mistag. Right: at 1%. Numbers next to points are k, the number of pixel tracks per jet. {sample_note}</figcaption></figure>
  <div class="tablewrap"><table>
    <tr><th>Input to the tagger</th><th class="n">Extra bits / jet</th><th class="n">AUC</th><th class="n">b-eff @ 1% light</th><th class="n">b-eff @ 10% light</th></tr>
    {rows}
  </table></div>
</section>

<section>
  <div class="col">
    <div class="eyebrow">Data volume</div>
    <h2>What each option would cost at 40 MHz</h2>
    <p>Per bunch crossing, using the same word sizes, the pixel occupancy measured in PU 200 events ({C['clusters_per_event']:,.0f} pixel clusters and {ntrk:,.0f} HLT pixel tracks per event), and 40&nbsp;MHz.</p>
  </div>
  <div class="tablewrap"><table>
    <tr><th>Option</th><th>Count</th><th class="n">Bits / crossing</th><th class="n">At 40 MHz</th></tr>
    {volrows}
  </table></div>
  <p class="col muted">Per-jet options assume the jet directions are known where the pixel information is reduced, so only jet-level results travel. Shipping all tracks or all clusters off the detector is several orders of magnitude more.</p>
</section>

<section class="col">
  <div class="eyebrow">Hits</div>
  <h2>Can the hits be used directly?</h2>
  <ul class="tight">
    <li><b>Hits on pixel tracks</b> carry the same information as the track fit. Adding the 4 hits of each track (layer, position relative to the jet axis, cluster size and charge) does not improve on the tracks alone.</li>
    <li><b>Hits without the track fit</b> do not help at all with a small set-based network: AUC {by['NN + hits of 8 tracks (no fit)']['auc']:.2f} against {ng['auc']:.2f} for the NN alone. The b-tag information is an impact parameter of tens of &micro;m, which the network would have to reconstruct from centimetre-scale hit coordinates.</li>
    <li><b>Untracked clusters</b>: a PU 200 event has {C['clusters_per_event']:,.0f} pixel clusters ({C['barrel_per_event']:,.0f} barrel, {C['endcap_per_event']:,.0f} endcap). Within &Delta;R&lt;0.4 of an L1 jet (p<sub>T</sub>&gt;30&nbsp;GeV) there are {C['cone_all_median']:,.0f} (median; 90%: {C['cone_all_p90']:,.0f}), of which {C['cone_on_median']:,.0f} are on pixel tracks. These were stored and counted, not used in training.</li>
  </ul>
  <div class="callout" style="margin-top:8px"><b>Implication.</b> The useful output of the pixel detector for L1 b-tagging is the result of a track fit, and most of it compresses to a handful of numbers per jet. Whatever produces pixel tracks at 40&nbsp;MHz could compute the per-jet impact-parameter summary next to it and send ~64 bits per jet, about 6% on top of what the tagger already receives.</div>
</section>

<section class="col">
  <div class="eyebrow">How it was done</div>
  <h2>Method and assumptions</h2>
  <ul class="tight">
    <li><b>Samples</b>: Phase2Spring24 PU 200, HH&rarr;4b for b jets and QCD (flat p<sub>T</sub>) for light jets. {sample_note} b jets: {M['n_b']:,}, light jets: {M['n_light']:,}.</li>
    <li><b>Jets</b>: L1 SC4NG jets, 30&lt;p<sub>T</sub>&lt;300&nbsp;GeV, |&eta;|&lt;2.4, labelled by the hadron flavour of the gen jet within &Delta;R&lt;0.3. Light jets are reweighted to the b-jet (p<sub>T</sub>, |&eta;|) spectrum.</li>
    <li><b>Baseline</b>: L1 NN tagger model <code>L1TSC4NGJetModel_v2_0_0</code> (backported to our <code>L1PF_17_0_X</code> area); b/(b+uds+g).</li>
    <li><b>Pixel tracks</b>: HLT pixel tracks with p<sub>T</sub>&gt;1&nbsp;GeV within &Delta;R&lt;0.4, |&Delta;z|&lt;2&nbsp;mm to the leading pixel vertex (capped-p<sub>T</sub> &Sigma;p<sub>T</sub><sup>2</sup>), ordered by signed transverse-IP significance. Median {M['median_ntrk']:.0f} tracks per jet (90%: {M['ntrk_quantiles'][1]:.0f}).</li>
    <li><b>Jet summary</b> (64 bits = 8 numbers &times; 8 bits): from the vertex-compatible pixel tracks in the cone, with impact parameters signed by the jet direction: (1&ndash;3) the highest, 2nd and 3rd highest IP significance, (4) number of tracks, (5) number with significance &gt;3, (6) number with significance &gt;5, (7) sum of positive significances, (8) largest signed IP in cm. This is classic track-counting b-tagging. It is combined with the 8 NN class scores and the jet's log p<sub>T</sub> and &eta; in a gradient-boosted classifier.</li>
    <li><b>Track and hit sets</b>: DeepSets models (per-track and per-hit MLPs, masked mean and max pooling, NN scores concatenated). Trained on even events and tested on odd, then swapped, so every jet has an out-of-sample score.</li>
    <li><b>Word sizes</b> (assumed, easy to change in <code>train_sets.py</code>): pixel track {M['bits_track']} bits (p<sub>T</sub>, &eta;, &phi;, z<sub>0</sub>, d<sub>0</sub>, d<sub>0</sub> uncertainty, quality); pixel hit {M['bits_hit']} bits (layer, &phi;, z, cluster sizes, charge); summary {M['bits_summary']} bits (8 &times; 8); today's NN input {M['bits_puppi_jet']} bits per jet (16 PUPPI candidates &times; 64).</li>
  </ul>
</section>

<section class="col">
  <div class="eyebrow">Read with care</div>
  <h2>Caveats</h2>
  <ul class="tight">
    <li><b>Sample size.</b> The track-set models are data-limited. The 16-track model sees strictly more than the summary, which is computed from the same tracks, yet does no better: with about {M['n_b']//2:,} b and {M['n_light']//2:,} light jets per training half (20% of it held out for early stopping), a set network learning from raw track lists has not learned to use what it is given, while the summary hands a BDT the physics directly. The 1%-mistag column is also noisy. A ~10&times; larger sample is in production; a learning curve will show whether the set models catch up.</li>
    <li><b>HLT pixel tracks.</b> These are the tracks reconstructed by the Phase-2 HLT. The study assumes something equivalent exists at 40&nbsp;MHz. Whether that is feasible is the hardware question this result is meant to inform.</li>
    <li><b>Word sizes are assumptions</b>, not a firmware design; the quantisation of each feature has not been studied.</li>
    <li><b>No retraining of the NN tagger</b>: pixel information is added in a second-stage classifier, not inside the L1 NN. Training them together could do better with the same bits.</li>
  </ul>
</section>

<p class="foot">Code: <code>andrzejnovak/FastPUPPI:17_0_X_pixelTracks</code> (<code>NtupleProducer/test_pixels/analysis/make_lists.py</code>, <code>train_sets.py</code>). Main project page: <a href="https://claude.ai/artifact/9q5PSiwbxrxW7XKmDVXA7v">L1 Pixel b-Tagging</a>. Plots are private work.</p>
</div>
"""
open(outname, "w").write(html)
print("wrote", outname)

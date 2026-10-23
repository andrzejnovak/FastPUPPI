#!/usr/bin/env python3
"""Render the status/results page from summary.json + plots.

    python3 make_report.py PLOTDIR OUT.html
"""
import json
import os
import sys

plotdir, outname = sys.argv[1], sys.argv[2]
njobs = sys.argv[3] if len(sys.argv) > 3 else ""
banner = open(sys.argv[4]).read() if len(sys.argv) > 4 else ""
S = json.load(open(os.path.join(plotdir, "summary.json")))
R = S["roc"]
NG = R["L1 NN tagger (b/(b+uds+g))"]
PIX = R["Pixel tracks only (BDT)"]
COMB = R["L1 NN scores + pixel tracks (BDT)"]
TC2 = R["Pixel tracks only (2nd IP sig.)"]
NGBDT = R["L1 NN scores, BDT (same inputs, reference)"]
H = S["hh4b"]
W = S["within_hh4b"]
i1 = H["L1 NN tagger"]["mistag"].index(0.01)
i5 = H["L1 NN tagger"]["mistag"].index(0.05)


def pct(x):
    return f"{100 * x:.0f}%"


def ratio(a, b):
    return f"×{a / b:.1f}" if b > 0 else "n/a"


ptrows = ""
for rng, res in S["roc_ptbins"].items():
    lo, hi = rng.split("-")
    ptrows += (f"<tr><td>{lo}–{hi} GeV</td><td>{res['L1 NN tagger']['n_b']} / {res['L1 NN tagger']['n_l']}</td>"
               f"<td>{pct(res['L1 NN tagger']['beff_at_10pct'])}</td><td>{pct(res['pixel only (BDT)']['beff_at_10pct'])}</td>"
               f"<td><b>{pct(res['L1 NN + pixel (BDT)']['beff_at_10pct'])}</b></td></tr>\n")

html = f"""<title>L1 Pixel b-Tagging</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Layout: single reading column (~72ch) with full-width figure rows; a status ledger up top. */
:root {{
  --bg: #f6f7f9; --surface: #ffffff; --ink: #172030; --muted: #5a6577; --rule: #d9dee6;
  --accent: #0b6e8a; --accent-soft: #e2f0f4; --good: #1d7a46; --warn: #a15c00; --bad: #b3261e;
  --display: "Archivo", "Helvetica Neue", Arial, sans-serif;
  --body: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
  --mono: "JetBrains Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
  --plot-bg: #ffffff;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #11161e; --surface: #18202b; --ink: #e4e9f0; --muted: #9aa6b6; --rule: #2b3544;
  --accent: #5cc3dd; --accent-soft: #15303a; --good: #5fcf8e; --warn: #f0a94a; --bad: #ff8a80; --plot-bg: #ffffff; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #11161e; --surface: #18202b; --ink: #e4e9f0; --muted: #9aa6b6; --rule: #2b3544;
  --accent: #5cc3dd; --accent-soft: #15303a; --good: #5fcf8e; --warn: #f0a94a; --bad: #ff8a80; --plot-bg: #ffffff; color-scheme: dark }}
* {{ box-sizing: border-box }}
body {{ background: var(--bg); color: var(--ink); font: 400 17px/1.55 var(--body); }}
.wrap {{ max-width: 1080px; margin: 0 auto; padding-inline: 20px; padding-block: 40px 80px; display: grid; gap: 44px }}
.col {{ max-width: 74ch }}
h1 {{ font: 800 clamp(30px, 5vw, 46px)/1.05 var(--display); letter-spacing: -0.01em; margin: 0; text-wrap: balance }}
h2 {{ font: 700 25px/1.2 var(--display); margin: 0 0 12px; text-wrap: balance }}
h3 {{ font: 700 18px/1.3 var(--display); margin: 22px 0 6px }}
p {{ margin: 0 0 12px }}
.eyebrow {{ font: 600 12px/1 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--accent); margin-bottom: 10px }}
.lede {{ font-size: 19px; color: var(--ink) }}
.muted {{ color: var(--muted) }}
code, .mono {{ font-family: var(--mono); font-size: .86em }}
code {{ background: var(--accent-soft); padding: 1px 5px; border-radius: 4px; overflow-wrap: anywhere }}
a {{ color: var(--accent) }}
a:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px }}
section {{ display: grid; gap: 8px; min-width: 0 }}
.ledger {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 1px; background: var(--rule); border: 1px solid var(--rule); border-radius: 8px; overflow: hidden }}
.ledger > div {{ background: var(--surface); padding: 14px 16px; display: grid; gap: 4px; align-content: start; min-width: 0 }}
.ledger .k {{ font: 600 11px/1.2 var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted) }}
.ledger .v {{ font: 700 22px/1.2 var(--display); font-variant-numeric: tabular-nums }}
.ledger .s {{ font-size: 14px; color: var(--muted) }}
.pill {{ display: inline-block; font: 600 11px/1 var(--mono); letter-spacing: .06em; text-transform: uppercase; padding: 4px 7px; border-radius: 999px; border: 1px solid currentColor; vertical-align: 2px }}
.ok {{ color: var(--good) }} .wip {{ color: var(--warn) }} .no {{ color: var(--bad) }}
.tablewrap {{ overflow-x: auto; border: 1px solid var(--rule); border-radius: 8px; background: var(--surface) }}
table {{ border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; font-size: 15px }}
th, td {{ text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--rule); vertical-align: top }}
th {{ font: 600 12px/1.3 var(--mono); letter-spacing: .05em; text-transform: uppercase; color: var(--muted) }}
tr:last-child td {{ border-bottom: 0 }}
ol.bugs {{ margin: 0; padding-left: 22px; display: grid; gap: 10px }}
figure {{ margin: 0; display: grid; gap: 8px; min-width: 0 }}
figure img {{ background: var(--plot-bg); border: 1px solid var(--rule); border-radius: 6px; width: 100%; height: auto; padding: 6px }}
figcaption {{ font-size: 15px; color: var(--muted); max-width: 80ch }}
.figrow {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; align-items: start }}
.callout {{ border-left: 3px solid var(--accent); background: var(--surface); padding: 14px 18px; border-radius: 0 8px 8px 0 }}
ul.tight {{ margin: 0; padding-left: 20px; display: grid; gap: 6px }}
.foot {{ font-size: 14px; color: var(--muted); border-top: 1px solid var(--rule); padding-top: 16px }}
</style>

<div class="wrap">

<header class="col">
  <div class="eyebrow">Phase-2 L1 · HLT pixel tracks into FastPUPPI</div>
  <h1>L1 Pixel b-Tagging</h1>
  <p class="lede" style="margin-top:14px">Can the Phase-2 pixel tracks, available at 40&nbsp;MHz in the L1 scouting stream, make L1 b-tagging much better than today's L1 NN jet tagger? Good b-tagging at L1 would let HH&rarr;4b triggers lower their jet thresholds, which today are set by rate. This page tracks the revived project (with Marc Huwiler), what was fixed, what now exists on our forks, and the first numbers.</p>
</header>

{banner}
<section>
  <div class="ledger">
    <div><span class="k">Code</span><span class="v">17_0_X</span><span class="s">current FastPUPPI + <code>L1PF_17_0_X</code>, <code>CMSSW_17_0_0_pre2</code></span></div>
    <div><span class="k">Sample used here</span><span class="v">{S['n_sig_events']:,} + {S['n_bkg_events']:,}</span><span class="s">HH&rarr;4b + QCD flat events, PU 200 (Phase2Spring24)</span></div>
    <div><span class="k">Jets in the comparison</span><span class="v">{S['n_b_jets']:,} b / {S['n_light_jets']:,} light</span><span class="s">L1 SC4NG jets, 30&ndash;300 GeV, |&eta;|&lt;2.4</span></div>
    <div><span class="k">b eff. at 10% light mistag</span><span class="v">{pct(NG['beff_at_10pct'])} &rarr; {pct(COMB['beff_at_10pct'])}</span><span class="s">L1 NN tagger (v2_0_0) &rarr; NN + pixel tracks</span></div>
  </div>
</section>

<section class="col">
  <div class="eyebrow">Where it stood</div>
  <h2>What was wrong in the 2025 version</h2>
  <p>Marc's branches (<code>mhuwiler/cmssw:devPixelsForL1</code>, <code>L1PF_14_2_X_devPixelsForL1</code>) wrote the pixel tracks to the ntuple, but the hit positions never worked:</p>
  <ol class="bugs">
    <li><b>Crash.</b> <code>GlobalPositionProducer</code> declared its output map as an empty <code>unique_ptr</code> and then dereferenced it, so the job segfaulted on the first event.</li>
    <li><b>Config mismatch.</b> The position table read <code>pixelTracks</code> (the collection is <code>hltPhase2PixelTracks</code>) and evaluated <code>globalPosition().x()</code> on a stored <code>GlobalPoint</code>.</li>
    <li><b>Empty hit positions.</b> The RecHits stored with the HLT pixel tracks keep only their DetId; their local position is (0,0,0). Even with 1&ndash;2 fixed, every hit sat at its module centre. The hits still reference their pixel clusters, which are in the RAW files, so the fix computes each position from the cluster centroid and the module topology.</li>
  </ol>
  <div class="tablewrap" style="margin-top:14px">
  <table>
    <tr><th>Check on p<sub>T</sub>&gt;5&nbsp;GeV pixel tracks</th><th>Module centres (2025)</th><th>Cluster centroid (now)</th></tr>
    <tr><td>&phi; spread of a track's 4 hits</td><td>0.195 rad</td><td><b>0.0076 rad</b></td></tr>
    <tr><td>max residual to a straight line in r&ndash;z</td><td>5.4 cm</td><td><b>0.011 cm</b></td></tr>
    <tr><td>|&Delta;&phi;(hit, track)|, median</td><td>0.076 rad</td><td><b>0.006 rad</b></td></tr>
  </table></div>
  <p class="muted" style="margin-top:8px">These fixes are also on our forks for Marc's 14_2 version: <code>andrzejnovak/cmssw:L1PF_14_2_X_devPixelsForL1_fixes</code> and <code>andrzejnovak/FastPUPPI:14_2_X_devPixelsForL1_fixes</code>.</p>
</section>

<section class="col">
  <div class="eyebrow">What exists now</div>
  <h2>Ported to the current FastPUPPI</h2>
  <p>Everything is on one fresh branch, <a href="https://github.com/andrzejnovak/FastPUPPI/tree/17_0_X_pixelTracks"><code>andrzejnovak/FastPUPPI:17_0_X_pixelTracks</code></a>, on top of <code>p2l1pfp/FastPUPPI:17_0_X</code>. No extra CMSSW packages are needed beyond the standard FastPUPPI recipe.</p>
  <ul class="tight">
    <li><code>PixelTrackTableProducer</code> runs in the input step (<code>runInputs151X.py</code>, <code>addPixelTracks()</code>) and writes three flat tables: <code>PixelTracks</code> (p<sub>T</sub>, &eta;, &phi;, d<sub>xy</sub>/d<sub>z</sub> with errors, w.r.t. origin and beam spot, vertex index), <code>PixelHits</code> (global x/y/z from the cluster centroid, layer, cluster size and charge, track index) and <code>PixelVertices</code>. Clusters and RecHits are not kept, so the input files stay small. The tables pass through to <code>perfNano.root</code> unchanged.</li>
    <li><code>L1TaggedJetTableProducer</code> (<code>addNGJetTags()</code> in <code>runPerformanceNTuple.py</code>) stores the L1 SC4NG jets with one column per NN class score (b, c, uds, g, &tau;<sup>&plusmn;</sup>, &mu;, e). This is the benchmark.</li>
    <li>The official FastPUPPI input production (<code>151X</code>) keeps no pixel collections, so we make our own inputs from the same Phase2Spring24 RAW. Our inputs are the official content plus the pixel tables.</li>
    <li>Production jobs, local test configs and the analysis are in <code>NtupleProducer/test_pixels/</code>.</li>
  </ul>
</section>

<section>
  <div class="col">
    <div class="eyebrow">Validation</div>
    <h2>Hits land on the detector</h2>
  </div>
  <figure>
    <img src="hit_map.png" alt="Pixel-track hit positions in r versus z and in x versus y for five HH to 4b events">
    <figcaption>Hits of all HLT pixel tracks in five PU 200 events. Barrel layers at r &asymp; 3, 6, 10, 15 cm and the forward disks are clearly resolved. Every track is a quadruplet; the pixel tracks reach |&eta;| &asymp; 4.</figcaption>
  </figure>
</section>

<section>
  <div class="col">
    <div class="eyebrow">First physics look</div>
    <h2>Do pixel tracks separate b from light jets at L1?</h2>
    <p>For every L1 SC4NG jet, take the HLT pixel tracks with p<sub>T</sub>&gt;1&nbsp;GeV within &Delta;R&lt;0.4 that are compatible with the leading pixel vertex (|&Delta;z|&lt;2&nbsp;mm). Sign each track's transverse impact parameter by the jet direction and divide by its uncertainty. b jets come from HH&rarr;4b, light jets from QCD; light jets are reweighted to the b-jet (p<sub>T</sub>, |&eta;|) spectrum, so kinematics carry no information about which sample a jet came from. BDTs are trained on even events and evaluated on odd events.</p>
  </div>
  <div class="figrow">
    <figure><img src="jet_pixel_features.png" alt="Highest and second-highest track impact-parameter significance and number of displaced tracks for b and light jets">
      <figcaption>Track-counting features. The spike at the left edge holds jets with fewer than one or two vertex-compatible tracks.</figcaption></figure>
  </div>
  <div class="figrow">
    <figure><img src="roc.png" alt="ROC curves: light-jet mistag rate versus b-jet efficiency for the L1 NN tagger, pixel-only and combined classifiers">
      <figcaption>Light-jet mistag versus b efficiency. Solid blue: the L1 NN tagger as it runs today. Orange: pixel-track features alone. Red: NN scores plus pixel-track features.</figcaption></figure>
    <figure><img src="jet_ng_score.png" alt="L1 NN tagger b score for b and light jets">
      <figcaption>The L1 NN tagger's b score, b/(b+uds+g), for the same jets.</figcaption></figure>
  </div>
  <div class="tablewrap">
  <table>
    <tr><th>Classifier</th><th>AUC</th><th>b eff. @ 1% light</th><th>b eff. @ 10% light</th></tr>
    <tr><td>L1 NN tagger, b/(b+uds+g)</td><td>{NG['auc']:.3f}</td><td>{pct(NG['beff_at_1pct'])}</td><td>{pct(NG['beff_at_10pct'])}</td></tr>
    <tr><td class="muted">L1 NN scores re-combined by a BDT (reference)</td><td class="muted">{NGBDT['auc']:.3f}</td><td class="muted">{pct(NGBDT['beff_at_1pct'])}</td><td class="muted">{pct(NGBDT['beff_at_10pct'])}</td></tr>
    <tr><td>Pixel tracks, 2nd-highest IP significance</td><td>{TC2['auc']:.3f}</td><td>{pct(TC2['beff_at_1pct'])}</td><td>{pct(TC2['beff_at_10pct'])}</td></tr>
    <tr><td>Pixel tracks, BDT</td><td>{PIX['auc']:.3f}</td><td>{pct(PIX['beff_at_1pct'])}</td><td>{pct(PIX['beff_at_10pct'])}</td></tr>
    <tr><td><b>L1 NN scores + pixel tracks, BDT</b></td><td><b>{COMB['auc']:.3f}</b></td><td><b>{pct(COMB['beff_at_1pct'])}</b></td><td><b>{pct(COMB['beff_at_10pct'])}</b></td></tr>
  </table></div>
  <div class="callout" style="margin-top:18px"><b>Is it flavour or the sample?</b> HH&rarr;4b and QCD events differ in more than jet flavour. As a check, the same classifiers are applied to b and light jets inside HH&rarr;4b events only ({W['n_b']} b / {W['n_l']} light jets, odd events, light reweighted to b kinematics). Pixel BDT AUC: <b>{W['auc_pix']:.3f}</b> (vs {PIX['auc']:.3f} above); highest IP significance alone: {W['auc_ipsig1']:.3f}; L1 NN tagger: {W['auc_ng']:.3f}. The separation comes from the tracks, not from the sample.</div>
  <figure style="margin-top:18px"><img src="roc_ptbins.png" alt="ROC curves in three jet pT ranges">
    <figcaption>The same comparison in jet p<sub>T</sub> bins.</figcaption></figure>
  <div class="tablewrap">
  <table>
    <tr><th>Jet p<sub>T</sub></th><th>b / light jets (test)</th><th>NN @ 10%</th><th>pixel @ 10%</th><th>NN + pixel @ 10%</th></tr>
    {ptrows}
  </table></div>
</section>

<section>
  <div class="col">
    <div class="eyebrow">Napkin math</div>
    <h2>What it could mean for HH&rarr;4b</h2>
    <p>Take the 4 leading L1 jets in each HH&rarr;4b event and count b tags, with the per-jet working point fixed by the light-jet mistag rate. At 1% light mistag per jet, the fraction of HH&rarr;4b events with &ge;3 tags goes from <b>{pct(H['L1 NN tagger']['eff_ge3'][i1])}</b> with the NN tagger to <b>{pct(H['L1 NN + pixel']['eff_ge3'][i1])}</b> with NN + pixel tracks. At 5% it goes from {pct(H['L1 NN tagger']['eff_ge3'][i5])} to {pct(H['L1 NN + pixel']['eff_ge3'][i5])}. A pure-light QCD event passes &ge;3 tags at roughly the cube of the per-jet mistag in both cases, so at the same QCD rate this is the gain in signal acceptance. With the NN tagger as configured here almost no HH&rarr;4b event reaches 3 tags at tight working points, which says more about the NN baseline (see caveats) than about HH&rarr;4b.</p>
  </div>
  <figure><img src="hh4b_event_eff.png" alt="Fraction of HH to 4b events with at least 3 or 4 b tags versus per-jet light mistag rate">
    <figcaption>Fraction of HH&rarr;4b events with &ge;3 and 4 tags among the 4 leading L1 jets (p<sub>T</sub>&gt;30&nbsp;GeV), versus per-jet light mistag.</figcaption></figure>
</section>

<section class="col">
  <div class="eyebrow">Read with care</div>
  <h2>Caveats</h2>
  <ul class="tight">
    <li><b>Small sample.</b> These are first numbers from {njobs} a short local production; the statistical uncertainty on the 1%-mistag points is large.</li>
    <li><b>NN baseline.</b> The current <code>L1PF_17_0_X</code> on <code>CMSSW_17_0_0_pre2</code> runs the first tagger model, <code>L1TSC4NGJetModel_v0</code>. It gave b-vs-light AUC &asymp;0.6 and large &mu;/e scores for b jets. The numbers here use model <code>v2_0_0</code> (the <code>CMSSW_17_0_0_pre7</code> default), with its input code backported (<code>andrzejnovak/cmssw:L1PF_17_0_X_NGJetModel_v2</code>). It runs as it would in CMSSW; it is not retrained on these samples. TrainTagger's b class excludes semileptonic b jets (they are trained as &mu;/e), while here every jet with a b hadron counts as b, so the NN is judged on a slightly harder b sample than it was trained for.</li>
    <li><b>The pixel tracks are HLT pixel tracks</b>, as stored in the Phase2Spring24 RAW. Whether the L1 scouting stream would have the same tracks at 40&nbsp;MHz is the hardware question this study is meant to motivate.</li>
    <li><b>Leading-vertex choice matters.</b> The stored <code>sumPt2</code> is dominated by badly measured high-p<sub>T</sub> pixel tracks and picks a pileup vertex in ~60% of events. The analysis caps track p<sub>T</sub> at 10&nbsp;GeV when choosing the vertex; with that, only ~9% of b jets have fewer than 2 usable tracks.</li>
    <li><b>Hit positions use the cluster centroid</b> without the Lorentz-drift correction (O(10&nbsp;&micro;m) bias). The track-level IP comes from the HLT fit and is not affected.</li>
  </ul>
</section>

<section class="col">
  <div class="eyebrow">Next</div>
  <h2>Next steps</h2>
  <ul class="tight">
    <li>Scale up the production. A local run of 10 HH&rarr;4b + 10 QCD files (200 events each) is in progress on subMIT. OSPool jobs work technically (CMS el9 image, CMSSW tarball) but stall on wide-area reads of the 88&nbsp;GB HH&rarr;4b files, which only exist at CERN and UCL; a Rucio rule to <code>T2_US_MIT</code> would make the grid route practical.</li>
    <li>Confirm the v2_0_0 baseline with the tagger authors, then add pixel-track and pixel-hit inputs to the TrainTagger training instead of a side BDT.</li>
    <li>Use the hits themselves: hits not attached to any pixel track, and per-hit cluster shape, are not used yet.</li>
    <li>Share the branch with Marc and the smart-pixels group once the baseline is confirmed.</li>
  </ul>
</section>

<p class="foot">Produced from <code>/ceph/submit/data/user/n/novaka/l1pixels/</code> with <code>test_pixels/analysis/make_jets.py</code> and <code>plots.py</code>; plots are private work.</p>
</div>
"""
if banner:  # interim page still built from v0-tagger ntuples
    html = html.replace("The numbers here use model <code>v2_0_0</code>", "The numbers on this version of the page still use v0; the regenerated page will use model <code>v2_0_0</code>")
    html = html.replace("L1 NN tagger (v2_0_0) &rarr; NN + pixel tracks", "L1 NN tagger (v0, outdated) &rarr; NN + pixel tracks")
open(outname, "w").write(html)
print("wrote", outname)

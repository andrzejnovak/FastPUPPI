#!/usr/bin/env python3
"""Build the summary page (tabs.html): the HH->4b story first, then how path A works, getting the hits, rate, beyond
HH->4b and code. Styles and diagrams come from the long pilot page (index.html), figures from ../analysis/plots_page.

    python3 build_story.py
Tabs 1-4 are in tabs_main.py; tabs 5 (beyond HH->4b) and 6 (code) are the templates sec_beyond.tmpl and sec_code.tmpl.
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

exec(open("tabs_main.py").read())  # tabs 1-4: tab_hh, tab_how, tab_flow, tab_rate

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

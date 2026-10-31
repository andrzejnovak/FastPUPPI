#!/usr/bin/env python3
"""Render a Slides-artifact deck (project/deck.json + project/slides/*.html) to PNGs, one per slide, approximating the
runtime: 1920x1080 section, Google Fonts from deck.json, /_blob/<id> images mapped to local files.

    python render_deck.py DECK_DIR BLOBMAP.json OUT_DIR [scale]
"""
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

deck, blobmap, out = Path(sys.argv[1]), json.load(open(sys.argv[2])), Path(sys.argv[3])
scale = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
out.mkdir(parents=True, exist_ok=True)
d = json.load(open(deck / "project/deck.json"))
fonts = "".join(f'<link rel="stylesheet" href="{f["href"]}">' for f in d["faces"].values() if "href" in f)
css = ("html,body{margin:0;background:#777}section{position:relative;width:1920px;height:1080px;box-sizing:border-box;"
       "overflow:hidden}section *{box-sizing:border-box}h1,h2,h3,p,ul,ol,table{margin:0}"
       "section div{display:flex;flex-direction:column}img{display:block}aside{display:none}"
       "table{border-collapse:collapse}td,th{padding:0.35em 0.6em;border-bottom:1px solid #e3dccd;text-align:left}")
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=scale)
    for i, sid in enumerate(d["order"], 1):
        s = (deck / f"project/slides/{sid}.html").read_text()
        s = re.sub(r'src="/_blob/([0-9a-f]+)"', lambda m: f'src="file://{blobmap[m.group(1)]}"', s)
        html = f"<!doctype html><html><head><meta charset='utf-8'>{fonts}<style>{css}</style></head><body>{s}</body></html>"
        f = out / f"{i:02d}_{sid}.html"
        f.write_text(html)
        pg.goto(f"file://{f}")
        pg.wait_for_load_state("networkidle")
        # overflow check: any element whose box leaves the 1920x1080 canvas or overlaps the 920 px footer line
        bad = pg.evaluate("""() => { const r = []; document.querySelectorAll('section *').forEach(e => {
            const b = e.getBoundingClientRect(); if (!b.width) return;
            if (b.right > 1921 || b.bottom > 1081) r.push(e.tagName + ' ' + Math.round(b.right) + 'x' + Math.round(b.bottom));
            if (e.scrollHeight > e.clientHeight + 2 && getComputedStyle(e).overflow !== 'visible') r.push('clipped ' + e.tagName); });
            const fl = [...document.querySelectorAll('section > *')].filter(e => getComputedStyle(e).position !== 'absolute')
              .map(e => e.getBoundingClientRect().bottom); return {off: r.slice(0, 5), flowBottom: Math.round(Math.max(...fl, 0))}; }""")
        pg.screenshot(path=str(out / f"{i:02d}_{sid}.png"))
        print(f"{i:02d} {sid:14s} flow bottom {bad['flowBottom']:5d} {'OVER 920' if bad['flowBottom'] > 920 else ''} {bad['off']}", flush=True)
    b.close()

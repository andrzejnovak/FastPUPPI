#!/usr/bin/env python3
"""Build present.html from present.tmpl.html: {{IMG:name.png}} -> base64 data URI from ../analysis/plots_page/."""
import base64
import re

src = open("present.tmpl.html").read()
img = lambda m: "data:image/png;base64," + base64.b64encode(open(f"../analysis/plots_page/{m.group(1)}", "rb").read()).decode()
out = re.sub(r"\{\{IMG:([^}]+)\}\}", img, src)
open("present.html", "w").write(out)
print(f"present.html: {len(out) / 1e6:.2f} MB, {out.count('data:image/png')} figures")

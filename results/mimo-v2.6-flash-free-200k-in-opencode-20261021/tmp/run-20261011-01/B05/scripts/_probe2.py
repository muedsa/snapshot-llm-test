# -*- coding: utf-8 -*-
"""Calibration probe: how much does tw() underestimate real rendered width?

Renders the same string at a sweep of slot widths to find the true threshold,
then compares against the tw() estimate. Kept as evidence for the pitfall note.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from b05_common import box, text, tw
from b05_ui import BG, R_BLOCK, F_NUM, AQUA

S = "超出 18cm"
SZ = 38
WIDTHS = [184, 192, 200, 208, 216, 224, 232, 240]

el = []
el.append(text(20, 8, 660, 30,
               "tw()=%.1f  sweep of slot width, red bar marks the true threshold"
               % tw(S, SZ), 18, "#CCC"))
for i, w in enumerate(WIDTHS):
    y = 50 + i * 44
    el.append(box(20, y, w, 40, "#123"))
    el.append(text(20, y + 2, w, 36, S, SZ, R_BLOCK, bold=True, font=F_NUM))
    el.append(text(w + 40, y + 6, 200, 30, "w=%d" % w, 18, AQUA, font=F_NUM))

doc = ('<Snapshot type="png" background="%s">'
       '<SizedBox width="700" height="430">'
       '<Stack alignment="TOP_LEFT">%s</Stack>'
       '</SizedBox></Snapshot>' % (BG, "".join(el)))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "drafts",
                   "_probe2.snapshot")
with open(out, "w", encoding="utf-8") as f:
    f.write(doc)
print("tw() estimate:", tw(S, SZ))
print("written", out)

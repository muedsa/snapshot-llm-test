# -*- coding: utf-8 -*-
"""Calibration probe 3: how wide do DIGITS really render at 25px bold?

case-08 v2 clipped "26" to "2" even though tw()*1.10 said 31px was enough —
so the 1.10 factor was derived from a 38px CJK+Latin string and may not hold
for numerals in Inter Bold. This sweeps each queue depth string across
multipliers of tw() to find the real threshold.

Temporary evidence file, kept in drafts per the no-cleanup rule.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "scripts"))
from b05_common import box, text, tw
from b05_ui import BG, AQUA, MUTED, R_BLOCK, F_NUM

SZ = 25
STRINGS = ["26", "12", "6.5", "31.5", "46"]
FACTORS = [1.00, 1.05, 1.10, 1.15, 1.20, 1.25, 1.30, 1.40]

el = []
el.append(text(20, 8, 900, 30,
               "slot width = ceil(tw() * factor) at %dpx bold Inter — "
               "find the factor where each string stops clipping" % SZ,
               17, MUTED))

y = 46
col_w = 120
for s in STRINGS:
    base = tw(s, SZ)
    el.append(text(20, y + 6, 130, 30, repr(s) + " tw=%.1f" % base, 16, AQUA,
                   font=F_NUM))
    for i, f in enumerate(FACTORS):
        w = int(math.ceil(base * f))
        x = 160 + i * col_w
        el.append(box(x, y, w, 38, "#123"))
        el.append(text(x, y + 4, w, 34, s, SZ, R_BLOCK, bold=True, font=F_NUM))
        el.append(text(x, y + 42, col_w - 8, 22, "x%.2f=%d" % (f, w), 13,
                       MUTED, font=F_NUM))
    y += 76

doc = ('<Snapshot type="png" background="%s">'
       '<SizedBox width="1180" height="%d">'
       '<Stack alignment="TOP_LEFT">%s</Stack>'
       '</SizedBox></Snapshot>' % (BG, y + 20, "".join(el)))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "drafts",
                   "_probe3.snapshot")
with open(out, "w", encoding="utf-8") as f:
    f.write(doc)
print("written", out)
for s in STRINGS:
    print("  tw(%r, %d) = %.1f" % (s, SZ, tw(s, SZ)))

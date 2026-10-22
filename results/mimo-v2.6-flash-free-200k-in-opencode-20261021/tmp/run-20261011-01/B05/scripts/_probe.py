# -*- coding: utf-8 -*-
"""Diagnostic probe: why does "超出 18cm" render as only "超出"?

Three variants isolate height vs width vs font-family override.
Temporary evidence file, kept in drafts per the no-cleanup rule.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from b05_common import box, text, tw
from b05_ui import BG, R_BLOCK, F_NUM

el = []
# A: the tight box case-07 v2/v3 actually used (183 x 44)
el.append(box(40, 40, 220, 60, "#123"))
el.append(text(40, 50, 183, 44, "超出 18cm", 38, R_BLOCK, bold=True, font=F_NUM))
el.append(text(280, 50, 300, 44, "A: 183x44 +F_NUM", 20, "#AAA"))

# B: generous box, same font override
el.append(box(40, 130, 260, 80, "#123"))
el.append(text(40, 145, 260, 64, "超出 18cm", 38, R_BLOCK, bold=True, font=F_NUM))
el.append(text(320, 145, 300, 44, "B: 260x64 +F_NUM", 20, "#AAA"))

# C: generous box, NO font override (default body font)
el.append(box(40, 240, 260, 80, "#123"))
el.append(text(40, 255, 260, 64, "超出 18cm", 38, R_BLOCK, bold=True))
el.append(text(320, 255, 300, 44, "C: 260x64 default", 20, "#AAA"))

# D: tight box but with height raised to 56 (lineHeight 38*1.28 = 48.6)
el.append(box(40, 330, 220, 76, "#123"))
el.append(text(40, 340, 183, 56, "超出 18cm", 38, R_BLOCK, bold=True, font=F_NUM))
el.append(text(280, 340, 300, 44, "D: 183x56 +F_NUM", 20, "#AAA"))

doc = ('<Snapshot type="png" background="%s">'
       '<SizedBox width="700" height="430">'
       '<Stack alignment="TOP_LEFT">%s</Stack>'
       '</SizedBox></Snapshot>' % (BG, "".join(el)))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "drafts",
                   "_probe.snapshot")
with open(out, "w", encoding="utf-8") as f:
    f.write(doc)
print("tw estimate for 38px:", tw("超出 18cm", 38))
print("written", out)

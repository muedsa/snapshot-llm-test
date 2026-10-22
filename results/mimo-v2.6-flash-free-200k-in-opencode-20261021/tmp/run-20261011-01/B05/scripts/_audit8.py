# -*- coding: utf-8 -*-
"""Pre-render audit for case-08: horizontal collisions the FIT-WARN can't see.

FIT-WARN only checks each box against its own text; two boxes placed side by
side can still overlap. This measures the KPI card 1/2 unit-vs-caption gap and
scans the generated DSL for forbidden ASCII angle brackets.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from b05_common import tw_fit, tw

W = 1440
kw = (W - 64 - 3 * 20) / 4.0
print("card width kw =", kw)

for val, unit, sub in (("46", "/52", "88.5% 覆盖 6 处风险点"),
                       ("3", "座", "2 运行 · 1 检修")):
    x = 32.0
    vw = int(-(-tw_fit(val, 44) // 1))            # ceil
    import math
    vw = int(math.ceil(tw_fit(val, 44)))
    unit_x = x + 24 + vw + 6
    unit_w = tw_fit(unit, 18)
    bw = kw - 48
    sub_w = tw_fit(sub, 15)
    sub_x = x + 24 + bw - sub_w                    # right-aligned in the box
    print("val=%r vw=%d unit %.1f@%.0f..%.0f | sub %.1f@%.0f..%.0f | gap %.1f"
          % (val, vw, unit_w, unit_x, unit_x + unit_w, sub_w, sub_x,
             sub_x + sub_w, sub_x - (unit_x + unit_w)))

# forbidden ASCII angle brackets in the emitted DSL body
body = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                         "drafts", "case-08-v3.snapshot"),
            encoding="utf-8").read()
n_lt, n_gt = body.count("<Text"), body.count("&lt;")
print("XML '<Text' tags:", n_lt, " escaped '&lt;':", n_gt)
import re
bad = [m for m in re.findall(r'text="([^"]*)"', body)
       if "<" in m or ">" in m]
print("rendered text containing ASCII < or >:", bad if bad else "NONE")

# -*- coding: utf-8 -*-
"""A15 字重/字号探针：Overview 与 NORTHSTAR 候选规格渲染，回读墨迹量选择。"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ieces = [
    ("L0_18B_ls0", "Overview", 18, 'fontWeight="BOLD"', ""),
    ("L1_18W800", "Overview", 18, 'fontWeight="W800"', ""),
    ("L2_18W900", "Overview", 18, 'fontWeight="W900"', ""),
    ("L3_20B", "Overview", 20, 'fontWeight="BOLD"', ""),
    ("L4_19W800", "Overview", 19, 'fontWeight="W800"', ""),
    ("L5_18Bls1", "Overview", 18, 'fontWeight="BOLD"', ' letterSpacing="1.0"'),
    ("N0_18B", "NORTHSTAR", 18, 'fontWeight="BOLD"', ' letterSpacing="1.2"'),
    ("N1_18W800", "NORTHSTAR", 18, 'fontWeight="W800"', ' letterSpacing="1.2"'),
    ("N2_18W900", "NORTHSTAR", 18, 'fontWeight="W900"', ' letterSpacing="1.2"'),
    ("P0_195", "Projects", 19.5, "", ""),
    ("P1_20", "Projects", 20, "", ""),
    ("P2_19W4", "Projects", 19, 'fontWeight="W400"', ""),
]
body = ['<Snapshot background="#14233C" type="png"><Stack><SizedBox width="360" height="500" />']
for i, (tag, s, size, fw, extra) in enumerate(ieces):
    y = 18 + i * 40
    body.append(f'<Positioned left="16" top="{y}"><Text fontSize="{size}" color="#FFFFFF" fontFamily="Inter" {fw}{extra}>{s}</Text></Positioned>')
body.append("</Stack></Snapshot>")
os.makedirs("tmp/20261016T164020-m1/A15/probe", exist_ok=True)
open("tmp/20261016T164020-m1/A15/probe/weights.snapshot", "w", encoding="utf-8").write("\n".join(body))
print("probe written", len(ieces), "variants")

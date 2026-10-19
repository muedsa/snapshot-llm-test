# -*- coding: utf-8 -*-
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ieces = [
    ("E1_ov18EB", "Overview", 18, "Inter Extra Bold", ""),
    ("E2_ov19EB", "Overview", 19, "Inter Extra Bold", ""),
    ("E3_ov18BL", "Overview", 18, "Inter Black", ""),
    ("E4_ov20EB", "Overview", 20, "Inter Extra Bold", ""),
    ("B1_ns18EB", "NORTHSTAR", 18, "Inter Extra Bold", ' letterSpacing="1.2"'),
    ("B2_ns18BL", "NORTHSTAR", 18, "Inter Black", ' letterSpacing="1.2"'),
    ("B3_ns19EB", "NORTHSTAR", 19, "Inter Extra Bold", ' letterSpacing="1.2"'),
    ("OV18SB", "Overview", 18, "Inter Semi Bold", ""),
]
body = ['<Snapshot background="#14233C" type="png"><Stack><SizedBox width="360" height="420" />']
for i, (tag, s, size, fam, extra) in enumerate(ieces):
    y = 18 + i * 48
    body.append(f'<Positioned left="16" top="{y}"><Text fontSize="{size}" color="#FFFFFF" fontFamily="{fam}"{extra}>{s}</Text></Positioned>')
body.append("</Stack></Snapshot>")
open("tmp/20261016T164020-m1/A15/probe/families.snapshot", "w", encoding="utf-8").write("\n".join(body))
print("ok")

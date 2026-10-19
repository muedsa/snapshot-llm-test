# -*- coding: utf-8 -*-
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
pieces = [
    ("r1_DV18B", "Design review", 18, "Inter", ' fontWeight="BOLD"', ""),
    ("r2_DV18EB", "Design review", 18, "Inter Extra Bold", "", ""),
    ("r3_DV18EBls", "Design review", 18, "Inter Extra Bold", "", ' letterSpacing="-0.5"'),
    ("r4_DV19EB", "Design review", 19, "Inter Extra Bold", "", ' letterSpacing="-0.5"'),
    ("r5_val34B", "¥128,400", 34, "Inter", ' fontWeight="BOLD"', ""),
    ("r6_val34EB", "¥128,400", 34, "Inter Extra Bold", "", ""),
    ("r7_val33EB", "¥128,400", 33, "Inter Extra Bold", "", ' letterSpacing="-0.5"'),
    ("r8_ti34B", "Workspace Overview", 34, "Inter", ' fontWeight="BOLD"', ""),
    ("r9_ti34EB", "Workspace Overview", 34, "Inter Extra Bold", "", ' letterSpacing="-1.0"'),
    ("r10_nr22B", "Net revenue", 22, "Inter", ' fontWeight="BOLD"', ""),
    ("r11_nr22EB", "Net revenue", 22, "Inter Extra Bold", "", ""),
]
body = ['<Snapshot background="#FFFFFF" type="png"><Stack><SizedBox width="640" height="560" />']
for i, (tag, s, size, fam, fw, extra) in enumerate(pieces):
    y = 16 + i * 50
    body.append(f'<Positioned left="20" top="{y}"><Text fontSize="{size}" color="#18283F" fontFamily="{fam}"{fw}{extra}>{s}</Text></Positioned>')
body.append("</Stack></Snapshot>")
open("tmp/20261016T164020-m1/A15/probe/weights2.snapshot", "w", encoding="utf-8").write("\n".join(body))
print("ok")

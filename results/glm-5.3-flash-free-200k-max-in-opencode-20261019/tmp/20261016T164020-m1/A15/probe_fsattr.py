# -*- coding: utf-8 -*-
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
rows = [
    ("a_fwBOLD", "Design review", 18, ' fontWeight="BOLD"'),
    ("b_fsBOLD", "Design review", 18, ' fontStyle="BOLD"'),
    ("c_fsBI", "Design review", 18, ' fontStyle="BOLD_ITALIC"'),
    ("d_plain", "Design review", 18, ""),
    ("e_val_fw", "¥128,400", 34, ' fontWeight="BOLD"'),
    ("f_val_fs", "¥128,400", 34, ' fontStyle="BOLD"'),
    ("g_nv_fs", "Design review", 18, ' fontStyle="BOLD" fontWeight="BOLD"'),
]
body = ['<Snapshot background="#FFFFFF" type="png"><Stack><SizedBox width="640" height="420" />']
for i, (tag, s, size, attr) in enumerate(rows):
    fam = "Inter"
    y = 16 + i * 52
    body.append(f'<Positioned left="20" top="{y}"><Text fontSize="{size}" color="#18283F" fontFamily="{fam}"{attr} maxLines="1" overflow="CLIP">{s}</Text></Positioned>')
# val rows italic-comparison trimmed; keep 7 rows
body.append("</Stack></Snapshot>")
open("tmp/20261016T164020-m1/A15/probe/fsattr.snapshot", "w", encoding="utf-8").write("\n".join(body))
print("ok")

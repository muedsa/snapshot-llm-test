# -*- coding: utf-8 -*-
"""A15 AA 补偿探针：BOLD + 同色 textShadow(sigma) 模拟更锐更粗的参考渲染。"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
def T(tag, s, size, color, fw, fam, shadow, x, y):
    return (f'<Positioned left="{x}" top="{y}"><Text fontSize="{size}" color="{color}" fontFamily="{fam}"{fw}'
            f' maxLines="1" overflow="CLIP" textShadow="{shadow}">{s}</Text></Positioned>')
rows = [
    ("a_DV18B_s06", "Design review", 18, "#18283F", ' fontWeight="BOLD"', "Inter", "0 0 0.6 #18283F", 20, 16),
    ("b_DV18B_s09", "Design review", 18, "#18283F", ' fontWeight="BOLD"', "Inter", "0 0 0.9 #18283F", 20, 66),
    ("c_DV18B_s12", "Design review", 18, "#18283F", ' fontWeight="BOLD"', "Inter", "0 0 1.2 #18283F", 20, 116),
    ("d_val34_s09", "¥128,400", 34, "#18283F", ' fontWeight="BOLD"', "Inter", "0 0 0.9 #18283F", 20, 166),
    ("e_val34_s12", "¥128,400", 34, "#18283F", ' fontWeight="BOLD"', "Inter", "0 0 1.2 #18283F", 320, 166),
    ("f_WS34_s14", "Workspace Overview", 34, "#18283F", ' fontWeight="BOLD"', "Inter", "0 0 1.4 #18283F", 20, 226),
    ("g_WS34_s18", "Workspace Overview", 34, "#18283F", ' fontWeight="BOLD"', "Inter", "0 0 1.8 #18283F", 20, 286),
    ("h_NR22_s10", "Net revenue", 22, "#18283F", ' fontWeight="BOLD"', "Inter", "0 0 1.0 #18283F", 20, 346),
    ("i_sat18s05", "Saturday, 07 November 2026", 18, "#7C8AA1", "", "Inter", "0 0 0.5 #7C8AA1", 20, 396),
    ("j_sat18dark", "Saturday, 07 November 2026", 18, "#6F7B93", "", "Inter", "0 0 0 #7C8AA1", 20, 446),
    ("k_DV18halfoffset", "Design review", 18, "#18283F", ' fontWeight="BOLD"', "Inter", "0.4 0.4 0 #18283F", 20, 496),
]
body = ['<Snapshot background="#FFFFFF" type="png"><Stack><SizedBox width="640" height="560" />']
for i, r in enumerate(rows):
    body.append(T(r[0], *r[1:7], r[7], r[8]))
body.append("</Stack></Snapshot>")
open("tmp/20261016T164020-m1/A15/probe/shadows.snapshot", "w", encoding="utf-8").write("\n".join(body))
print("ok", len(rows))

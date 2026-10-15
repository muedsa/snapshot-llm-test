#!/usr/bin/env python
"""鎺㈤拡锛氱‘璁ゆ湇鍔＄ Transform.matrix 鐨勫疄闄呰涔夛紙鏋㈣酱琛ュ伩鏄惁鑷姩鏂藉姞锛夈€?

鐢诲嚭鍚屼竴鏋氬嵃绔犵殑 4 涓彉浣擄細
 P0 鍙傝€冿細matrix = 鍗曚綅闃?
 P1 缁曟灑杞寸殑瀹屾暣鐭╅樀锛堝惈骞崇Щ 120,0锛?
 P2 鍙湁绾挎€ч儴鍒嗭紙涓嶅惈骞崇Щ锛?
 P3 鍙湁绾挎€ч儴鍒?+ 鏄惧紡鏋㈣酱琛ュ伩锛屼絾鎶婂钩绉绘斁鍦?m[8],m[9] 鐨勫彟涓€绉嶅啓娉?
鐢?measure 鑴氭湰鎸夐鑹插垎鍒噺鍑哄悇鑷綅缃紝鍒ゆ柇寮曟搸鍒板簳鎬庝箞瑙ｉ噴杩?16 涓暟銆?
"""
from __future__ import annotations

import sys

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")

RECTS = [(8, 8, 28, 92, "#E54B4B"), (36, 72, 68, 28, "#2364DB"), (64, 8, 40, 28, "#EAB53B")]
DOT = (91, 49, 8, "#111111")

CASES = [
    ("P0-identity", "1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1"),
    ("P1-aboutpivot", "0,-1,0,0,1,0,0,0,0,0,1,0,120,0,0,1"),
    ("P2-linear-only", "0,-1,0,0,1,0,0,0,0,0,1,0,0,0,0,1"),
    ("P3-trans-in-8-9", "0,-1,0,0,1,0,0,0,120,0,1,0,0,0,0,1"),
    ("P4-linear-topLeft", "0,-1,0,0,1,0,0,0,0,0,1,0,0,0,0,1"),
]

P = ['<Positioned left="0" top="0" width="1000" height="1000">'
     '<Container width="1000" height="1000" color="#FFFFFF"/></Positioned>']
for i, (name, m) in enumerate(CASES):
    bx = 40 + (i % 3) * 320
    by = 40 + (i // 3) * 320
    P.append(f'<Positioned left="{bx - 40}" top="{by - 20}" width="280" height="280">'
             f'<Container width="280" height="280" color="#F1F5F9" border="1 SOLID #94A3B8"/></Positioned>')
    nodes = []
    for x, y, w, h, c in RECTS:
        nodes.append(f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
                     f'<Container width="{w}" height="{h}" color="{c}"/></Positioned>')
    dx, dy, dr, dc = DOT
    nodes.append(f'<Positioned left="{dx-dr}" top="{dy-dr}" width="{2*dr}" height="{2*dr}">'
                 f'<ClipOval><Container width="{2*dr}" height="{2*dr}" color="{dc}"/></ClipOval></Positioned>')
    align = "CENTER" if name != "P4-linear-topLeft" else "TOP_LEFT"
    P.append(f'<Positioned left="{bx}" top="{by}" width="120" height="120">'
             f'<Transform matrix="({m})" alignment="{align}">'
             f'<Container width="120" height="120"><Stack fit="EXPAND">'
             f'{"".join(nodes)}</Stack></Container></Transform></Positioned>')
    P.append(f'<Positioned left="{bx - 30}" top="{by + 130}" width="260" height="30">'
             f'<Text fontSize="20" fontFamily="Noto Sans CJK SC">{name}</Text></Positioned>')
    # 鍙傝€冩锛堝眬閮?0-120 鍘熶綅锛?
    for a, b in (((bx, by), (bx + 120, by)), ((bx + 120, by), (bx + 120, by + 120)),
                 ((bx + 120, by + 120), (bx, by + 120)), ((bx, by + 120), (bx, by))):
        w = abs(b[0] - a[0]) or 1
        h = abs(b[1] - a[1]) or 1
        if w > 1:
            P.append(f'<Positioned left="{a[0]}" top="{a[1]}" width="{w}" height="1">'
                     f'<Container width="{w}" height="1" color="#CBD5E1"/></Positioned>')
        if h > 1:
            P.append(f'<Positioned left="{a[0]}" top="{a[1]}" width="1" height="{h}">'
                     f'<Container width="1" height="{h}" color="#CBD5E1"/></Positioned>')

out = ('<Snapshot type="png">\n<Container width="1000" height="1000">\n<Stack fit="EXPAND">\n'
       + "".join(P) + '\n</Stack>\n</Container>\n</Snapshot>\n')
open("tmp/run-20261011-01/A09/probe.snapshot", "w", encoding="utf-8").write(out)
print("probe written", len(out))


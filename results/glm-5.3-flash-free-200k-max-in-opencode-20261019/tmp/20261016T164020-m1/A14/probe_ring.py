# -*- coding: utf-8 -*-
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
OUT = "tmp/20261016T164020-m1/A14/probe"
os.makedirs(OUT, exist_ok=True)
def rc(x, y, w, h, r=None, color=None, border=0, border_color=None):
    a = f'width="{w}" height="{h}"'
    if color: a += f' color="{color}"'
    if r: a += f' borderRadius="{r}"'
    if border: a += f' borderWidth="{border}" borderColor="{border_color}"'
    return f'<Positioned left="{x}" top="{y}"><Container {a} /></Positioned>'
body = [
    rc(20, 20, 40, 40, 20, None, 6, "#FF5555"),          # A: 无 color + border
    rc(100, 20, 40, 40, 20, "#00000000", 6, "#55FF55"),  # B: 全透明 color + border
    rc(180, 20, 40, 40, 20, "#99CCFF"),                  # C1 外盘
    rc(193, 33, 14, 14, 7, "#0E1526"),                   # C2 内盘（双圆成环）
    rc(260, 20, 12, 12, 6, None, 4, "#FFCC00"),          # D: 12px 小环 border4
]
dsl = '<Snapshot background="#0E1526" type="png"><Stack><SizedBox width="320" height="120" />\n' + "\n".join(body) + "\n</Stack></Snapshot>"
open(os.path.join(OUT, "probe.snapshot"), "w", encoding="utf-8").write(dsl)
print(dsl)

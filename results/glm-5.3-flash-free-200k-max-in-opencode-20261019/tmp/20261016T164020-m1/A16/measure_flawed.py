# -*- coding: utf-8 -*-
"""A16 取证：flawed-report.png 精确测量（轴刻度/柱几何/图例/卡片/配色）。"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image

OUT = {}
im = Image.open("tasks/A16-visual-data-forensics/inputs/flawed-report.png").convert("RGB")
px = im.load()
W, H = im.size
OUT["size"] = [W, H]

def runs(y, pred, x0=0, x1=None):
    x1 = x1 or W
    segs, s = [], None
    for x in range(x0, x1):
        ok = pred(*px[x, y])
        if ok and s is None:
            s = x
        elif not ok and s is not None:
            segs.append([s, x - 1]); s = None
    if s is not None:
        segs.append([s, x1 - 1])
    return segs

def col_top(x, pred, y0, y1):
    for y in range(y0, y1):
        if pred(*px[x, y]):
            return y
    return None

def col_bot(x, pred, y0, y1):
    for y in range(y1 - 1, y0, -1):
        if pred(*px[x, y]):
            return y
    return None

# 配色采样
OUT["samples"] = {
    "bg": "#%02X%02X%02X" % px[1250, 120],
    "card": "#%02X%02X%02X" % px[600, 250],
    "bar_blue": "#%02X%02X%02X" % px[330, 500],
    "bar_orange": "#%02X%02X%02X" % px[393, 500],
}

BLUE = lambda r, g, b: 25 <= r <= 90 and 70 <= g <= 130 and 190 <= b <= 255
ORANGE = lambda r, g, b: r > 200 and 120 <= g <= 180 and b < 110

# 8 根柱 x 范围（扫 y=460 与 y=520 取并集）
r460b = runs(460, BLUE, 140, 1260); r460o = runs(460, ORANGE, 140, 1260)
r520b = runs(520, BLUE, 140, 1260); r520o = runs(520, ORANGE, 140, 1260)
OUT["bar_x_runs@460"] = {"blue": r460b, "orange": r460o}
OUT["bar_x_runs@520"] = {"blue": r520b, "orange": r520o}

# 每根柱顶部/底部 y（用段中心列）
bars = []
def merge(segs):
    out = []
    for s in sorted([tuple(x) for x in segs]):
        if out and s[0] <= out[-1][1] + 2:
            out[-1] = (out[-1][0], max(out[-1][1], s[1]))
        else:
            out.append(s)
    return [list(x) for x in out]

blues = merge(r460b + r520b)
oranges = merge(r460o + r520o)
def measure(colsegs, pred, i, kind):
    c = (colsegs[i][0] + colsegs[i][1]) // 2
    top = col_top(c, pred, 150, 600)
    bot = col_bot(c, pred, 150, 600)
    bars.append({"kind": kind, "i": i, "x_center": c, "x": colsegs[i], "top": top, "bottom": bot})
for i, s in enumerate(blues):
    measure(blues, BLUE, i, "blue")
for i, s in enumerate(oranges):
    measure(oranges, ORANGE, i, "orange")
OUT["bars"] = bars

# y 轴刻度标签：深色文字带（x 78..138），并找每标签 y 中心
def text_bands(x0, x1, y0, y1, pred):
    bands, s = [], None
    for y in range(y0, y1):
        has = any(pred(*px[x, y]) for x in range(x0, x1))
        if has and s is None:
            s = y
        elif not has and s is not None:
            bands.append([s, y - 1]); s = None
    if s is not None:
        bands.append([s, y1 - 1])
    return bands

DARK = lambda r, g, b: r < 120 and g < 120 and b < 130
OUT["yaxis_label_bands"] = text_bands(60, 140, 240, 600, DARK)
# 刻度标签包围盒（逐带 x 极值）
lbl_boxes = []
for b in OUT["yaxis_label_bands"]:
    xs = [x for y in range(b[0], b[1] + 1) for x in range(50, 145) if DARK(*px[x, y])]
    lbl_boxes.append([min(xs), max(xs)] if xs else None)
OUT["yaxis_label_x"] = lbl_boxes

# 横向网格线检测：整行 150..1180 浅灰占比
grid_rows = []
for y in range(240, 600):
    n = sum(1 for x in range(150, 1180, 4) if abs(px[x, y][0] - 229) < 15 and abs(px[x, y][1] - 229) < 15 and abs(px[x, y][2] - 231) < 15)
    if n > 180:
        grid_rows.append(y)
OUT["grid_rows(~#E5E5E7)"] = grid_rows

# 图例：图表卡右上 小方块（蓝/橙）
legend_blue = [], []
lb = runs(300, BLUE, 900, 1260); lo = runs(300, ORANGE, 900, 1260)
OUT["legend_rows@300"] = {"blue": lb, "orange": lo}
# 图例方块上文本带
OUT["legend_text_bands"] = text_bands(950, 1260, 280, 330, DARK)

# 卡片结构：白色卡边界（row 扫描）
OUT["card_rows:white"] = runs(700, lambda r, g, b: r > 245 and g > 245 and b > 240, 0, 1280)
OUT["card_rows:amber"] = runs(700, lambda r, g, b: r > 240 and 200 < g < 235 and 150 < b < 195, 0, 1280)
OUT["card_cols:col400"] = [y for y in range(600, 900, 1) if px[400, y][0] > 245 and px[400, y][1] > 245 and px[400, y][2] > 240][:3]
# 底部文本带（明细卡文字）
OUT["detail_text_bands@x90-820"] = text_bands(90, 830, 620, 890, DARK)
# 柱顶数值标签带（蓝柱上方）
OUT["value_label_bands"] = text_bands(300, 1260, 280, 460, lambda r, g, b: DARK(r, g, b))

json.dump(OUT, open("tmp/20261016T164020-m1/A16/steps/flaw-scan.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in OUT.items():
    if k == "bars":
        for b in v:
            print("bar", b)
    else:
        print(k, "=", v)

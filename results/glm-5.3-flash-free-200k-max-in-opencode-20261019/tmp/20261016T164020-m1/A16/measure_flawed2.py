# -*- coding: utf-8 -*-
"""A16 取证二：图例盒/明细致值盒/季度标签/卡片精确边界。"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image

im = Image.open("tasks/A16-visual-data-forensics/inputs/flawed-report.png").convert("RGB")
px = im.load()
OUT = {}

def runs(y, pred, x0, x1):
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

def bbox(x0, y0, x1, y1, pred, step=1):
    xs, ys = [], []
    for y in range(y0, y1, step):
        for x in range(x0, x1, step):
            if pred(*px[x, y]):
                xs.append(x); ys.append(y)
    return [min(xs), min(ys), max(xs), max(ys)] if xs else None

BLUE = lambda r, g, b: 25 <= r <= 90 and 70 <= g <= 130 and 190 <= b <= 255
ORANGE = lambda r, g, b: r > 200 and 110 <= g <= 185 and b < 110
DARK = lambda r, g, b: r < 120 and g < 120 and b < 130
WHITE = lambda r, g, b: r > 250 and g > 250 and b > 245
AMBER = lambda r, g, b: r >= 250 and 230 <= g <= 248 and 195 <= b <= 225

# 图例：y=198 行 swatch runs + 文字带
OUT["legend_blue@198"] = runs(198, BLUE, 840, 1270)
OUT["legend_orange@198"] = runs(198, ORANGE, 840, 1270)
# 图例文字（右于方块）
OUT["legend_text_bbox_total"] = bbox(840, 178, 1270, 214, DARK)
# 柱顶数值标签逐柱盒
LAB = []
for t, xs in [("blueQ", [255, 491, 727, 963]), ("orangeQ", [331, 567, 803, 1039])]:
    for c in xs:
        LAB.append({"kind": t, "x_center": c,
                    "box": bbox(c - 45, 250, c + 45, 420, DARK)})
OUT["bar_value_labels"] = LAB
# X 轴季度标签带
QL = []
for y0, y1 in [(580, 640)]:
    bands, s = [], None
    for y in range(y0, y1):
        has = any(DARK(*px[x, y]) for x in range(150, 1180))
        if has and s is None:
            s = y
        elif not has and s is not None:
            bands.append([s, y - 1]); s = None
    if s is not None:
        bands.append([s, y1 - 1])
    for b in bands:
        out = []
        for seg in runs((b[0] + b[1]) // 2, DARK, 150, 1180):
            if seg[1] - seg[0] > 4:
                out.append(seg)
        QL.append({"band": b, "runs": out})
OUT["quarter_labels"] = QL
# 明细卡数值盒
DV = []
for c in [130, 300, 470, 640, 700, 760]:
    pass
vals = runs(771, DARK, 80, 830)
OUT["detail_value_runs@771"] = vals
# 卡片边界
OUT["chart_card_row250"] = runs(250, WHITE, 30, 1280)
OUT["card_col400_white"] = [y for y in range(140, 900) if WHITE(*px[400, y]) == False] and None
ys = [y for y in range(140, 620) if WHITE(*px[400, y])]
OUT["chart_card_y(col400)"] = [min(ys), max(ys)] if ys else None
ys = [y for y in range(600, 890) if WHITE(*px[400, y])]
OUT["detail_card_y(col400)"] = [min(ys), max(ys)] if ys else None
ys = [y for y in range(600, 890) if AMBER(*px[1000, y])]
OUT["focus_card_y(col1000)"] = [min(ys), max(ys)] if ys else None
OUT["focus_card_row700amber"] = runs(700, AMBER, 800, 1280)
# 标题/副标题盒
OUT["title_box"] = bbox(40, 25, 1270, 80, DARK)
OUT["subtitle_box"] = bbox(40, 80, 1270, 118, lambda r, g, b: 90 < r < 160 and 95 < g < 165 and 105 < b < 175)
# 页脚盒
OUT["footer_box"] = bbox(50, 850, 900, 890, lambda r, g, b: 130 < r < 190 and 130 < g < 190 and 130 < b < 190)
# 明细卡标题/列标签框
OUT["detail_title_box"] = bbox(80, 655, 500, 700, DARK)
OUT["detail_qlabels@725"] = runs(725, DARK, 80, 830)
# focus 卡文本框
OUT["focus_text_bbox"] = bbox(850, 655, 1260, 810, lambda r, g, b: r < 180 and g < 150 and b < 130)

json.dump(OUT, open("tmp/20261016T164020-m1/A16/steps/flaw-scan2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in OUT.items():
    print(k, "=", v)

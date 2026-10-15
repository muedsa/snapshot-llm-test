#!/usr/bin/env python
"""A15 参考图第三次测量：卡片外框精确值 + 文字/图标颜色取样。"""
from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path

from PIL import Image

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
REF = BASE / "tasks/A15-reference-reconstruction/inputs/reference.png"
OUTD = BASE / "tmp/run-20261011-01/A15/drafts"
WHITE = (255, 255, 255)
MAIN = (243, 246, 251)
SIDE = (20, 35, 60)


def hx(t):
    return "#%02X%02X%02X" % t[:3]


def edge(im, y, x0, x1, bg):
    """沿行找 bg→非bg 的边界"""
    px = im.load()
    out = []
    prev = px[x0, y] == bg
    for x in range(x0 + 1, x1):
        cur = px[x, y] == bg
        if cur != prev:
            out.append((x, "enter" if cur else "leave"))
            prev = cur
    return out


def vedge(im, x, y0, y1, bg):
    px = im.load()
    out = []
    prev = px[x, y0] == bg
    for y in range(y0 + 1, y1):
        cur = px[x, y] == bg
        if cur != prev:
            out.append((y, "enter" if cur else "leave"))
            prev = cur
    return out


def darkest(box, img):
    px = img.load()
    x0, y0, x1, y1 = box
    cnt = Counter()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = px[x, y]
            if sum(c) < 620:
                cnt[c] += 1
    return hx(cnt.most_common(1)[0][0]) if cnt else None


def main() -> None:
    with Image.open(REF) as s:
        s.load()
        im = s.convert("RGB")
    W, H = im.size
    px = im.load()
    r = {}

    # ---- 卡片外框：沿主背景找 enter/leave
    r["edges_y200"] = edge(im, 200, 230, 1440, MAIN)
    r["edges_y450"] = edge(im, 450, 230, 1440, MAIN)
    r["edges_y700"] = edge(im, 700, 230, 1440, MAIN)
    r["edges_x300_v_kpi"] = vedge(im, 300, 120, 300, MAIN)
    r["edges_x300_v_chart"] = vedge(im, 300, 300, 610, MAIN)
    r["edges_x300_v_table"] = vedge(im, 300, 610, 870, MAIN)
    r["edges_x1300_v_kpi"] = vedge(im, 1300, 120, 300, MAIN)
    r["edges_x1300_v_chart"] = vedge(im, 1300, 300, 610, MAIN)
    r["edges_x1300_v_table"] = vedge(im, 1300, 610, 870, MAIN)

    # ---- 侧栏边界
    r["sidebar_edge_y300"] = edge(im, 300, 0, 260, SIDE)
    r["sidebar_v_y100"] = vedge(im, 110, 0, 200, SIDE)

    # ---- 颜色取样（取区域内最深色 = 文字色）
    r["colors"] = {
        "title": darkest((261, 38, 600, 70), im),
        "subtitle": darkest((261, 84, 520, 104), im),
        "brand_text": darkest((70, 36, 195, 56), im),
        "nav_overview_text": darkest((63, 128, 200, 146), im),
        "nav_other_text": darkest((63, 252, 200, 274), im),
        "kpi_label": darkest((284, 158, 420, 172), im),
        "kpi_value": darkest((284, 196, 460, 232), im),
        "kpi_change": darkest((284, 244, 380, 262), im),
        "kpi_change_ords": darkest((668, 244, 764, 262), im),
        "kpi_change_refund": darkest((1052, 244, 1150, 262), im),
        "card_title_chart": darkest((283, 334, 430, 356), im),
        "chart_period": darkest((895, 334, 980, 356), im),
        "axis_unit": darkest((283, 373, 350, 388), im),
        "axis_ticks": darkest((295, 396, 322, 410), im),
        "month_labels": darkest((370, 556, 410, 576), im),
        "activity_title": darkest((1055, 332, 1210, 360), im),
        "activity_text": darkest((1076, 392, 1200, 415), im),
        "activity_time": darkest((1076, 419, 1120, 436), im),
        "table_title": darkest((283, 642, 470, 670), im),
        "thead_text": darkest((296, 696, 360, 712), im),
        "row_project": darkest((296, 730, 470, 754), im),
        "row_owner": darkest((781, 730, 870, 754), im),
        "status_text_1": darkest((1040, 734, 1165, 752), im),
        "status_text_2": darkest((1040, 770, 1165, 788), im),
        "status_text_3": darkest((1040, 805, 1165, 823), im),
        "due_text": darkest((1229, 730, 1290, 754), im),
        "footer": darkest((259, 864, 520, 880), im),
        "pro_label": darkest((36, 766, 190, 784), im),
        "pro_members": darkest((36, 800, 190, 820), im),
        "pro_manage": darkest((36, 831, 190, 852), im),
    }

    # ---- 图标/圆点颜色（取该区域的主色）
    def dominant(box, only=None):
        x0, y0, x1, y1 = box
        cnt = Counter()
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                c = px[x, y]
                if only is None or only(c):
                    cnt[c] += 1
        return [(hx(c), n) for c, n in cnt.most_common(4)]

    r["brand_mark_colors"] = dominant((30, 33, 57, 60))
    r["nav_dot_selected"] = dominant((32, 128, 48, 144), only=lambda c: c != SIDE and c != (41, 68, 103))
    r["nav_dot_other"] = dominant((32, 254, 48, 270), only=lambda c: c != SIDE)
    r["activity_dot_colors"] = {
        "i0": dominant((1050, 396, 1066, 412), only=lambda c: c != WHITE),
        "i1": dominant((1050, 456, 1066, 472), only=lambda c: c != WHITE),
        "i2": dominant((1050, 516, 1066, 532), only=lambda c: c != WHITE),
    }
    r["gridline_color"] = dominant((340, 404, 960, 407), only=lambda c: c != WHITE)
    r["bar_colors"] = [dominant((360, 500, 408, 540), only=lambda c: c != WHITE)[:1],
                     dominant((861, 430, 914, 540), only=lambda c: c != WHITE)[:1]]

    # ---- 状态药丸完整框与圆角
    for i, y in enumerate((743, 778, 813)):
        xs = [x for x in range(1010, 1200) if px[x, y] != WHITE]
        ys = [yy for yy in range(y - 20, y + 20) if px[1100, yy] != WHITE]
        r[f"pill{i}_bbox"] = [min(xs), min(ys), max(xs), max(ys)]
        r[f"pill{i}_fill"] = hx(px[min(xs) + 3, y])

    # ---- 图表零线端点
    r["zero_line"] = {"y": 549, "x_left": 333, "x_right": 969,
                      "color": dominant((340, 548, 960, 551), only=lambda c: c != WHITE)[0][0]}
    # ---- 导航选中态圆角
    r["nav_selected"] = {"bbox": [18, 116, 201, 163],
                         "corner_probe": [[px[x, 118] for x in range(18, 34)],
                                          [px[20, y] for y in range(116, 132)]]}

    (OUTD / "reference-geometry-3.json").write_text(
        json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    for k, v in r.items():
        print(k, "=", v)


if __name__ == "__main__":
    main()
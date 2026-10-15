#!/usr/bin/env python
"""A15 参考图精细测量：卡片包围盒、图表网格线与零线、表格行、导航与状态药丸。"""
from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
REF = BASE / "tasks/A15-reference-reconstruction/inputs/reference.png"
OUTD = BASE / "tmp/run-20261011-01/A15/drafts"

WHITE = (255, 255, 255)


def hx(t):
    return "#%02X%02X%02X" % t[:3]


def main() -> None:
    with Image.open(REF) as s:
        s.load()
        im = s.convert("RGB")
    W, H = im.size
    px = im.load()
    rep = {}

    # ---- 1. 主区白色卡片连通域（按行扫描，合并成矩形）
    def white_bbox(x0, y0, x1, y1):
        xs, ys = [], []
        for y in range(y0, y1):
            for x in range(x0, x1):
                if px[x, y] == WHITE:
                    xs.append(x)
                    ys.append(y)
        return [min(xs), min(ys), max(xs), max(ys)] if xs else None

    # KPI 卡：y 带 130..285
    cards = []
    y = 130
    row = [x for x in range(230, W) if px[x, y] == WHITE]
    if row:
        # 分段
        segs, s0 = [], row[0]
        for a, b in zip(row, row[1:]):
            if b - a > 1:
                segs.append((s0, a))
                s0 = b
        segs.append((s0, row[-1]))
        for a, b in segs:
            bb = white_bbox(a, 125, b + 1, 295)
            if bb:
                cards.append(bb)
    rep["kpi_card_bboxes"] = cards

    # 图表卡 y=330 / 活动卡：同法
    y2 = 340
    row2 = [x for x in range(230, W) if px[x, y2] == WHITE]
    segs, s0 = [], row2[0]
    for a, b in zip(row2, row2[1:]):
        if b - a > 1:
            segs.append((s0, a))
            s0 = b
    segs.append((s0, row2[-1]))
    rep["mid_card_xsegs_y340"] = segs
    rep["chart_card_bbox"] = white_bbox(segs[0][0] - 2, 310, segs[0][1] + 3, 595)
    rep["activity_card_bbox"] = white_bbox(segs[1][0] - 2, 310, segs[1][1] + 3, 595) \
        if len(segs) > 1 else None

    y3 = 640
    row3 = [x for x in range(230, W) if px[x, y3] == WHITE]
    rep["table_card_bbox"] = white_bbox(min(row3) - 2, 620, max(row3) + 3, 845)

    # ---- 2. 图表网格线：在 x∈[330,960] 上统计每行的非白像素数
    prof = []
    for y in range(390, 600):
        n = sum(1 for x in range(330, 960) if px[x, y] != WHITE)
        if n > 400:
            prof.append((y, n, hx(px[700, y])))
    rep["chart_gridline_rows"] = prof
    # 每条线的横向起止
    for (yy, _, _) in prof:
        xs = [x for x in range(300, 1000) if px[x, yy] != WHITE]
        rep.setdefault("chart_gridline_extent", []).append(
            {"y": yy, "x_left": min(xs), "x_right": max(xs), "color": hx(px[700, yy])})

    # 零线：含柱子的那一行 → 用 y=548 附近
    zero = [yy for (yy, _, _) in prof if yy >= 540]
    rep["zero_line_y_candidates"] = zero

    # ---- 3. 柱体（精确蓝色 #245CE4 家族）
    bars = []
    for x in range(340, 960):
        run = []
        for y in range(390, 560):
            r, g, b = px[x, y]
            if b > 200 and r < 110 and g < 130 and b - r > 110:
                run.append(y)
        if run:
            bars.append((x, min(run), max(run)))
    groups, cur = [], []
    for b in bars:
        if cur and b[0] - cur[-1][0] <= 2:
            cur.append(b)
        else:
            if cur:
                groups.append(cur)
            cur = [b]
    if cur:
        groups.append(cur)
    rep["bars"] = [{"x_left": g[0][0], "x_right": g[-1][0],
                    "width": g[-1][0] - g[0][0] + 1,
                    "x_center": round((g[0][0] + g[-1][0]) / 2, 1),
                    "y_top": min(v[1] for v in g), "y_bottom": max(v[2] for v in g),
                    "height": max(v[2] for v in g) - min(v[1] for v in g) + 1,
                    "center_color": hx(px[g[0][0] + 5, (g[0][1] + g[-1][2]) // 2])}
                   for g in groups]

    # ---- 4. 表格：行分隔线 + 表头底色
    prof2 = []
    for y in range(680, 845):
        n = sum(1 for x in range(300, 1380) if px[x, y] == (243, 246, 251))
        if n > 900:
            prof2.append((y, n))
    rep["table_header_rows_bgF3F6FB"] = prof2
    sep = []
    for y in range(715, 840):
        n = sum(1 for x in range(300, 1380) if px[x, y] != WHITE and px[x, y] != (243, 246, 251))
        if n > 700:
            sep.append((y, n, hx(px[700, y])))
    rep["table_row_separators"] = sep

    # ---- 5. 状态药丸：扫描行内的非白非表头色块
    for i, (y0, y1, name) in enumerate([(730, 760, "row1"), (765, 795, "row2"),
                                        (800, 830, "row3")]):
        segs = []
        x = 1020
        while x < 1200:
            c = px[x, y0 + 15]
            if c != WHITE:
                x0 = x
                while x < 1200 and px[x, y0 + 15] != WHITE:
                    x += 1
                segs.append((x0, x - 1, hx(px[(x0 + x - 1) // 2, y0 + 15])))
            else:
                x += 1
        ys = [y for y in range(y0, y1) if px[1100, y] != WHITE]
        rep[f"status_pill_{name}"] = {"x": [segs[0][0], segs[-1][1]] if segs else None,
                                      "y": [min(ys), max(ys)] if ys else None,
                                      "fill": segs[0][2] if segs else None}

    # ---- 6. 导航项 y 带与选中态外框
    nav = []
    for yy in range(100, 370):
        n = sum(1 for x in range(20, 200) if px[x, yy] == (41, 68, 103))
        if n > 120:
            nav.append(yy)
    rep["nav_selected_rows"] = [min(nav), max(nav)] if nav else None
    if nav:
        xs = [x for x in range(10, 215) if px[x, (min(nav) + max(nav)) // 2] == (41, 68, 103)]
        rep["nav_selected_bbox"] = [min(xs), min(nav), max(xs), max(nav)]
    # 其他导航项文字 y
    rep["nav_item_text_rows"] = []
    for yy in range(100, 370):
        n = sum(1 for x in range(50, 200) if px[x, yy][0] > 150 and px[x, yy][2] > 180)
        if n > 20:
            rep["nav_item_text_rows"].append(yy)

    # ---- 7. 导出按钮
    xs = [x for x in range(1100, 1440) if px[x, 63] == (36, 92, 228)]
    ys = [y for y in range(20, 110) if px[1290, y] == (36, 92, 228)]
    rep["export_btn_bbox"] = [min(xs), min(ys), max(xs), max(ys)] if xs and ys else None

    # ---- 8. PRO 卡
    xs = [x for x in range(0, 220) if px[x, 800] == (35, 57, 84)]
    ys = [y for y in range(700, 900) if px[110, y] == (35, 57, 84)]
    rep["pro_card_bbox"] = [min(xs), min(ys), max(xs), max(ys)] if xs and ys else None

    # ---- 9. 品牌标记
    xs = [x for x in range(0, 220) if px[x, 46][1] > 180 and px[x, 46][2] > 150]
    ys = [y for y in range(10, 90) if px[43, y][1] > 180 and px[43, y][2] > 150]
    rep["brand_mark_bbox"] = [min(xs), min(ys), max(xs), max(ys)] if xs and ys else None
    rep["brand_mark_color"] = hx(px[(min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2])

    # ---- 10. 活动项圆点与文字
    for i, yc in enumerate([400, 461, 521]):
        xs = [x for x in range(1040, 1070) if px[x, yc] != WHITE and px[x, yc] != (255, 255, 255)]
        segs = []
        x = 1045
        while x < 1065:
            c = px[x, yc]
            if c != WHITE:
                x0 = x
                while x < 1065 and px[x, yc] != WHITE:
                    x += 1
                segs.append((x0, x - 1, hx(px[(x0 + x - 1) // 2, yc])))
            else:
                x += 1
        ys = [y for y in range(yc - 25, yc + 25) if px[1052, y] != WHITE]
        rep[f"activity_dot_{i}"] = {"bbox": [min(xs), min(ys), max(xs), max(ys)]
                                    if xs and ys else None,
                                    "color": segs[0][2] if segs else None}

    (OUTD / "reference-geometry.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    for k, v in rep.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
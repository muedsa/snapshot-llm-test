#!/usr/bin/env python
"""A15 参考图二次精细测量：补齐卡片包围盒、网格线起止、表头带、文字墨迹行。"""
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


def white_run_y(im, x, y0, y1):
    px = im.load()
    runs, cur, s = [], None, y0
    for y in range(y0, y1):
        c = px[x, y] == WHITE
        if c != cur:
            if cur:
                runs.append((s, y - 1))
            cur, s = c, y
    if cur:
        runs.append((s, y1 - 1))
    return [r for r in runs if r[1] - r[0] >= 5]


def white_run_x(im, y, x0, x1):
    px = im.load()
    runs, cur, s = [], None, x0
    for x in range(x0, x1):
        c = px[x, y] == WHITE
        if c != cur:
            if cur:
                runs.append((s, x - 1))
            cur, s = c, x
    if cur:
        runs.append((s, x1 - 1))
    return [r for r in runs if r[1] - r[0] >= 5]


def ink_rows(im, x0, x1, y0, y1, bg, thr=28):
    """在给定区域内找与 bg 不同且足够"非背景"的像素行（文字/图形行带）。"""
    px = im.load()
    out = []
    cur = None
    for y in range(y0, y1):
        n = 0
        for x in range(x0, x1):
            c = px[x, y]
            if abs(c[0] - bg[0]) + abs(c[1] - bg[1]) + abs(c[2] - bg[2]) > thr:
                n += 1
        if n > 2:
            if cur is None:
                cur = [y, y, n]
            else:
                cur[1] = y
                cur[2] = max(cur[2], n)
        else:
            if cur:
                out.append(tuple(cur))
                cur = None
    if cur:
        out.append(tuple(cur))
    return out


def ink_cols(im, x0, x1, y0, y1, bg, thr=28, minpix=2):
    px = im.load()
    xs = []
    for x in range(x0, x1):
        n = 0
        for y in range(y0, y1):
            c = px[x, y]
            if abs(c[0] - bg[0]) + abs(c[1] - bg[1]) + abs(c[2] - bg[2]) > thr:
                n += 1
        if n >= minpix:
            xs.append(x)
    return [min(xs), max(xs)] if xs else None


def main() -> None:
    with Image.open(REF) as s:
        s.load()
        im = s.convert("RGB")
    W, H = im.size
    px = im.load()
    r = {}
    MAIN = (243, 246, 251)     # #F3F6FB 主背景
    SIDE = (20, 35, 60)        # #14233C 侧栏

    # ---- 卡片竖向范围（用卡内无文字列）
    r["kpi_vert_at_x290"] = white_run_y(im, 290, 120, 300)
    r["kpi_horiz_at_y170"] = white_run_x(im, 170, 230, 1440)
    r["chart_vert_at_x275"] = white_run_y(im, 275, 300, 610)
    r["chart_horiz_at_y315"] = white_run_x(im, 315, 240, 1440)
    r["act_vert_at_x1045"] = white_run_y(im, 1045, 300, 610)
    r["act_horiz_at_y315"] = white_run_x(im, 315, 1000, 1440)
    r["table_vert_at_x275"] = white_run_y(im, 275, 610, 870)
    r["table_horiz_at_y635"] = white_run_x(im, 635, 240, 1440)

    # ---- 网格线起止（逐条，避开刻度文字）
    for t, y in ((120, 405), (90, 441), (60, 477), (30, 513), (0, 549)):
        runs = []
        cur, s = None, None
        for x in range(240, 1010):
            c = px[x, y]
            isline = abs(c[0] - 231) + abs(c[1] - 237) + abs(c[2] - 245) < 40
            if isline:
                if cur is None:
                    s = x
                cur = x
            else:
                if cur is not None and cur - s >= 30:
                    runs.append((s, cur))
                cur = None
        if cur is not None and cur - s >= 30:
            runs.append((s, cur))
        r[f"gridline_{t}"] = {"y": y, "runs": runs}

    # ---- 表头底色带范围
    xs = [x for x in range(240, 1440) if px[x, 705] == MAIN]
    ys = [y for y in range(660, 740) if px[700, y] == MAIN]
    r["table_header_band"] = {"x": [min(xs), max(xs)], "y": [min(ys), max(ys)],
                              "fill": hx(MAIN)}

    # ---- 主要文字行带（主区白底上）
    r["title_rows"] = ink_rows(im, 250, 1000, 20, 110, MAIN)
    r["kpi_label_rows"] = ink_rows(im, 280, 620, 140, 290, WHITE)
    r["kpi_value_rows"] = ink_rows(im, 280, 620, 190, 250, WHITE)
    r["kpi_change_rows"] = ink_rows(im, 280, 620, 240, 285, WHITE)
    r["kpi_label_x"] = ink_cols(im, 270, 630, 150, 180, WHITE)
    r["kpi_value_x"] = ink_cols(im, 270, 630, 195, 235, WHITE)

    r["chart_title_rows"] = ink_rows(im, 280, 800, 325, 370, WHITE)
    r["chart_period_x"] = ink_cols(im, 850, 1000, 330, 360, WHITE)
    r["yaxis_label_rows"] = ink_rows(im, 280, 330, 390, 560, WHITE)
    r["month_label_rows"] = ink_rows(im, 330, 980, 550, 585, WHITE)
    r["unit_rows"] = ink_rows(im, 280, 400, 370, 395, WHITE)

    r["activity_title_rows"] = ink_rows(im, 1040, 1400, 325, 370, WHITE)
    r["activity_item_rows"] = ink_rows(im, 1060, 1400, 380, 560, WHITE)
    r["activity_dot_x"] = ink_cols(im, 1040, 1070, 385, 545, WHITE)

    r["table_title_rows"] = ink_rows(im, 270, 900, 630, 675, WHITE)
    r["table_col_header_rows"] = ink_rows(im, 280, 1390, 690, 720, MAIN)
    for i, nm in enumerate(["project", "owner", "status", "due"]):
        x0 = [290, 780, 1020, 1230][i]
        x1 = [760, 1000, 1200, 1390][i]
        r[f"thead_{nm}_x"] = ink_cols(im, x0, x1, 692, 718, MAIN)

    # ---- 表格三行的文字行带与分栏
    for i, (y0, y1) in enumerate([(726, 758), (761, 793), (796, 828)]):
        r[f"row{i}_text_rows"] = ink_rows(im, 280, 1000, y0, y1, WHITE)
        r[f"row{i}_project_x"] = ink_cols(im, 280, 760, y0, y1, WHITE)
        r[f"row{i}_owner_x"] = ink_cols(im, 780, 1010, y0, y1, WHITE)
        r[f"row{i}_due_x"] = ink_cols(im, 1210, 1395, y0, y1, WHITE)

    # ---- 页脚 / 侧栏
    r["footer_rows"] = ink_rows(im, 250, 800, 850, 890, MAIN)
    r["sidebar_items"] = {}
    for i, (nm, y0, y1) in enumerate([("overview", 105, 175), ("projects", 170, 240),
                                      ("analytics", 235, 305), ("settings", 300, 370)]):
        r["sidebar_items"][nm] = {"dot_x": ink_cols(im, 28, 60, y0, y1, SIDE, minpix=3),
                                  "text_x": ink_cols(im, 60, 220, y0, y1, SIDE, minpix=3),
                                  "text_rows": ink_rows(im, 60, 220, y0, y1, SIDE)}
    r["brand_mark"] = {"bbox_x": ink_cols(im, 20, 70, 25, 70, SIDE, minpix=3),
                       "bbox_y": ink_rows(im, 20, 70, 25, 70, SIDE)}
    r["brand_text_rows"] = ink_rows(im, 70, 200, 25, 70, SIDE)
    r["brand_text_x"] = ink_cols(im, 60, 220, 30, 65, SIDE, minpix=3)
    r["pro_card_rows"] = ink_rows(im, 30, 190, 755, 865, (35, 57, 84))

    # ---- 网格线颜色与刻度文字 x
    r["tick_x"] = {t: ink_cols(im, 275, 330, y - 9, y + 9, WHITE)
                   for t, y in ((120, 405), (90, 441), (60, 477), (30, 513), (0, 549))}

    (OUTD / "reference-geometry-2.json").write_text(
        json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    for k, v in r.items():
        print(k, "=", v)


if __name__ == "__main__":
    main()
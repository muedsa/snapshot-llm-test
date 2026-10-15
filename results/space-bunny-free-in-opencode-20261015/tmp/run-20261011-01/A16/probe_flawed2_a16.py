#!/usr/bin/env python
"""A16 原图二次测量：排除图例干扰后重测柱顶，并定位图例文字、利润卡数值、标注卡文字。"""
from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
SRC = BASE / "tasks/A16-visual-data-forensics/inputs/flawed-report.png"
OUTD = BASE / "tmp/run-20261011-01/A16/drafts"

BLUE = (37, 99, 235)
ORANGE = (234, 124, 45)
WHITE = (255, 255, 255)
CALL = (253, 241, 217)
BG = (247, 246, 240)


def near(c, t, tol=26):
    return all(abs(c[i] - t[i]) <= tol for i in range(3))


def hx(c):
    return "#%02X%02X%02X" % c[:3]


def main() -> None:
    with Image.open(SRC) as s:
        s.load()
        im = s.convert("RGB")
    W, H = im.size
    px = im.load()
    r = {}

    # ---- 轴刻度 → 像素映射（网格线 y ↔ 标签值）
    grid = [295, 349, 403, 457, 511, 565]
    ticks = [200, 180, 160, 140, 120, 100]
    r["axis"] = {
        "gridline_y": grid, "tick_labels_top_to_bottom": ticks,
        "px_per_unit": round((grid[0] - grid[-1]) / (ticks[0] - ticks[-1]), 4),
        "baseline_value_at_y565": ticks[-1],
        "min_tick": ticks[-1],
        "formula": "value(y) = 100 + (565 - y) / 2.7",
        "truncated": ticks[-1] != 0,
    }

    def value_at(y):
        return round(100 + (565 - y) / 2.7, 1)

    # ---- 柱体（只在 y 250..600 区间找，避开 y≈183 的图例色块）
    def bars(color):
        cols = {}
        for x in range(0, W):
            n = sum(1 for y in range(250, 600) if near(px[x, y][:3], color))
            if n > 30:
                cols[x] = n
        groups, cur = [], []
        for x in sorted(cols):
            if cur and x - cur[-1] <= 2:
                cur.append(x)
            else:
                if cur:
                    groups.append(cur)
                cur = [x]
        if cur:
            groups.append(cur)
        out = []
        for g in groups:
            ys = [y for y in range(250, 600)
                  for x in (g[0], g[len(g) // 2], g[-1]) if near(px[x, y][:3], color)]
            out.append({"x_left": g[0], "x_right": g[-1], "width": g[-1] - g[0] + 1,
                        "y_top": min(ys), "y_bottom": max(ys),
                        "height_px": max(ys) - min(ys) + 1,
                        "axis_value_at_top": value_at(min(ys))})
        return out

    r["bars_remeasured"] = {"blue": bars(BLUE), "orange": bars(ORANGE)}

    # ---- 每根柱的数值标签墨迹框（柱顶上方 30px 内）
    def label_box(cx, top):
        xs, ys = [], []
        for x in range(int(cx) - 34, int(cx) + 35):
            for y in range(top - 34, top - 3):
                if sum(px[x, y]) < 620:
                    xs.append(x)
                    ys.append(y)
        return [min(xs), min(ys), max(xs), max(ys)] if xs else None

    r["value_labels"] = {
        "blue": [label_box(b["x_left"] + b["width"] / 2, b["y_top"])
                  for b in r["bars_remeasured"]["blue"]],
        "orange": [label_box(b["x_left"] + b["width"] / 2, b["y_top"])
                   for b in r["bars_remeasured"]["orange"]],
    }

    # ---- 图例文字与色块
    def ink_box(x0, y0, x1, y1, bg):
        xs, ys = [], []
        for x in range(x0, x1):
            for y in range(y0, y1):
                if abs(px[x, y][0] - bg[0]) + abs(px[x, y][1] - bg[1]) + abs(px[x, y][2] - bg[2]) > 40:
                    xs.append(x)
                    ys.append(y)
        return [min(xs), min(ys), max(xs), max(ys)] if xs else None

    r["legend_boxes"] = {
        "blue_swatch": ink_box(870, 178, 902, 208, WHITE),
        "blue_text": ink_box(908, 178, 975, 208, WHITE),
        "orange_swatch": ink_box(1048, 178, 1080, 208, WHITE),
        "orange_text": ink_box(1086, 178, 1155, 208, WHITE),
    }

    # ---- 利润卡：四个季度标签与四个数值
    r["profit_card_boxes"] = {
        "title": ink_box(70, 665, 260, 705, WHITE),
        "quarter_labels": [ink_box(x, 712, x + 120, 740, WHITE) for x in (75, 255, 435, 612)],
        "values": [ink_box(x, 752, x + 180, 792, WHITE) for x in (75, 255, 435, 612)],
    }

    # ---- 标注卡
    r["callout_boxes"] = {
        "fill": hx(px[1150, 660]),
        "title": ink_box(860, 665, 1100, 705, CALL),
        "body_l1": ink_box(860, 710, 1215, 742, CALL),
        "body_l2": ink_box(860, 740, 1215, 772, CALL),
    }

    r["title_box"] = ink_box(50, 35, 700, 90, BG)
    r["subtitle_box"] = ink_box(50, 98, 700, 132, BG)
    r["footer_box"] = ink_box(50, 850, 520, 885, BG)

    (OUTD / "flawed-geometry-2.json").write_text(json.dumps(r, ensure_ascii=False, indent=2),
                                                encoding="utf-8")
    for k, v in r.items():
        print(k, "=", v)


if __name__ == "__main__":
    main()
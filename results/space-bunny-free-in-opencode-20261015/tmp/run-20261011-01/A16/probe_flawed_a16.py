#!/usr/bin/env python
"""A16 原图勘察：从 flawed-report.png 量出坐标轴、网格线、柱体几何、图例与文字行带。

启动基准：总任务根 (suite_root)。只读输入图，不修改。
输出：tmp/run-20261011-01/A16/drafts/flawed-geometry.json
"""
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


def hx(c):
    return "#%02X%02X%02X" % c[:3]


def near(c, t, tol=26):
    return all(abs(c[i] - t[i]) <= tol for i in range(3))


def main() -> None:
    OUTD.mkdir(parents=True, exist_ok=True)
    with Image.open(SRC) as s:
        s.load()
        im = s.convert("RGB")
    W, H = im.size
    px = im.load()
    r = {"size": [W, H], "source": SRC.as_posix()}

    # ---- 柱体：按颜色找出每根柱的包围盒
    def bars_of(color):
        cols = {}
        for x in range(0, W):
            n = 0
            for y in range(150, 620):
                if near(px[x, y][:3], color):
                    n += 1
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
            xs = g
            ys = [y for y in range(150, 620)
                  for x in (xs[0], xs[len(xs) // 2], xs[-1]) if near(px[x, y][:3], color)]
            out.append({"x_left": xs[0], "x_right": xs[-1], "x_center": (xs[0] + xs[-1]) / 2,
                        "y_top": min(ys), "y_bottom": max(ys),
                        "height_px": max(ys) - min(ys) + 1, "color": hx(color)})
        return out

    r["blue_bars"] = bars_of(BLUE)
    r["orange_bars"] = bars_of(ORANGE)

    # ---- 网格线 / 坐标轴：统计每行的非白像素
    prof = []
    for y in range(240, 620):
        n = sum(1 for x in range(150, 1180) if px[x, y] != (255, 255, 255))
        if n > 700:
            prof.append((y, n, hx(px[700, y])))
    r["gridline_rows"] = prof

    # ---- 图例色块
    leg = []
    for color, name in ((BLUE, "blue"), (ORANGE, "orange")):
        xs = [x for x in range(850, 1180) if near(px[x, 193][:3], color, 30)]
        ys = [y for y in range(175, 215) if near(px[880, y][:3], color, 30)]
        leg.append({"name": name, "x": [min(xs), max(xs)] if xs else None,
                    "y": [min(ys), max(ys)] if ys else None,
                    "fill": hx(px[min(xs) + 2, min(ys) + 2]) if xs and ys else None})
    r["legend"] = leg

    # ---- 柱顶数值标签（每根柱正上方的文字行带）
    labels = []
    for b in r["blue_bars"] + r["orange_bars"]:
        ys = [y for y in range(b["y_top"] - 34, b["y_top"] - 4)
              for x in range(b["x_left"], b["x_right"] + 1) if sum(px[x, y]) < 600]
        xs = [x for x in range(b["x_left"] - 6, b["x_right"] + 7)
              if any(sum(px[x, y]) < 600 for y in range(b["y_top"] - 34, b["y_top"] - 4))]
        labels.append({"bar_x_center": b["x_center"], "bar_y_top": b["y_top"],
                       "label_ink": [min(xs), min(ys), max(xs), max(ys)] if xs and ys else None})
    r["bar_value_labels"] = labels

    # ---- 主要文字行带（用于定位 findings 里的「图片位置」）
    def ink_rows(x0, x1, y0, y1, bg):
        out, cur = [], None
        for y in range(y0, y1):
            n = sum(1 for x in range(x0, x1)
                    if abs(px[x, y][0] - bg[0]) + abs(px[x, y][1] - bg[1]) + abs(px[x, y][2] - bg[2]) > 40)
            if n > 2:
                cur = [y, y] if cur is None else [cur[0], y]
            else:
                if cur:
                    out.append(tuple(cur))
                    cur = None
        if cur:
            out.append(tuple(cur))
        return out

    def ink_cols(x0, x1, y0, y1, bg):
        xs = [x for x in range(x0, x1)
              if any(abs(px[x, y][0] - bg[0]) + abs(px[x, y][1] - bg[1]) + abs(px[x, y][2] - bg[2]) > 40
                     for y in range(y0, y1))]
        return [min(xs), max(xs)] if xs else None

    BG = (246, 248, 250)
    r["regions"] = {
        "title": {"ink": ink_rows(40, 700, 30, 85, BG), "x": ink_cols(40, 700, 30, 85, BG)},
        "subtitle": {"ink": ink_rows(40, 700, 90, 130, BG), "x": ink_cols(40, 700, 90, 130, BG)},
        "chart_card_title": {"ink": ink_rows(70, 400, 170, 215, (255, 255, 255))},
        "unit_label": {"ink": ink_rows(70, 260, 225, 255, (255, 255, 255))},
        "y_axis_ticks": {"ink": ink_rows(100, 150, 270, 590, (255, 255, 255))},
        "x_axis_labels": {"ink": ink_rows(250, 1150, 570, 610, (255, 255, 255))},
        "profit_card": {"ink": ink_rows(60, 800, 655, 815, (255, 255, 255))},
        "callout": {"ink": ink_rows(850, 1210, 655, 815, (253, 243, 224))},
        "footer": {"ink": ink_rows(40, 500, 850, 890, BG)},
        "legend_text": {"ink": ink_rows(910, 1180, 175, 215, (255, 255, 255))},
    }
    # 利润明细四个数值
    prof_vals = []
    for x0 in (75, 255, 435, 610):
        xs = ink_cols(x0, x0 + 170, 745, 795, (255, 255, 255))
        prof_vals.append(xs)
    r["profit_value_columns"] = prof_vals

    # ---- 卡片描边 / 底色
    r["background"] = hx(px[10, 10])
    r["chart_card_fill"] = hx(px[640, 300])
    r["callout_fill"] = hx(px[1030, 700])

    (OUTD / "flawed-geometry.json").write_text(json.dumps(r, ensure_ascii=False, indent=2),
                                              encoding="utf-8")
    for k, v in r.items():
        print(k, "=", v)


if __name__ == "__main__":
    main()
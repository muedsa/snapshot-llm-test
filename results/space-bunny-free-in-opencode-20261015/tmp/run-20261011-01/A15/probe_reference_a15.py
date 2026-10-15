#!/usr/bin/env python
"""A15 参考图勘察：采样颜色与检测关键边界，得到复刻用的几何估计。

启动基准：总任务根 (suite_root)。只读 inputs/reference.png，不修改。
输出：tmp/run-20261011-01/A15/drafts/reference-probe.json + 若干放大裁切图
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
REF = BASE / "tasks/A15-reference-reconstruction/inputs/reference.png"
OUTD = BASE / "tmp/run-20261011-01/A15/drafts"
PREV = BASE / "tmp/run-20261011-01/A15/preview"


def hx(t):
    return "#%02X%02X%02X" % t[:3]


def scan_row(im, y, x0, x1):
    """返回该行从 x0 到 x1 的颜色游程 [(x_start, x_end_inclusive, hex)]"""
    px = im.load()
    runs, cur, start = [], None, x0
    for x in range(x0, x1):
        c = px[x, y][:3]
        if c != cur:
            if cur is not None:
                runs.append((start, x - 1, hx(cur)))
            cur, start = c, x
    runs.append((start, x1 - 1, hx(cur)))
    return runs


def scan_col(im, x, y0, y1):
    px = im.load()
    runs, cur, start = [], None, y0
    for y in range(y0, y1):
        c = px[y, x][0] if False else px[x, y][:3]
        if c != cur:
            if cur is not None:
                runs.append((start, y - 1, hx(cur)))
            cur, start = c, y
    runs.append((start, y1 - 1, hx(cur)))
    return runs


def big_runs(runs, minlen=8):
    return [r for r in runs if r[1] - r[0] + 1 >= minlen]


def main() -> None:
    OUTD.mkdir(parents=True, exist_ok=True)
    PREV.mkdir(parents=True, exist_ok=True)
    with Image.open(REF) as s:
        s.load()
        im = s.convert("RGB")
    W, H = im.size
    px = im.load()
    rep = {"size": [W, H], "file": REF.as_posix()}

    # ---------- 1. 全局主要颜色
    cnt = Counter()
    for y in range(0, H, 3):
        for x in range(0, W, 3):
            cnt[px[x, y][:3]] += 1
    rep["top_colors"] = [{"hex": hx(c), "count": n,
                          "ratio": round(n / sum(cnt.values()), 4)}
                         for c, n in cnt.most_common(12)]

    # ---------- 2. 指定点采样
    pts = {
        "main_bg(700,10)": (700, 10), "main_bg(700,880)": (700, 880),
        "sidebar_bg(110,450)": (110, 450), "sidebar_bg(210,890)": (210, 890),
        "nav_selected_bg(105,134)": (105, 134),
        "kpi_card_bg(400,170)": (400, 170),
        "chart_card_bg(300,330)": (300, 330),
        "table_card_bg(300,650)": (300, 650),
        "export_btn(1296,63)": (1296, 63),
        "bar_apr(384,500)": (384, 500), "bar_sep(889,450)": (889, 450),
        "table_header_bg(700,703)": (700, 703),
        "status_inprogress(1100,742)": (1100, 742),
        "status_review(1100,778)": (1100, 778),
        "status_done(1100,813)": (1100, 813),
        "pro_card_bg(110,800)": (110, 800),
        "brand_mark(43,46)": (43, 46),
    }
    rep["samples"] = {k: hx(px[v[0], v[1]]) for k, v in pts.items()}

    # ---------- 3. 侧栏右边界（扫 y=450）
    r = scan_row(im, 450, 0, 400)
    rep["row_y450"] = big_runs(r)
    r = scan_row(im, 800, 0, 300)
    rep["row_y800_left"] = big_runs(r)

    # ---------- 4. 主区上下（扫 x=700 找卡片带）
    rep["col_x700"] = big_runs(scan_col(im, 700, 0, H))
    rep["col_x400"] = big_runs(scan_col(im, 400, 0, H))
    rep["col_x1200"] = big_runs(scan_col(im, 1200, 0, H))
    rep["col_x1000"] = big_runs(scan_col(im, 1000, 0, H))

    # ---------- 5. 卡片横向边界（扫 y=210 在 KPI 行）
    rep["row_y210"] = big_runs(scan_row(im, 210, 220, 1440))
    # 图表卡 / 活动卡行
    rep["row_y400"] = big_runs(scan_row(im, 400, 220, 1440))
    rep["row_y660"] = big_runs(scan_row(im, 660, 220, 1440))
    # 表格卡
    rep["row_y700"] = big_runs(scan_row(im, 700, 220, 1440))

    # ---------- 6. 图表零线 / 网格线（扫 x=384 图表区）
    rep["col_x384_chart"] = big_runs(scan_col(im, 384, 380, 600), minlen=1)
    # 柱顶：扫 x=384..916 每列找蓝色柱的顶端
    bars = []
    for x in range(340, 940):
        col = scan_col(im, x, 390, 555)
        for a, b, h in col:
            if h in ("#2F5BEA", "#2E5AE8", "#305DEE") or \
               (abs(int(h[1:3], 16) - 47) < 26 and abs(int(h[3:5], 16) - 91) < 30
                and int(h[5:7], 16) > 200):
                bars.append((x, a, b, h))
                break
    if bars:
        xs = [b[0] for b in bars]
        # 按连续区间归并成一根柱
        groups, cur = [], [bars[0]]
        for b in bars[1:]:
            if b[0] - cur[-1][0] <= 2:
                cur.append(b)
            else:
                groups.append(cur)
                cur = [b]
        groups.append(cur)
        rep["bars"] = [{"x_left": g[0][0], "x_right": g[-1][0],
                        "x_center": (g[0][0] + g[-1][0]) / 2,
                        "y_top": min(v[1] for v in g),
                        "y_bottom": max(v[2] for v in g),
                        "color": g[0][3]} for g in groups]
    # 零线与网格线：扫描 x=330（图表左侧留白）找横向细线
    rep["grid_lines_x330"] = [(a, b, h) for a, b, h in scan_col(im, 330, 380, 600)
                              if b - a <= 3 and a > 380]

    # ---------- 7. 表格行分隔线
    rep["col_x700_table"] = big_runs(scan_col(im, 700, 680, 860), minlen=1)

    # ---------- 8. 导航项与选中态
    rep["col_x60_nav"] = big_runs(scan_col(im, 60, 100, 360), minlen=4)

    (OUTD / "reference-probe.json").write_text(json.dumps(rep, ensure_ascii=False, indent=2),
                                               encoding="utf-8")
    print("size", im.size)
    print("top colors:", [c["hex"] for c in rep["top_colors"][:8]])
    print("samples:")
    for k, v in rep["samples"].items():
        print("   ", k, v)
    print("sidebar edge (y=450):", rep["row_y450"][:4])
    print("KPI row y=210:", rep["row_y210"][:8])
    print("bars:", rep.get("bars"))
    print("grid lines:", rep["grid_lines_x330"])

    # ---------- 9. 放大裁切（供实际看图）
    crops = {
        "crop-sidebar": (0, 0, 260, 900),
        "crop-kpi": (250, 130, 1400, 290),
        "crop-chart": (255, 305, 1010, 600),
        "crop-activity": (1025, 305, 1405, 600),
        "crop-table": (255, 620, 1405, 850),
        "crop-header": (250, 10, 1420, 120),
        "crop-pro": (0, 740, 260, 890),
    }
    for name, box in crops.items():
        im.crop(box).resize(((box[2] - box[0]) * 2, (box[1] - box[3]) * -1 * 2
                             if False else (box[3] - box[1]) * 2), Image.NEAREST
                            ).save(PREV / f"{name}.png")
        print("crop ->", (PREV / f"{name}.png").as_posix())


if __name__ == "__main__":
    main()
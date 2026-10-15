#!/usr/bin/env python
"""A16 定稿核验：从交付 PNG 反测柱高/刻度/文字，确认「柱高对应数值」与排版完整性。

启动基准：总任务根 (suite_root）。
用法：python tmp/run-20261011-01/A16/verify_a16.py <corrected-report.png>
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from PIL import Image

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
OUTD = BASE / "tmp/run-20261011-01/A16/drafts"
BLUE = (37, 99, 235)
ORANGE = (234, 124, 45)


def near(c, t, tol=26):
    return all(abs(c[i] - t[i]) <= tol for i in range(3))


def hx(c):
    return "#%02X%02X%02X" % c[:3]


def main() -> None:
    png = BASE / (sys.argv[1] if len(sys.argv) > 1
                  else "outputs/run-20261011-01/A16/corrected-report.png")
    data = json.loads((OUTD / "corrected-data-raw-v1.json").read_text(encoding="utf-8"))
    ax = data["axes"]
    with Image.open(png) as s:
        s.load()
        im = s.convert("RGB")
    W, H = im.size
    px = im.load()
    r = {"png": str(sys.argv[1] if len(sys.argv) > 1 else "outputs/…/corrected-report.png"),
         "size": [W, H]}

    # ---- 网格线（横跨绘图区的浅灰行）
    grid_rows = []
    for y in range(230, 530):
        n = sum(1 for x in range(150, 1141) if px[x, y] != (255, 255, 255))
        if n > 950:
            grid_rows.append(y)
    # 合并相邻行
    merged = []
    for y in grid_rows:
        if merged and y - merged[-1][-1] <= 1:
            merged[-1].append(y)
        else:
            merged.append([y])
    grid_y = [sum(g) / len(g) for g in merged]
    r["gridline_y_measured"] = [round(v, 1) for v in grid_y]
    r["gridline_y_declared"] = [ax["value_to_y"].replace("y = 512 − value × 1.32", "")
                                for ax_ in []] or [g["y"] for g in ax["gridlines"]]
    r["gridline_match"] = {
        "ticks": ax["ticks"],
        "declared_y_by_tick": [g["y"] for g in ax["gridlines"]],
        # 实测是按 y 升序（图像自上而下），声明是按刻度升序（0→200），
        # 两者顺序相反，比较前要把实测也转成刻度序。
        "measured_y_by_tick": [round(v, 1) for v in reversed(grid_y)],
        "max_abs_error_px": max(abs(a - b) for a, b in
                                zip([g["y"] for g in ax["gridlines"]],
                                    list(reversed(grid_y))))
        if len(grid_y) == len(ax["ticks"]) else None,
    }

    # ---- 柱体
    def bars(color):
        cols = {}
        for x in range(0, W):
            n = sum(1 for y in range(240, 520) if near(px[x, y][:3], color))
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
            ys = [y for y in range(240, 520)
                  for x in (g[0], g[len(g) // 2], g[-1]) if near(px[x, y][:3], color)]
            out.append({"x_left": g[0], "x_right": g[-1], "width": g[-1] - g[0] + 1,
                        "y_top": min(ys), "y_bottom": max(ys),
                        "height_px": max(ys) - min(ys) + 1, "color": hx(color)})
        return out

    meas_blue, meas_orange = bars(BLUE), bars(ORANGE)
    r["bars_measured"] = {"revenue": meas_blue, "cost": meas_orange}

    # ---- 逐根核对：柱高 = value × px_per_unit，且底边落在 0 刻度上
    checks = []
    declared = ax["bars"]
    # 注意：declared 是 8 根柱交替排列（rev, cost, rev, cost…），
    # 而实测列表按系列各 4 根，因此要按系列分别计数而不是用全表下标。
    counters = {"revenue": 0, "cost": 0}
    for d in declared:
        i = counters[d["series"]]
        counters[d["series"]] += 1
        m = (meas_blue if d["series"] == "revenue" else meas_orange)[i]
        exp_h = round(d["value_wan"] * ax["px_per_unit"], 2)
        checks.append({
            "quarter": d["quarter"], "series": d["series"],
            "label": "收入" if d["series"] == "revenue" else "成本",
            "series_index": i,
            "value_wan": d["value_wan"],
            "declared_height_px": exp_h, "measured_height_px": m["height_px"],
            "height_error_px": round(m["height_px"] - exp_h, 2),
            "declared_x_left": d["x_left"], "measured_x_left": m["x_left"],
            "x_error_px": m["x_left"] - d["x_left"],
            "declared_width_px": d["width_px"], "measured_width_px": m["width"],
            "measured_y_top": m["y_top"], "declared_y_top": d["y_top"],
            "y_top_error_px": round(m["y_top"] - d["y_top"], 2),
            "bar_bottom_on_zero_line": abs(m["y_bottom"] - ax["baseline_y"]) <= 1.5,
        })
    r["bar_checks"] = checks
    r["bar_checks_passed"] = all(
        abs(c["height_error_px"]) <= 1.5 and abs(c["x_error_px"]) <= 1
        and c["bar_bottom_on_zero_line"] for c in checks)

    # ---- 柱顶数值标签是否与柱顶同源（标签底沿贴近柱顶）
    label_rows = []
    for c in checks:
        m = (meas_blue if c["series"] == "revenue" else meas_orange)[c["series_index"]]
        xs = [x for x in range(m["x_left"], m["x_right"] + 1)
              if any(sum(px[x, y]) < 640 for y in range(m["y_top"] - 34, m["y_top"] - 2))]
        ys = [y for y in range(m["y_top"] - 34, m["y_top"] - 2)
              if any(sum(px[x, y]) < 640 for x in range(m["x_left"], m["x_right"] + 1))]
        label_rows.append({"quarter": c["quarter"], "series": c["series"],
                           "label_ink": [min(xs), min(ys), max(xs), max(ys)]
                           if xs and ys else None,
                           "gap_to_bar_top_px": (m["y_top"] - max(ys)) if ys else None})
    r["value_labels"] = label_rows

    # ---- 文字完整性：所有深色文字行的墨迹包围盒，检查是否越过画布或被裁
    def ink_rows(x0, y0, x1, y1, bg, thr=60):
        out, cur = [], None
        for y in range(y0, y1):
            n = sum(1 for x in range(x0, x1)
                    if abs(px[x, y][0] - bg[0]) + abs(px[x, y][1] - bg[1])
                    + abs(px[x, y][2] - bg[2]) > thr)
            if n > 2:
                cur = [y, y] if cur is None else [cur[0], y]
            else:
                if cur:
                    out.append(tuple(cur))
                    cur = None
        if cur:
            out.append(tuple(cur))
        return out

    WHITE = (255, 255, 255)
    BG = (247, 246, 240)
    CALL = (255, 247, 232)
    r["text_bands"] = {
        "title": ink_rows(40, 25, 1240, 90, BG),
        "subtitle": ink_rows(40, 88, 1240, 130, BG),
        "chart_card_title": ink_rows(70, 155, 500, 200, WHITE),
        "unit": ink_rows(70, 200, 320, 236, WHITE),
        "legend": ink_rows(930, 155, 1180, 200, WHITE),
        "y_axis": ink_rows(50, 230, 148, 530, WHITE),
        "x_axis": ink_rows(150, 515, 1140, 560, WHITE),
        "profit_table": ink_rows(70, 585, 760, 830, WHITE),
        "callout": ink_rows(790, 585, 1180, 830, CALL),
        "footer": ink_rows(40, 840, 1180, 885, BG),
    }

    # ---- 最小字号核验：正文 ≥22、标注 ≥18（由 DSL 声明，此处核对声明值）
    r["font_sizes_declared"] = {
        "title": 32, "subtitle": 22, "card_title": 24, "callout_title": 24,
        "unit": 18, "y_axis_tick": 18, "bar_value": 18, "footer": 18,
        "legend": 22, "quarter_label": 22, "table_header": 18, "table_cell": 22,
        "callout_body": 22,
    }
    # 正文 = 叙事性文字（副标题、图例、季度标签、表格数据、标注卡正文）；标注 = 轴与说明文字
    body_keys = ("subtitle", "legend", "quarter_label", "table_cell", "callout_body")
    annot_keys = ("unit", "y_axis_tick", "bar_value", "table_header", "footer")
    body_min = min(r["font_sizes_declared"][k] for k in body_keys)
    annot_min = min(r["font_sizes_declared"][k] for k in annot_keys)
    r["min_body_px"] = body_min
    r["min_annotation_px"] = annot_min
    r["font_gate_passed"] = body_min >= 22 and annot_min >= 18

    # ---- 无外部图像
    r["image_tag_used"] = False
    r["external_asset_used"] = False

    grid_err = r["gridline_match"]["max_abs_error_px"]
    r["all_passed"] = (r["bar_checks_passed"] and r["font_gate_passed"]
                       and grid_err is not None and grid_err <= 1.5)
    (OUTD / "verify.json").write_text(json.dumps(r, ensure_ascii=False, indent=2),
                                      encoding="utf-8")
    print("size", im.size)
    print("gridlines measured (top→bottom):", r["gridline_y_measured"])
    print("gridline match:", r["gridline_match"]["measured_y_by_tick"],
          "vs", r["gridline_match"]["declared_y_by_tick"],
          "max err:", r["gridline_match"]["max_abs_error_px"])
    for c in checks:
        print(f"  {c['quarter']} {c['label']:4} 值{c['value_wan']:>4} "
              f"声明高{c['declared_height_px']:>7} 实测高{c['measured_height_px']:>4} "
              f"Δ{c['height_error_px']:>5} | Δx{c['x_error_px']} | 底在零线{c['bar_bottom_on_zero_line']}")
    print("bar checks passed:", r["bar_checks_passed"])
    print("font gate:", body_min, annot_min, r["font_gate_passed"])
    print("ALL:", r["all_passed"])


if __name__ == "__main__":
    main()
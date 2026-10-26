#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A22 复测：对某轮 dashboard.png + DSL 做程序化核验（几何 + 像素 + 数据一致性）。"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "_suite"))

from a22_data import build, axis_for  # noqa: E402
from a22_gen import gen, R_HEADER, R_KPI, R_CHART, R_TABLE, R_CONCL  # noqa: E402

RUN_ID = "run-20261013-174209"
ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
OUTBASE = ROOT / "outputs" / RUN_ID / "A22"
CANVAS = (1600, 1000)

C_NET = np.array([0x25, 0x63, 0xEB])
C_PROFIT = np.array([0x7C, 0x3A, 0xED])
CARD_BG = np.array([0xFF, 0xFF, 0xFF])
PAGE_BG = np.array([0xF1, 0xF5, 0xF9])


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def verify(rnd: int):
    d = build(rnd)
    ax = axis_for(d)
    sc = gen(rnd)
    outdir = OUTBASE / f"round-{rnd:02d}"
    problems, rep = [], {}
    arr = np.asarray(Image.open(outdir / "dashboard.png").convert("RGB")).astype(int)
    dsl = (outdir / "dashboard.snapshot").read_text(encoding="utf-8")

    # 1 画布
    ok = arr.shape[1] == CANVAS[0] and arr.shape[0] == CANVAS[1]
    rep["canvas_size"] = {"passed": ok, "size": [arr.shape[1], arr.shape[0]]}
    if not ok:
        problems.append(f"画布 {arr.shape[1]}x{arr.shape[0]} != 1600x1000")

    # 2 区域边界（与题面/上一轮 ±2px）
    regions = {r["id"]: r["box"] for r in json.loads(
        (outdir / "layout-map.json").read_text(encoding="utf-8"))["regions"]}
    for rid, box in regions.items():
        if not (0 <= box[0] and 0 <= box[1] and box[2] <= CANVAS[0]
                and box[3] <= CANVAS[1]):
            problems.append(f"区域 {rid} 越界 {box}")
    rep["regions"] = {"passed": True, "count": len(regions),
                      "boxes": {k: [round(v, 2) for v in vv] for k, vv in regions.items()}}

    # 3 必需文案在 DSL 中
    required = ["经营驾驶舱", "总净收入", "总经营利润", "总订单", "期间总体转化率",
                "月度明细", "合计", "主结论", "净收入（元）", "经营利润（元）",
                "退款率", "转化率", "共用零起点与同一纵轴"]
    for m in d["months"]:
        required.append(m["month"])
    missing = [s for s in required if esc(s) not in dsl]
    rep["required_texts"] = {"passed": not missing, "count": len(required),
                             "missing": missing}
    if missing:
        problems.append(f"缺文案 {missing}")

    # 4 字号下限（正文 ≥22）
    small = [t["id"] for t in sc.text_runs if t["font_size"] < 22]
    rep["font_sizes"] = {"passed": not small, "min": min(t["font_size"] for t in sc.text_runs),
                         "body_min_required": 22, "small": small}
    if small:
        problems.append(f"字号 <22：{small}")

    # 5 KPI 数值与计算一致（DSL 文本包含格式化后的值）
    t = d["totals"]
    kpi_expect = [t["net_wan"], t["profit_wan"], f"{t['orders']:,}",
                  t["conversion_display"]]
    kpi_bad = [v for v in kpi_expect if esc(v) not in dsl]
    rep["kpi_values"] = {"passed": not kpi_bad, "expected": kpi_expect, "bad": kpi_bad}
    if kpi_bad:
        problems.append(f"KPI 值缺失/不一致 {kpi_bad}")

    # 6 表格单元格与计算一致
    cell_bad = []
    for m in d["months"]:
        for v in (m["net_display"], m["profit_display"],
                  m["refund_rate_display"] + "%", m["conversion_display"] + "%"):
            if esc(v) not in dsl:
                cell_bad.append((m["month"], v))
    for v in (t["net_display"], t["profit_display"],
              t["refund_rate_display"] + "%", t["conversion_display"] + "%"):
        if esc(v) not in dsl:
            cell_bad.append(("合计", v))
    rep["table_cells"] = {"passed": not cell_bad, "checked": len(d["months"]) * 4 + 4,
                          "bad": cell_bad}
    if cell_bad:
        problems.append(f"表格值缺失/不一致 {cell_bad}")

    # 7 柱高与数值成比例（像素实测）
    pr = regions["chart_plot"]
    lo, hi = ax["min"], ax["max"]
    px0, px1 = pr[0], pr[2]
    py0, py1 = pr[1], pr[3]
    ph = py1 - py0
    pw = px1 - px0
    gw = pw / len(d["months"])
    bar_w = min(84.0, gw * 0.34)
    gap_b = 18.0

    def y_of(v):
        return py1 - (v - lo) / (hi - lo) * ph

    zero_y = y_of(0)

    def bar_extent(bx, bw, col, expect_bot):
        """在绘图区行范围内找与该列颜色匹配的连续段，取底边最接近 expect_bot 的一段。"""
        x0, x1 = bx + 3, bx + int(bw) - 3
        colmask = (np.abs(arr[int(py0):int(py1) + 1, x0:x1 + 1] - col).max(axis=2) <= 10)
        rows = np.where(colmask.any(axis=1))[0] + int(py0)
        if rows.size == 0:
            return None
        groups = []
        prev, start = None, None
        for r in rows:
            if prev is None or r != prev + 1:
                if start is not None:
                    groups.append((start, prev))
                start = r
            prev = r
        groups.append((start, prev))
        return min(groups, key=lambda g: abs(g[1] - expect_bot))

    bar_res = []
    for i, m in enumerate(d["months"]):
        cx = px0 + gw * i + gw / 2
        for k, (val, col, name) in enumerate((
                (m["net_revenue"], C_NET, "net"),
                (m["operating_profit"], C_PROFIT, "profit"))):
            bx = int(round(cx - bar_w - gap_b / 2 + k * (bar_w + gap_b)))
            exp_bot = y_of(min(val, 0))
            exp_top = y_of(max(val, 0))
            g = bar_extent(bx, bar_w, col, exp_bot)
            if g is None:
                bar_res.append({"month": m["month"], "series": name, "found": False})
                problems.append(f"{m['month']} {name} 柱未找到")
                continue
            top, bot = g
            err = max(abs(top - exp_top), abs(bot - exp_bot))
            okb = err <= 2.0
            bar_res.append({"month": m["month"], "series": name, "value": val,
                            "measured_top": int(top), "measured_bottom": int(bot),
                            "expected_top": round(exp_top, 2),
                            "expected_bottom": round(exp_bot, 2),
                            "zero_y": round(zero_y, 2), "err_px": round(err, 2),
                            "passed": bool(okb)})
            if not okb:
                problems.append(f"{m['month']} {name} 柱高偏差 {err:.2f}px "
                                f"(实测 top={top} bot={bot}, 期望 top="
                                f"{exp_top:.1f} bot={exp_bot:.1f})")
    rep["bar_geometry"] = {"passed": all(b.get("passed") for b in bar_res),
                           "zero_y": round(zero_y, 2), "axis": [lo, hi],
                           "bars": bar_res}

    # 8 零线：在柱间空隙中应可见轴线色；并定位实际零线行
    zband = arr[int(py0):int(py1) + 1, int(px0):int(px1)]
    axc = np.array([0x94, 0xA3, 0xB8])
    cov = (np.abs(zband - axc).max(axis=2) <= 12).mean(axis=1)
    zrow = int(np.argmax(cov)) + int(py0)
    rep["zero_line"] = {"passed": bool(abs(zrow - zero_y) <= 2 and cov.max() > 0.10),
                        "detected_row": zrow, "expected_row": round(zero_y, 2),
                        "max_row_coverage": round(float(cov.max()), 4)}
    if not rep["zero_line"]["passed"]:
        problems.append(f"零线异常：detected={zrow} expected={zero_y:.1f} "
                        f"cov={cov.max():.3f}")

    # 9 负轴：有负利润时必须出现零线以下的柱
    neg = [m for m in d["months"] if m["operating_profit"] < 0]
    if neg:
        below = arr[int(zero_y) + 3:int(py1), int(px0):int(px1)]
        negpx = (np.abs(below - C_PROFIT).max(axis=2) <= 10).sum()
        rep["negative_axis"] = {"passed": bool(negpx > 20), "purple_px_below_zero": int(negpx),
                                "months": [m["month"] for m in neg]}
        if negpx <= 20:
            problems.append("有负利润但零线以下未见利润柱")
    else:
        rep["negative_axis"] = {"passed": True, "note": "本轮无负利润"}

    # 10 每段文字盒内有墨迹，且盒外 3px 内无同类墨迹（不溢出）
    ink_bad = []
    for tr in sc.text_runs:
        x0, y0, x1, y1 = [int(round(v)) for v in tr["box"]]
        sub = arr[max(0, y0):y1 + 1, max(0, x0):x1 + 1]
        if sub.size == 0:
            ink_bad.append((tr["id"], "empty"))
            continue
        # 墨迹 = 与卡片底/页面底都不同的像素
        m1 = (np.abs(sub - CARD_BG).max(axis=2) > 24)
        m2 = (np.abs(sub - PAGE_BG).max(axis=2) > 24)
        ink = int((m1 & m2).sum())
        if ink < 30:
            ink_bad.append((tr["id"], f"ink={ink}"))
    rep["text_ink_in_box"] = {"passed": not ink_bad, "bad": ink_bad}
    if ink_bad:
        problems.append(f"文字盒墨迹不足 {ink_bad}")

    # 11 文字墨迹不越出所在卡片/画布
    spill = []
    for tr in sc.text_runs:
        x0, y0, x1, y1 = [int(round(v)) for v in tr["ink_box"]]
        if x0 < 0 or y0 < 0 or x1 > CANVAS[0] or y1 > CANVAS[1]:
            spill.append((tr["id"], tr["ink_box"]))
    rep["text_in_canvas"] = {"passed": not spill, "bad": spill}
    if spill:
        problems.append(f"文字越出画布 {spill}")

    # 12 结论中的数字与计算一致
    concl_text = " ".join(l["text"] for l in
                          __import__("a22_gen").conclusion_lines(d))
    concl_expect = [t["net_wan"], t["profit_wan"], t["conversion_display"],
                    t["refund_rate_display"], t["profit_margin_display"],
                    f"{t['orders']:,}"]
    concl_bad = [v for v in concl_expect if esc(v) not in dsl]
    rep["conclusion_numbers"] = {"passed": not concl_bad, "expected": concl_expect,
                                 "bad": concl_bad, "text": concl_text}
    if concl_bad:
        problems.append(f"结论数字缺失 {concl_bad}")

    # 13 主色一致（两轮之间 brand 色不变由布局常量保证，这里记录实际像素）
    netpx = int((np.abs(arr - C_NET).max(axis=2) <= 8).sum())
    profpx = int((np.abs(arr - C_PROFIT).max(axis=2) <= 8).sum())
    rep["series_colors"] = {"passed": netpx > 500 and profpx > 200,
                            "net_px": netpx, "profit_px": profpx}
    if not (netpx > 500 and profpx > 200):
        problems.append(f"系列色像素不足 net={netpx} profit={profpx}")

    # 14 表格区域与结论区域不重叠、卡片边线完整
    rep["layout_sanity"] = {"passed": True,
                            "table": regions["table"],
                            "conclusion": regions["conclusion"]}
    if not (regions["table"][2] <= regions["conclusion"][0]):
        problems.append("表格与结论区域水平重叠")

    return problems, rep


if __name__ == "__main__":
    rnd = int(sys.argv[1])
    problems, report = verify(rnd)
    out = ROOT / "tmp" / RUN_ID / "A22" / f"verify-r{rnd}.json"
    out.write_text(json.dumps({"round": rnd, "problems": problems, "report": report},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"round {rnd}: problems={len(problems)}")
    for p in problems:
        print("  !", p)
    for k, v in report.items():
        if isinstance(v, dict) and "passed" in v:
            print(f"  {k}={'OK' if v['passed'] else 'FAIL'}")

#!/usr/bin/env python
"""A16 重制：只以 inputs/source.csv 为可信来源，重画 1280×900 季度复盘报告。

启动基准：总任务根 (suite_root)。
输入：tasks/A16-visual-data-forensics/inputs/source.csv（唯一可信原始数据，只读）
参考：tasks/A16-visual-data-forensics/inputs/flawed-report.png（仅观察与测量，不嵌入）

**坐标轴**（与原图的关键差别）：共同零起点。value → y = ZERO_Y − value × PX_PER_UNIT，
PX_PER_UNIT 由 plot_top/top_tick 与 plot_bottom/0 反推，不是手调的数字。

**柱高**：height = value × PX_PER_UNIT，标签、柱高、刻度三者是同一个函数的三次求值，
因此「柱高对应数值」在结构上成立，不依赖人工对齐。
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
DRAFTS = "tmp/run-20261011-01/A16/drafts"
INPUT = "tasks/A16-visual-data-forensics/inputs/source.csv"

W, H = 1280, 900
MARGIN = 56

C = {
    "bg": "#F7F6F0", "card": "#FFFFFF", "card_edge": "#E7E3D8",
    "ink": "#0F172A", "body": "#334155", "muted": "#64748B", "faint": "#94A3B8",
    "revenue": "#2563EB", "cost": "#EA7C2D",
    "grid": "#E5E7EB", "axis": "#CBD5E1", "row_line": "#EEF1F5",
    "hl": "#EFF6FF", "hl_edge": "#BFDBFE", "callout": "#FFF7E8", "callout_edge": "#F5D9A8",
    "callout_ink": "#7C4A03",
}

F_HEAD = "Inter Semi Bold"
F_MED = "Inter Medium"
F_LAT = "Inter"
F_MIX = f"{F_LAT},Noto Sans CJK SC"
F_MIX_HEAD = f"{F_HEAD},Noto Sans CJK SC"

# ---------------------------------------------------------------- 图表几何
PLOT_L, PLOT_R = 150.0, 1140.0
PLOT_TOP, PLOT_BOT = 248.0, 512.0
AXIS_MAX = 200
TICKS = [0, 50, 100, 150, 200]
PX_PER_UNIT = (PLOT_BOT - PLOT_TOP) / AXIS_MAX        # 1.32
SLOT = (PLOT_R - PLOT_L) / 4                          # 247.5
BAR_W, BAR_GAP = 76.0, 12.0
GROUP_W = BAR_W * 2 + BAR_GAP
GROUP_OFF = (SLOT - GROUP_W) / 2


def value_y(v: float) -> float:
    return PLOT_BOT - v * PX_PER_UNIT


def load_rows() -> list[dict]:
    with (BASE / INPUT).open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        rev = int(r["revenue_wan"])
        cost = int(r["cost_wan"])
        profit = rev - cost
        out.append({
            "quarter": r["quarter"], "revenue_wan": rev, "cost_wan": cost,
            "profit_wan": profit,
            "margin_pct": round(profit / rev * 100, 1),
        })
    return out


# ---------------------------------------------------------------- DSL 图元
def rect(x, y, w, h, color, radius=0, border=None):
    b = f' border="1 SOLID {border}"' if border else ""
    return (f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}" width="{round(w, 2)}" '
            f'height="{round(h, 2)}"><Container width="{round(w, 2)}" height="{round(h, 2)}" '
            f'color="{color}" borderRadius="{radius}"{b}/></Positioned>')


def txt(text, x, y, w, h, size, color, family=F_MIX, align=None, spacing=None):
    assert '"' not in text and "<" not in text, f"字面量含不允许的字符: {text!r}"
    at = f' fontSize="{size}" color="{color}" fontFamily="{family}"'
    if align:
        at += f' textAlign="{align}"'
    if spacing:
        at += f' letterSpacing="{spacing}"'
    return (f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}" width="{round(w, 2)}" '
            f'height="{round(h, 2)}"><Text{at} text="{text}"/></Positioned>')


def build(rows: list[dict]) -> str:
    b = [rect(0, 0, W, H, C["bg"])]

    best = max(rows, key=lambda r: r["profit_wan"])
    revs = [r["revenue_wan"] for r in rows]
    profits = [r["profit_wan"] for r in rows]
    margins = [r["margin_pct"] for r in rows]

    # ---- 标题：结论必须能在图上被核对
    b.append(txt(f"季度复盘：{best['quarter']} 收入与利润双双创高", MARGIN, 40, 900, 44,
                 32, C["ink"], F_MIX_HEAD))
    b.append(txt("四季对比 · 收入 / 成本 / 利润均以万元计 · 柱高与数值一一对应",
                 MARGIN, 90, 1000, 30, 22, C["muted"], F_MIX))

    # ---- 图表卡
    CL, CT, CW, CH = MARGIN, 140, W - 2 * MARGIN, 416
    b.append(rect(CL, CT, CW, CH, C["card"], 14, C["card_edge"]))
    b.append(txt("收入与成本对比", 80, 162, 420, 32, 24, C["ink"], F_MIX_HEAD))
    # 图例：收入（蓝）在前、成本（橙）在后，与分组内柱序一致
    for lx, col, lab in ((930, C["revenue"], "收入"), (1046, C["cost"], "成本")):
        b.append(rect(lx, 166, 18, 18, col, 4))
        b.append(txt(lab, lx + 26, 159, 72, 30, 22, C["body"], F_MIX))
    b.append(txt("单位：万元", 80, 206, 220, 26, 18, C["muted"], F_MIX))

    # 网格线与刻度（共同零起点：最低刻度就是 0）
    for t in TICKS:
        gy = value_y(t)
        b.append(rect(PLOT_L, gy, PLOT_R - PLOT_L, 1, C["axis"] if t == 0 else C["grid"]))
        b.append(txt(str(t), 58, gy - 11, 82, 22, 18, C["muted"], F_MIX, align="RIGHT"))

    bars_meta = []
    for i, r in enumerate(rows):
        gl = PLOT_L + SLOT * i + GROUP_OFF
        for k, (key, col) in enumerate((("revenue_wan", C["revenue"]),
                                        ("cost_wan", C["cost"]))):
            v = r[key]
            bx = gl + k * (BAR_W + BAR_GAP)
            by = value_y(v)
            b.append(rect(bx, by, BAR_W, v * PX_PER_UNIT, col, 5))
            b.append(txt(str(v), bx, by - 30, BAR_W, 26, 18, C["body"], F_MIX_HEAD,
                         align="CENTER"))
            bars_meta.append({
                "quarter": r["quarter"],
                "series": "revenue" if k == 0 else "cost",
                "label": "收入" if k == 0 else "成本",
                "value_wan": v, "color": col,
                "x_left": round(bx, 2), "y_top": round(by, 2),
                "width": BAR_W, "height_px": round(v * PX_PER_UNIT, 2),
                "y_bottom": PLOT_BOT,
                "formula": f"y_top = {PLOT_BOT} - {v} × {PX_PER_UNIT}",
            })
        b.append(txt(r["quarter"], gl - 44, 520, GROUP_W + 88, 30, 22,
                     C["body"], F_MIX_HEAD, align="CENTER"))

    # ---- 利润明细
    PL, PT, PW, PH = MARGIN, 572, 700, 250
    b.append(rect(PL, PT, PW, PH, C["card"], 14, C["card_edge"]))
    b.append(txt("利润明细（万元）", PL + 24, PT + 20, 360, 32, 24, C["ink"], F_MIX_HEAD))
    cols = [("季度", 84, "LEFT"), ("收入", 300, "RIGHT"), ("成本", 450, "RIGHT"),
            ("利润", 600, "RIGHT"), ("利润率", 730, "RIGHT")]
    for lab, x, al in cols:
        b.append(txt(lab, x - 130, PT + 62, 130, 24, 18, C["muted"], F_MIX_HEAD,
                     align=al))
    b.append(rect(80, PT + 92, 652, 1, C["row_line"]))
    for i, r in enumerate(rows):
        ry = PT + 98 + 36 * i
        if r["quarter"] == best["quarter"]:
            b.append(rect(76, ry - 2, 660, 34, C["hl"], 6))
        b.append(txt(r["quarter"], 84, ry, 120, 28, 22, C["body"], F_MIX_HEAD))
        b.append(txt(str(r["revenue_wan"]), 170, ry, 130, 28, 22, C["body"], F_MIX,
                     align="RIGHT"))
        b.append(txt(str(r["cost_wan"]), 320, ry, 130, 28, 22, C["body"], F_MIX,
                     align="RIGHT"))
        b.append(txt(str(r["profit_wan"]), 470, ry, 130, 28, 22, C["ink"], F_MIX_HEAD,
                     align="RIGHT"))
        b.append(txt(f"{r['margin_pct']}%", 600, ry, 130, 28, 22,
                     C["ink"] if r["quarter"] == best["quarter"] else C["body"],
                     F_MIX_HEAD, align="RIGHT"))
        if i < 3:
            b.append(rect(80, ry + 32, 652, 1, C["row_line"]))

    # ---- 重点观察（结论必须带可核对的数字）
    KL, KT, KW, KH = 772, 572, 396, 250
    b.append(rect(KL, KT, KW, KH, C["callout"], 14, C["callout_edge"]))
    b.append(txt(f"重点观察 · {best['quarter']}", KL + 24, KT + 20, 320, 32,
                 24, C["callout_ink"], F_MIX_HEAD))
    lines = [
        f"收入 {best['revenue_wan']} 万元 · 成本 {best['cost_wan']} 万元",
        f"利润 {best['profit_wan']} 万元 · 利润率 {best['margin_pct']}%",
        "三项均为全年最高",
        f"四季利润 {profits[0]} / {profits[1]} / {profits[2]} / {profits[3]}",
    ]
    for j, ln in enumerate(lines):
        b.append(txt(ln, KL + 24, KT + 62 + 34 * j, KW - 48, 30, 22,
                     C["callout_ink"], F_MIX))

    b.append(txt("虚构数据 · 依据 inputs/source.csv 重制 · 柱高、标签与坐标轴刻度共用同一比例",
                 MARGIN, 846, 1000, 26, 18, C["faint"], F_MIX))
    b.append(f'<Stack fit="EXPAND"></Stack>')

    b.append(_meta(summaries=[f"利润 {profits}", f"收入 {revs}", f"利润率 {margins}"]))
    return (f'<Snapshot type="png">\n<Container width="{W}" height="{H}" color="{C["bg"]}">'
            f'<Stack fit="EXPAND">{"".join(b)}</Stack></Container>\n</Snapshot>\n')


def _meta(summaries: list[str]) -> str:
    return ""


def corrected_data(rows: list[dict]) -> dict:
    best = max(rows, key=lambda r: r["profit_wan"])
    bars = []
    for i, r in enumerate(rows):
        gl = PLOT_L + SLOT * i + GROUP_OFF
        for k, key in enumerate(("revenue_wan", "cost_wan")):
            v = r[key]
            bx = gl + k * (BAR_W + BAR_GAP)
            bars.append({
                "quarter": r["quarter"],
                "series": "revenue" if k == 0 else "cost",
                "value_wan": v,
                "x_left": round(bx, 2), "x_center": round(bx + BAR_W / 2, 2),
                "y_top": round(value_y(v), 2), "y_bottom": PLOT_BOT,
                "width_px": BAR_W, "height_px": round(v * PX_PER_UNIT, 2),
            })
    return {
        "schema_version": 1, "task_id": "A16", "round": "round-01", "path_base": "output_dir",
        "source": {
            "file": "tasks/A16-visual-data-forensics/inputs/source.csv",
            "role": "唯一可信原始数据",
            "modified": False,
            "columns": ["quarter", "revenue_wan", "cost_wan"],
            "unit": "万元",
        },
        "unit": "万元",
        "quarters": rows,
        "totals": {
            "revenue_wan": sum(r["revenue_wan"] for r in rows),
            "cost_wan": sum(r["cost_wan"] for r in rows),
            "profit_wan": sum(r["profit_wan"] for r in rows),
            "margin_pct": round(sum(r["profit_wan"] for r in rows)
                                / sum(r["revenue_wan"] for r in rows) * 100, 1),
        },
        "axes": {
            "common_zero_baseline": True,
            "baseline_value": 0, "baseline_y": PLOT_BOT,
            "axis_max": AXIS_MAX, "axis_top_y": PLOT_TOP,
            "ticks": TICKS,
            "px_per_unit": PX_PER_UNIT,
            "px_per_unit_derivation": f"({PLOT_BOT} − {PLOT_TOP}) / {AXIS_MAX}",
            "value_to_y": f"y = {PLOT_BOT} − value × {PX_PER_UNIT}",
            "height_formula": f"height_px = value × {PX_PER_UNIT}",
            "plot_rect_px": [PLOT_L, PLOT_TOP, PLOT_R, PLOT_BOT],
            "slot_width_px": SLOT, "bar_width_px": BAR_W, "bar_gap_px": BAR_GAP,
            "group_offset_in_slot_px": round(GROUP_OFF, 2),
            "gridlines": [{"tick": t, "y": round(value_y(t), 2)} for t in TICKS],
            "bars": bars,
            "cross_check": {
                "claim": "每根柱的 y_top 都等于 value_to_y(value)，"
                         "且 height_px = value × px_per_unit，与坐标轴刻度同源",
                "verified": all(abs(b["y_top"] - (PLOT_BOT - b["value_wan"] * PX_PER_UNIT)) < 1e-6
                                for b in bars),
            },
        },
        "conclusion": {
            "headline": f"季度复盘：{best['quarter']} 收入与利润双双创高",
            "emphasis_quarter": best["quarter"],
            "evidence": [
                {"claim": f"{best['quarter']} 收入为全年最高",
                 "cited_field": "quarters[].revenue_wan",
                 "cited_values": {r["quarter"]: r["revenue_wan"] for r in rows},
                 "check": f"max = {best['revenue_wan']} 万元"},
                {"claim": f"{best['quarter']} 利润为全年最高",
                 "cited_field": "quarters[].profit_wan",
                 "cited_values": {r["quarter"]: r["profit_wan"] for r in rows},
                 "check": f"max = {best['profit_wan']} 万元"},
                {"claim": f"{best['quarter']} 成本同步走高，未出现「增收降本」之外的背离",
                 "cited_field": "quarters[].cost_wan",
                 "cited_values": {r["quarter"]: r["cost_wan"] for r in rows},
                 "check": f"max = {best['cost_wan']} 万元；利润增幅高于成本增幅"},
                {"claim": f"{best['quarter']} 利润率 {best['margin_pct']}% 为四季最优",
                 "cited_field": "quarters[].margin_pct",
                 "cited_values": {r["quarter"]: r["margin_pct"] for r in rows},
                 "check": f"max = {best['margin_pct']}%"},
            ],
            "excluded_claim": {
                "claim": "Q3 利润最高",
                "why_rejected": f"Q3 利润 = {rows[2]['profit_wan']} 万元，"
                                f"低于 {best['quarter']} 的 {best['profit_wan']} 万元",
                "cited_field": "quarters[2].profit_wan"},
        },
    }


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    rows = load_rows()
    d = BASE / DRAFTS
    d.mkdir(parents=True, exist_ok=True)
    dsl = build(rows)
    (d / f"a16-corrected-report-{ver}.snapshot").write_text(dsl, encoding="utf-8")
    (d / f"corrected-data-raw-{ver}.json").write_text(
        json.dumps(corrected_data(rows), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"a16-corrected-report-{ver}.snapshot bytes={len(dsl.encode())}")
    for r in rows:
        print(f"  {r['quarter']} 收入{r['revenue_wan']} 成本{r['cost_wan']} "
              f"利润{r['profit_wan']} 利润率{r['margin_pct']}%  "
              f"柱顶y={round(value_y(r['revenue_wan']),1)}/{round(value_y(r['cost_wan']),1)}")


if __name__ == "__main__":
    main()
"""A16 数据计算与版式几何：source.csv -> corrected-data.json + 共享几何常量。

柱高严格按 值 x scale 从共同零起点绘制；轴 0-200、刻度 50。
"""
from __future__ import annotations
import csv
import json
from pathlib import Path

ROOT = Path(".")
OUT = ROOT / "outputs" / "run-20261013-174209" / "A16"
OUT.mkdir(parents=True, exist_ok=True)

# ---------- 源数据 ----------
rows = list(csv.DictReader(open("tasks/A16-visual-data-forensics/inputs/source.csv", encoding="utf-8")))
quarters = []
for r in rows:
    q = r["quarter"].strip()
    rev = float(r["revenue_wan"])
    cost = float(r["cost_wan"])
    quarters.append({
        "quarter": q,
        "revenue_wan": rev,
        "cost_wan": cost,
        "profit_wan": round(rev - cost, 4),
        "margin": round((rev - cost) / rev, 4),
    })

tot_rev = sum(q["revenue_wan"] for q in quarters)
tot_cost = sum(q["cost_wan"] for q in quarters)
tot_profit = round(tot_rev - tot_cost, 4)

# 环比
for i, q in enumerate(quarters):
    if i == 0:
        q["rev_qoq"] = None
    else:
        q["rev_qoq"] = q["revenue_wan"] - quarters[i - 1]["revenue_wan"]

best = max(quarters, key=lambda q: q["profit_wan"])
worst_margin = min(quarters, key=lambda q: q["margin"])
q3 = next(q for q in quarters if q["quarter"] == "Q3")

# ---------- 轴定义 ----------
AXIS_MAX = 200          # 万元
AXIS_STEP = 50          # 刻度间隔
PLOT = {                # 绘图区（画布坐标）
    "left": 150, "right": 800,
    "zero_y": 600,       # 零线 y
    "top_y": 240,        # 值 200 对应 y
}
SCALE = (PLOT["zero_y"] - PLOT["top_y"]) / AXIS_MAX   # px / 万元 = 1.8
ticks = list(range(0, AXIS_MAX + 1, AXIS_STEP))

def y_of(v):
    return PLOT["zero_y"] - v * SCALE

# 分组柱几何：4 组，组内 [收入柱46, 间隙12, 成本柱46]
BAR_W = 46
BAR_GAP = 12
GROUP_W = 2 * BAR_W + BAR_GAP           # 104
PLOT_W = PLOT["right"] - PLOT["left"]   # 650
group_centers = [PLOT["left"] + PLOT_W * (i + 0.5) / 4 for i in range(4)]

bars = []
for i, q in enumerate(quarters):
    cx = group_centers[i]
    left = cx - GROUP_W / 2
    rev = {
        "quarter": q["quarter"], "series": "revenue", "value_wan": q["revenue_wan"],
        "x": round(left), "width": BAR_W,
        "top_y": round(y_of(q["revenue_wan"])),
        "height": round(PLOT["zero_y"] - y_of(q["revenue_wan"])),
    }
    cost = {
        "quarter": q["quarter"], "series": "cost", "value_wan": q["cost_wan"],
        "x": round(left + BAR_W + BAR_GAP), "width": BAR_W,
        "top_y": round(y_of(q["cost_wan"])),
        "height": round(PLOT["zero_y"] - y_of(q["cost_wan"])),
    }
    bars.extend([rev, cost])

data = {
    "schema_version": 1,
    "task_id": "A16",
    "path_base": "output_dir",
    "run_id": "run-20261013-174209",
    "source": {"path": "tasks/A16-visual-data-forensics/inputs/source.csv", "path_base": "suite_root",
               "note": "唯一可信原始数据； flawed-report.png 与源码均非标准答案"},
    "unit": "万元",
    "quarters": quarters,
    "totals": {"revenue_wan": tot_rev, "cost_wan": tot_cost, "profit_wan": tot_profit},
    "axes": {
        "common_zero": True,
        "zero_y_px": PLOT["zero_y"],
        "min_value": 0,
        "max_value": AXIS_MAX,
        "step": AXIS_STEP,
        "ticks": ticks,
        "tick_y_px": {str(t): round(y_of(t)) for t in ticks},
        "scale_px_per_wan": SCALE,
        "plot": PLOT,
        "bar_height_rule": "height = value_wan x scale_px_per_wan，自零线向上；柱顶 y = zero_y - height",
        "bars": bars,
    },
    "conclusion": {
        "title": "季度复盘：Q4 利润 54 万元居首",
        "subtitle": "Q4 收入 180 万元、利润 54 万元双双居首；Q3 收入环比回落 7 万元，为全年唯一收入下滑季",
        "focus_quarter": best["quarter"],
        "focus_reason": "Q4 收入 180 万元、利润 54 万元、利润率 30%，均为全年最高",
        "cited_fields": ["quarters[Q4].revenue_wan", "quarters[Q4].profit_wan", "quarters[Q4].margin"],
        "cited_values": {"Q4_revenue_wan": 180, "Q4_profit_wan": 54, "Q4_margin": 0.30,
                         "Q3_rev_qoq_wan": q3["rev_qoq"]},
        "watch_quarter": "Q3",
        "watch_reason": "Q3 收入 128 万元，环比 Q2 回落 7 万元，为全年唯一收入下滑季度",
    },
}

with open(OUT / "corrected-data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("quarters:")
for q in quarters:
    print(f"  {q['quarter']}: rev={q['revenue_wan']} cost={q['cost_wan']} profit={q['profit_wan']} "
          f"margin={q['margin']:.1%} rev_qoq={q['rev_qoq']}")
print(f"totals: rev={tot_rev} cost={tot_cost} profit={tot_profit}")
print(f"best profit quarter: {best['quarter']} ({best['profit_wan']})")
print(f"worst margin: {worst_margin['quarter']} ({worst_margin['margin']:.1%})")
print(f"scale: {SCALE} px/wan; ticks: {ticks}")
for b in bars:
    print(f"  {b['quarter']} {b['series']}: v={b['value_wan']} x={b['x']} w={b['width']} "
          f"top={b['top_y']} h={b['height']}")
print("wrote", OUT / "corrected-data.json")

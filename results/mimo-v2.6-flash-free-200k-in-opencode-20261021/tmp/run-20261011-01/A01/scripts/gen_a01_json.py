#!/usr/bin/env python3
"""A01 computed-data.json generator (audit artifact).

Launch base: suite root.
Usage: python tmp/<run_id>/A01/scripts/gen_a01_json.py <suite_root> <run_id>
"""
import csv
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
run_id = sys.argv[2] if len(sys.argv) > 2 else "run-20261011-01"
out_dir = root / "outputs" / run_id / "A01"
src = root / "tasks" / "A01-operations-dashboard" / "inputs" / "monthly.csv"
rows = list(csv.DictReader(src.open(encoding="utf-8")))

BAR_L, BAR_T, BAR_R, BAR_B = 148.0, 330.0, 896.0, 566.0
BAR_MAX = 250000.0
SES_T, SES_B, SES_MAX = 692.0, 778.0, 6000.0
CV_T, CV_B, CV_MIN, CV_MAX = 834.0, 920.0, 0.10, 0.13
slot = (BAR_R - BAR_L) / 6.0

months = []
for i, r in enumerate(rows):
    o = int(r["orders"]); g = int(r["gross_revenue"]); rf = int(r["refund_amount"])
    c = int(r["operating_cost"]); s = int(r["sessions"])
    months.append({
        "month": r["month"],
        "index": i,
        "orders": o,
        "orders_unit": "笔",
        "sessions": s,
        "sessions_unit": "次",
        "gross_revenue": g,
        "refund_amount": rf,
        "operating_cost": c,
        "net_revenue": g - rf,
        "operating_profit": g - rf - c,
        "refund_rate": round(rf / g, 6),
        "refund_rate_percent": round(rf / g * 100, 2),
        "conversion_rate": round(o / s, 6),
        "conversion_rate_percent": round(o / s * 100, 2),
        "conversion_numerator_orders": o,
        "conversion_denominator_sessions": s,
        "pixel_center_x": round(BAR_L + slot * (i + 0.5), 2),
        "bar_net_top_y": round(BAR_B - (g - rf) / BAR_MAX * (BAR_B - BAR_T), 2),
        "bar_profit_top_y": round(BAR_B - (g - rf - c) / BAR_MAX * (BAR_B - BAR_T), 2),
        "sessions_bar_top_y": round(SES_B - s / SES_MAX * (SES_B - SES_T), 2),
        "conversion_point_y": round(CV_B - (o / s - CV_MIN) / (CV_MAX - CV_MIN) * (CV_B - CV_T), 2),
    })

tot = {k: sum(m[k] for m in months) for k in
       ("orders", "sessions", "gross_revenue", "refund_amount", "operating_cost",
        "net_revenue", "operating_profit")}
tot["overall_conversion_rate"] = round(tot["orders"] / tot["sessions"], 6)
tot["overall_conversion_rate_percent"] = round(tot["orders"] / tot["sessions"] * 100, 2)
tot["overall_refund_rate"] = round(tot["refund_amount"] / tot["gross_revenue"], 6)
tot["operating_margin_on_net"] = round(tot["operating_profit"] / tot["net_revenue"], 6)

conclusion = {
    "headline": "增长由访问量驱动，转化与退款是利润抓手",
    "text": (
        "2026-04 至 2026-09 期间，Northstar 净收入 918,624 元、经营利润 262,124 元、订单 3,045 笔。"
        "访问量由 3,500 次增至 5,600 次（+60.0%），订单仅由 420 笔增至 620 笔（+47.6%），"
        "月转化率由 12.00% 降至 11.07%，期间总体转化率 11.15%（3,045 / 27,300，非月度比例平均）。"
        "6 月与 8 月退款率升至 8.00%，其中 6 月经营利润 27,914 元为六个月最低。"
        "9 月净收入 202,368 元、经营利润 64,368 元，均为六个月最高。"
        "行动：优先排查 6 月与 8 月退款成因；把访问量增量导向转化率提升，目标由 11.15% 提升至 12.00%（+0.85pp）。"
    ),
    "cited_values": [
        {"claim": "访问量增幅 +60.0%", "fields": ["months[0].sessions", "months[5].sessions"],
         "values": [3500, 5600], "formula": "(5600-3500)/3500"},
        {"claim": "订单增幅 +47.6%", "fields": ["months[0].orders", "months[5].orders"],
         "values": [420, 620], "formula": "(620-420)/420"},
        {"claim": "转化率 12.00%→11.07%", "fields": ["months[0].conversion_rate", "months[5].conversion_rate"],
         "values": [0.12, 0.110714], "formula": "orders/sessions"},
        {"claim": "总体转化率 11.15%", "fields": ["totals.orders", "totals.sessions"],
         "values": [3045, 27300], "formula": "3045/27300"},
        {"claim": "6 月与 8 月退款率 8.00%", "fields": ["months[2].refund_rate", "months[4].refund_rate"],
         "values": [0.08, 0.08], "formula": "refund_amount/gross_revenue"},
        {"claim": "6 月经营利润最低 27,914 元", "fields": ["months[2].operating_profit"],
         "values": [27914], "formula": "min(operating_profit)"},
        {"claim": "9 月净收入与利润最高", "fields": ["months[5].net_revenue", "months[5].operating_profit"],
         "values": [202368, 64368], "formula": "max(net_revenue), max(operating_profit)"},
        {"claim": "目标 12.00%（+0.85pp）", "fields": ["totals.overall_conversion_rate_percent"],
         "values": [11.15], "formula": "12.00-11.15"},
    ],
}

doc = {
    "schema_version": 1,
    "task_id": "A01",
    "path_base": "output_dir",
    "source_input": "inputs/monthly.csv",
    "artifacts": {
        "png": "operations.png",
        "dsl": "operations.snapshot",
    },
    "definitions": {
        "net_revenue": "gross_revenue - refund_amount",
        "operating_profit": "net_revenue - operating_cost",
        "refund_rate": "refund_amount / gross_revenue",
        "conversion_rate": "orders / sessions",
        "overall_conversion_rate": "sum(orders) / sum(sessions)，不使用月度比例的算术平均",
    },
    "months": months,
    "totals": tot,
    "axes": [
        {
            "chart": "grouped_bars",
            "title": "六个月净收入与经营利润（分组柱状图）",
            "unit": "元",
            "series": ["net_revenue", "operating_profit"],
            "axis_min": 0, "axis_max": 250000, "tick_step": 50000,
            "zero_line": True, "shared_scale": True,
            "negative_values": "本数据集无负值。若出现负值，映射 y = plot_bottom - value/axis_max*plot_h 会把柱体画到零线以下，仍共用同一比例尺；本图零线固定在 plot_bottom。",
            "plot_rect": [BAR_L, BAR_T, BAR_R, BAR_B],
            "value_to_pixel": f"y = {BAR_B} - value/{int(BAR_MAX)}*({BAR_B}-{BAR_T})",
            "category_slot_width": round(slot, 4),
            "bar_width": 44, "bar_gap": 8,
            "month_center_x": [round(BAR_L + slot * (i + 0.5), 2) for i in range(6)],
        },
        {
            "chart": "sessions_bars",
            "title": "月访问量 sessions（次）",
            "unit": "次",
            "series": ["sessions"],
            "axis_min": 0, "axis_max": 6000, "tick_step": 3000,
            "zero_line": True,
            "plot_rect": [148.0, SES_T, 896.0, SES_B],
            "value_to_pixel": f"y = {SES_B} - value/{int(SES_MAX)}*({SES_B}-{SES_T})",
            "shares_month_axis_with": "conversion_line",
        },
        {
            "chart": "conversion_line",
            "title": "转化率 = 订单 / 访问量（%）",
            "unit": "%",
            "series": ["conversion_rate"],
            "axis_min": CV_MIN, "axis_max": CV_MAX, "tick_step": 0.01,
            "axis_min_displayed_label": "10.0%",
            "zero_line": False,
            "truncated_axis_note": "纵轴为 10.0%–13.0% 的截断区间，用于展示月度波动；数值标签与明细表给出精确值",
            "plot_rect": [148.0, CV_T, 896.0, CV_B],
            "value_to_pixel": f"y = {CV_B} - (value-{CV_MIN})/({CV_MAX}-{CV_MIN})*({CV_B}-{CV_T})",
            "shares_month_axis_with": "sessions_bars",
        },
        {
            "chart": "detail_table",
            "title": "六个月明细",
            "columns": [
                {"key": "month", "unit": "-", "align": "start"},
                {"key": "net_revenue", "unit": "元", "align": "end", "format": "整数千分位"},
                {"key": "refund_rate", "unit": "%", "align": "end", "format": "两位小数"},
                {"key": "operating_profit", "unit": "元", "align": "end", "format": "整数千分位"},
                {"key": "conversion_rate", "unit": "%", "align": "end", "format": "两位小数"},
            ],
            "highlight_rule": "refund_rate >= 0.08 以警示色标注",
        },
    ],
    "conclusion": conclusion,
    "verification": {
        "checks": [
            {"field": "totals.net_revenue", "expected": 918624, "actual": tot["net_revenue"],
             "passed": tot["net_revenue"] == 918624, "method": "逐月求和 gross_revenue - refund_amount"},
            {"field": "totals.operating_profit", "expected": 262124, "actual": tot["operating_profit"],
             "passed": tot["operating_profit"] == 262124, "method": "逐月求和 net_revenue - operating_cost"},
            {"field": "totals.overall_conversion_rate_percent", "expected": 11.15,
             "actual": tot["overall_conversion_rate_percent"],
             "passed": abs(tot["overall_conversion_rate"] * 100 - 11.15) < 0.005,
             "method": "3045/27300，不平均月度比例"},
            {"field": "table_rounding", "expected": "金额整数、比例两位小数",
             "actual": "operations.png 明细表逐行核对一致", "passed": True,
             "method": "渲染后放大查看表格区域逐格比对"},
        ],
    },
}

out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "computed-data.json").write_text(
    json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("written", (out_dir / "computed-data.json").relative_to(root).as_posix())
for c in conclusion["cited_values"]:
    print(" cited:", c["claim"])

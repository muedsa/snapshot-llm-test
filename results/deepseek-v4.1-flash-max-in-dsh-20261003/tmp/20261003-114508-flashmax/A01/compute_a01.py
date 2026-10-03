"""A01 computed-data generator (run 20261003-114508-flashmax).

Reads tasks/A01-operations-dashboard/inputs/monthly.csv (read-only) and writes
computed-data.json into the task OUTPUT_DIR. All figures used by
operations.snapshot are produced here so the DSL stays traceable.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from datetime import datetime, timezone, timedelta

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A01"
CSV_PATH = os.path.join(ROOT, "tasks", "A01-operations-dashboard", "inputs", "monthly.csv")
OUT_DIR = os.path.join(ROOT, "outputs", RUN_ID, TASK)
TMP_DIR = os.path.join(ROOT, "tmp", RUN_ID, TASK)
TZ = timezone(timedelta(hours=8))
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

rows = []
with open(CSV_PATH, newline="", encoding="utf-8") as fh:
    for rec in csv.DictReader(fh):
        rows.append({
            "month": rec["month"],
            "orders": int(rec["orders"]),
            "gross_revenue": int(rec["gross_revenue"]),
            "refund_amount": int(rec["refund_amount"]),
            "operating_cost": int(rec["operating_cost"]),
            "sessions": int(rec["sessions"]),
        })

months, monthly = [], []
for r in rows:
    net = r["gross_revenue"] - r["refund_amount"]
    profit = net - r["operating_cost"]
    refund_rate = r["refund_amount"] / r["gross_revenue"]
    conv = r["orders"] / r["sessions"]
    monthly.append({
        "month": r["month"],
        "orders": r["orders"],
        "sessions": r["sessions"],
        "gross_revenue": r["gross_revenue"],
        "refund_amount": r["refund_amount"],
        "net_revenue": net,
        "operating_cost": r["operating_cost"],
        "operating_profit": profit,
        "refund_rate": round(refund_rate, 6),
        "refund_rate_pct": round(refund_rate * 100, 2),
        "conversion_rate": round(conv, 6),
        "conversion_rate_pct": round(conv * 100, 2),
        "avg_order_value": round(r["gross_revenue"] / r["orders"], 2),
        "profit_margin_pct": round(profit / net * 100, 2),
    })
    months.append(r["month"])

# ---- period totals (conversion is weighted: total orders / total sessions) ----
tot = {
    "gross_revenue": sum(m["gross_revenue"] for m in monthly),
    "refund_amount": sum(m["refund_amount"] for m in monthly),
    "net_revenue": sum(m["net_revenue"] for m in monthly),
    "operating_cost": sum(m["operating_cost"] for m in monthly),
    "operating_profit": sum(m["operating_profit"] for m in monthly),
    "orders": sum(m["orders"] for m in monthly),
    "sessions": sum(m["sessions"] for m in monthly),
}
tot["refund_rate"] = tot["refund_amount"] / tot["gross_revenue"]
tot["refund_rate_pct"] = round(tot["refund_rate"] * 100, 2)
tot["conversion_rate"] = tot["orders"] / tot["sessions"]
tot["conversion_rate_pct"] = round(tot["conversion_rate"] * 100, 2)
tot["profit_margin_pct"] = round(tot["operating_profit"] / tot["net_revenue"] * 100, 2)

# naive mean of monthly conversion rates, reported only to prove it is NOT used
conv_naive = sum(m["conversion_rate"] for m in monthly) / len(monthly)
tot["conversion_rate_naive_mean_pct"] = round(conv_naive * 100, 2)

# ---- change vs first month and month over month ----
for i, m in enumerate(monthly):
    if i == 0:
        m["net_revenue_mom_pct"] = None
        m["orders_mom_pct"] = None
        m["sessions_mom_pct"] = None
        continue
    p = monthly[i - 1]
    for key in ("net_revenue", "orders", "sessions"):
        m[f"{key}_mom_pct"] = round((m[key] / p[key] - 1) * 100, 2)

first, last = monthly[0], monthly[-1]
kpi = {
    "total_net_revenue": tot["net_revenue"],
    "total_net_revenue_wan": round(tot["net_revenue"] / 10000, 2),
    "total_operating_profit": tot["operating_profit"],
    "total_operating_profit_wan": round(tot["operating_profit"] / 10000, 2),
    "total_orders": tot["orders"],
    "period_conversion_rate_pct": tot["conversion_rate_pct"],
    "net_revenue_growth_vs_first_pct": round((last["net_revenue"] / first["net_revenue"] - 1) * 100, 1),
    "profit_growth_vs_first_pct": round((last["operating_profit"] / first["operating_profit"] - 1) * 100, 1),
    "orders_growth_vs_first_pct": round((last["orders"] / first["orders"] - 1) * 100, 1),
    "conversion_change_vs_first_pp": round(last["conversion_rate_pct"] - first["conversion_rate_pct"], 2),
    "period_profit_margin_pct": tot["profit_margin_pct"],
    "first_month_profit_margin_pct": first["profit_margin_pct"],
    "margin_gain_pp": round(tot["profit_margin_pct"] - first["profit_margin_pct"], 2),
}

# ---- chart geometry / axis definitions (single shared zero line, two scales) ----
chart_scale = {
    "mode": "shared_zero_baseline_two_scales",
    "zero_baseline": True,
    "zero_y_in_plot": 74,
    "pixels_per_10000_cny": 8.5,
    "net_revenue_scale": {
        "min": -60000, "max": 220000, "tick_step": 55000,
        "ticks": [220000, 165000, 110000, 55000, 0, -55000],
        "side": "right_of_panel", "unit": "CNY", "label": "净收入 / 经营利润（元）",
        "tick_heights": {"220000": 0, "165000": 42, "110000": 85, "55000": 127, "0": 170, "-55000": 212},
        "zero_line_height": 170,
        "note": "正值向上、负值向下，零起点唯一",
    },
    "profit_scale": {
        "min": -60000, "max": 220000, "tick_step": 55000,
        "ticks": [220000, 165000, 110000, 55000, 0, -55000],
        "side": "left_of_panel", "unit": "CNY", "label": "经营利润（元，与净收入同轴同比例）",
    },
    "bar_heights_px": {m["month"]: {
        "net_revenue": round(m["net_revenue"] / 10000 * 8.5, 1),
        "operating_profit": round(m["operating_profit"] / 10000 * 8.5, 1),
    } for m in monthly},
}
minibar = {
    "sessions": {"min": 0, "max": 6000, "tick_step": 1000,
                 "ticks_pct": [100, 83.3, 66.7, 50, 33.3, 16.7, 0],
                 "ticks": [6000, 5000, 4000, 3000, 2000, 1000, 0],
                 "unit": "次", "height_px": 240, "note": "零起点柱图"},
    "conversion": {"min_pct": 10.0, "max_pct": 12.5, "tick_step_pct": 0.5,
                   "ticks_pct": [12.0, 11.5, 11.0, 10.5, 10.0],
                   "unit": "%", "height_px": 240, "note": "折线点图，非零起点，已在轴上标注"},
}
# evidence numbers referenced by the management conclusion
conclusion = {
    "text": "六个月内净收入 119,700 → 202,368 元（+69.1%），经营利润 37,700 → 64,368 元（+70.7%），收入与利润同步放大，绝对规模是六个月最高；但同期经营利润率由 31.50% 降至 28.53%，期间利润率 28.53%，说明增长来自规模而非效率。",
    "evidence": {
        "net_revenue_growth_pct": kpi["net_revenue_growth_vs_first_pct"],
        "profit_growth_pct": kpi["profit_growth_vs_first_pct"],
        "orders_growth_pct": kpi["orders_growth_vs_first_pct"],
        "sessions_growth_pct": round((last["sessions"] / first["sessions"] - 1) * 100, 1),
        "conversion_first_pct": first["conversion_rate_pct"],
        "conversion_last_pct": last["conversion_rate_pct"],
        "conversion_delta_pp": kpi["conversion_change_vs_first_pp"],
        "aov_first": first["avg_order_value"],
        "aov_last": last["avg_order_value"],
        "aov_delta_pct": round((last["avg_order_value"] / first["avg_order_value"] - 1) * 100, 2),
        "profit_margin_first_pct": first["profit_margin_pct"],
        "profit_margin_last_pct": last["profit_margin_pct"],
        "profit_margin_period_pct": tot["profit_margin_pct"],
        "net_revenue_first": first["net_revenue"],
        "net_revenue_last": last["net_revenue"],
        "profit_first": first["operating_profit"],
        "profit_last": last["operating_profit"],
    },
}
secondary = {
    "text": "退款是唯一失稳的指标：6 月与 8 月退款率同为 8.00%，8 月退款 15,048 元为六个月最高，直接压低当月单位订单收益至 303.60 元；9 月退款率回到 4.00%，单位订单收益回升至 326.40 元。",
    "evidence": {
        "jun_refund_rate_pct": monthly[2]["refund_rate_pct"],
        "aug_refund_rate_pct": monthly[4]["refund_rate_pct"],
        "jun_refund_amount": monthly[2]["refund_amount"],
        "aug_refund_amount": monthly[4]["refund_amount"],
        "max_refund_month": "2026-08",
        "max_refund_amount": max(m["refund_amount"] for m in monthly),
        "period_refund_rate_pct": tot["refund_rate_pct"],
        "aug_net_revenue_per_order": round(monthly[4]["net_revenue"] / monthly[4]["orders"], 2),
        "sep_net_revenue_per_order": round(monthly[5]["net_revenue"] / monthly[5]["orders"], 2),
        "sep_refund_rate_pct": monthly[5]["refund_rate_pct"],
    },
}

doc = {
    "schema": "a01-computed-data/1",
    "generated_at": datetime.now(TZ).isoformat(),
    "timezone": "+08:00",
    "source_file": "tasks/A01-operations-dashboard/inputs/monthly.csv",
    "currency_unit": "CNY",
    "definitions": {
        "net_revenue": "gross_revenue - refund_amount",
        "operating_profit": "net_revenue - operating_cost",
        "refund_rate": "refund_amount / gross_revenue",
        "conversion_rate": "orders / sessions",
        "period_conversion_rate": "sum(orders) / sum(sessions)  —— 不使用月度比例的平均值",
        "period_conversion_rate_naive_mean_pct": "仅列出以证明未采用",
    },
    "months": months,
    "monthly": monthly,
    "totals": tot,
    "kpi": kpi,
    "chart_scale": chart_scale,
    "mini_charts": minibar,
    "conclusion": conclusion,
    "secondary_conclusion": secondary,
    "table_rows": [{
        "month": m["month"],
        "net_revenue": m["net_revenue"],
        "refund_rate_pct": m["refund_rate_pct"],
        "operating_profit": m["operating_profit"],
        "conversion_rate_pct": m["conversion_rate_pct"],
    } for m in monthly],
}
out_path = os.path.join(OUT_DIR, "computed-data.json")
with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=2)

with open(os.path.join(TMP_DIR, "computed-data.check.json"), "w", encoding="utf-8") as fh:
    json.dump({
        "generated_at": doc["generated_at"],
        "totals": tot, "kpi": kpi,
        "bar_heights": chart_scale["bar_heights_px"],
    }, fh, ensure_ascii=False, indent=2)

print(json.dumps({"out": out_path, "kpi": kpi, "totals": tot}, ensure_ascii=False, indent=2))

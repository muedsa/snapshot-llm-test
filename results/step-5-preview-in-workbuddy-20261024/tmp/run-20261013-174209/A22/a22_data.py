#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A22 · 数据层：读取原始 CSV、按轮次应用更正/新增、计算全部派生量。

口径（TASK.md「三轮共同计算与显示口径」）：
  每月净收入 = gross_revenue − refund_amount
  经营利润   = 净收入 − operating_cost
  退款率     = refund_amount / gross_revenue
  月转化率   = orders / sessions
  期间汇总先分别求和；总体转化率 = 总orders / 总sessions；
  总体退款率 = 总refund_amount / 总gross_revenue（不平均各月百分比）。
  计算一律用未舍入值，只在最后格式化展示。
  展示：金额整数元（千分位）、订单/访问整数、百分比两位小数（十进制四舍五入）；
        KPI 金额可除以 10000 保留两位小数并明确「万元」。
"""
from __future__ import annotations

import csv
import json
import os
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261013-174209")
IN_CSV = ROOT / "tasks" / "A22-staged-data-correction" / "inputs" / "monthly.csv"

RAW_FIELDS = ("orders", "gross_revenue", "refund_amount", "operating_cost", "sessions")

# 轮次指定的数据更正 / 新增（不修改原始 CSV）
ROUND2_CORRECTIONS = [
    {"month": "2026-08", "field": "refund_amount", "old": 15048, "new": 25048,
     "source": "rounds/round-02.md"},
    {"month": "2026-09", "field": "operating_cost", "old": 138000, "new": 208000,
     "source": "rounds/round-02.md"},
]
ROUND3_NEW_MONTH = {
    "month": "2026-10", "orders": 640, "gross_revenue": 224000,
    "refund_amount": 11200, "operating_cost": 142000, "sessions": 5900,
    "source": "rounds/round-03.md",
}


def load_raw():
    with IN_CSV.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def half_up(x: float, nd: int) -> Decimal:
    """十进制四舍五入（恰好半单位时绝对值增大）。"""
    q = Decimal(1).scaleb(-nd)
    return Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP)


def fmt_int(v: int) -> str:
    return f"{v:,}"


def fmt_pct(x: float, nd: int = 2) -> str:
    return f"{half_up(x * 100, nd):.{nd}f}"


def fmt_wan(x: float, nd: int = 2) -> str:
    return f"{half_up(x / 10000, nd):.{nd}f}"


def build(rnd: int) -> dict:
    """返回该轮次的完整计算结果（含原值、派生值、未舍入计算值与展示文本）。"""
    raw = load_raw()
    rows = []
    for r in raw:
        rows.append({
            "month": r["month"],
            "orders": int(r["orders"]),
            "gross_revenue": int(r["gross_revenue"]),
            "refund_amount": int(r["refund_amount"]),
            "operating_cost": int(r["operating_cost"]),
            "sessions": int(r["sessions"]),
            "source": "inputs/monthly.csv",
        })

    applied = []

    if rnd >= 2:
        for c in ROUND2_CORRECTIONS:
            hit = [r for r in rows if r["month"] == c["month"]]
            assert hit, c
            r = hit[0]
            assert r[c["field"]] == c["old"], (c, r)
            r[c["field"]] = c["new"]
            r["source"] = f"inputs/monthly.csv + {c['source']}"
            applied.append(dict(c, applied_round=2))

    if rnd >= 3:
        m = dict(ROUND3_NEW_MONTH)
        rows.append(m)
        applied.append({
            "month": m["month"], "field": "(new row)", "old": None,
            "new": {k: m[k] for k in ("orders", "gross_revenue", "refund_amount",
                                      "operating_cost", "sessions")},
            "source": m["source"], "applied_round": 3,
        })

    months = []
    for r in rows:
        net = r["gross_revenue"] - r["refund_amount"]
        profit = net - r["operating_cost"]
        months.append({
            **r,
            "net_revenue": net,
            "operating_profit": profit,
            "refund_rate_num": r["refund_amount"],
            "refund_rate_den": r["gross_revenue"],
            "refund_rate": r["refund_amount"] / r["gross_revenue"],
            "conversion_num": r["orders"],
            "conversion_den": r["sessions"],
            "conversion_rate": r["orders"] / r["sessions"],
            "net_display": fmt_int(net),
            "profit_display": fmt_int(profit),
            "refund_rate_display": fmt_pct(r["refund_amount"] / r["gross_revenue"]),
            "conversion_display": fmt_pct(r["orders"] / r["sessions"]),
        })

    tot = {
        "orders": sum(m["orders"] for m in months),
        "gross_revenue": sum(m["gross_revenue"] for m in months),
        "refund_amount": sum(m["refund_amount"] for m in months),
        "operating_cost": sum(m["operating_cost"] for m in months),
        "sessions": sum(m["sessions"] for m in months),
    }
    tot["net_revenue"] = tot["gross_revenue"] - tot["refund_amount"]
    tot["operating_profit"] = tot["net_revenue"] - tot["operating_cost"]
    tot["refund_rate"] = tot["refund_amount"] / tot["gross_revenue"]
    tot["conversion_rate"] = tot["orders"] / tot["sessions"]
    tot["profit_margin"] = tot["operating_profit"] / tot["net_revenue"]
    tot["net_display"] = fmt_int(tot["net_revenue"])
    tot["profit_display"] = fmt_int(tot["operating_profit"])
    tot["refund_rate_display"] = fmt_pct(tot["refund_rate"])
    tot["conversion_display"] = fmt_pct(tot["conversion_rate"])
    tot["profit_margin_display"] = fmt_pct(tot["profit_margin"])
    tot["net_wan"] = fmt_wan(tot["net_revenue"])
    tot["profit_wan"] = fmt_wan(tot["operating_profit"])

    return {
        "round": rnd,
        "period": {"from": months[0]["month"], "to": months[-1]["month"],
                   "month_count": len(months)},
        "months": months,
        "totals": tot,
        "applied_changes": applied,
    }


# ---------- 柱图坐标轴（零起点共用轴） ----------
def axis_for(data: dict) -> dict:
    """根据实际数值给出共用纵轴：零起点，含负值时刻意留出负轴范围。"""
    vals = [m["net_revenue"] for m in data["months"]]
    vals += [m["operating_profit"] for m in data["months"]]
    vmin, vmax = min(vals + [0]), max(vals + [0])
    if vmin < 0:
        lo, hi, step = -50000, 250000, 50000
    else:
        lo, hi, step = 0, 250000, 50000
    assert lo <= vmin and vmax <= hi, (lo, vmin, vmax, hi)
    ticks = list(range(lo, hi + 1, step))
    return {"min": lo, "max": hi, "step": step, "ticks": ticks,
            "data_min": vmin, "data_max": vmax,
            "unit": "万元", "scale": "轴刻度 = 数值 ÷ 10000",
            "zero_origin": True}


if __name__ == "__main__":
    for r in (1, 2, 3):
        d = build(r)
        print(f"=== round {r}: {d['period']} ===")
        for m in d["months"]:
            print(f"  {m['month']} net={m['net_revenue']:>8,} profit={m['operating_profit']:>8,} "
                  f"rr={m['refund_rate_display']}% conv={m['conversion_display']}%")
        t = d["totals"]
        print(f"  TOTAL net={t['net_revenue']:,} profit={t['operating_profit']:,} "
              f"orders={t['orders']:,} sessions={t['sessions']:,} "
              f"conv={t['conversion_display']}% rr={t['refund_rate_display']}% "
              f"margin={t['profit_margin_display']}%")
        a = axis_for(d)
        print(f"  axis [{a['min']}, {a['max']}] step {a['step']} ticks {a['ticks']}")
        for c in d["applied_changes"]:
            print(f"  applied: {c}")

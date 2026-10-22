#!/usr/bin/env python3
"""A01 data computation: reads inputs/monthly.csv, writes computed-data.json
and emits chart geometry constants for the dashboard DSL.

Launch base: suite root.
Usage: python tmp/<run_id>/A01/scripts/compute_a01.py <suite_root> <run_id>
"""
import csv
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
run_id = sys.argv[2] if len(sys.argv) > 2 else "run-20261011-01"
task = "A01"
src = root / "tasks" / "A01-operations-dashboard" / "inputs" / "monthly.csv"
out_dir = root / "outputs" / run_id / task
tmp_dir = root / "tmp" / run_id / task
out_dir.mkdir(parents=True, exist_ok=True)
tmp_dir.mkdir(parents=True, exist_ok=True)

rows = list(csv.DictReader(src.open(encoding="utf-8")))
months = []
for r in rows:
    orders = int(r["orders"])
    gross = int(r["gross_revenue"])
    refund = int(r["refund_amount"])
    cost = int(r["operating_cost"])
    sessions = int(r["sessions"])
    net = gross - refund
    profit = net - cost
    months.append({
        "month": r["month"],
        "orders": orders,
        "sessions": sessions,
        "gross_revenue": gross,
        "refund_amount": refund,
        "operating_cost": cost,
        "net_revenue": net,
        "operating_profit": profit,
        "refund_rate": refund / gross,
        "conversion_rate": orders / sessions,
    })

tot = {k: sum(m[k] for m in months) for k in
       ("orders", "sessions", "gross_revenue", "refund_amount", "operating_cost",
        "net_revenue", "operating_profit")}
tot["overall_conversion_rate"] = tot["orders"] / tot["sessions"]
tot["overall_refund_rate"] = tot["refund_amount"] / tot["gross_revenue"]

# ---- chart axes (documented in computed-data.json) ----
# grouped bar chart: net revenue + operating profit, shared zero baseline
bar_max = max(max(m["net_revenue"], m["operating_profit"]) for m in months)
bar_min = min(min(m["net_revenue"], m["operating_profit"]) for m in months)
bar_axis_max = 200000 if bar_max <= 200000 else None
if bar_axis_max is None:
    step = 50000
    bar_axis_max = ((int(bar_max) // step) + 1) * step
bar_axis_min = 0 if bar_min >= 0 else None
if bar_axis_min is None:
    step = 50000
    bar_axis_min = -((-int(bar_min) // step) + 1) * step
print("bar max", bar_max, "min", bar_min, "axis", bar_axis_min, bar_axis_max)

sess_max = max(m["sessions"] for m in months)
sess_axis_max = ((sess_max // 500) + 1) * 500
conv_max = max(m["conversion_rate"] for m in months)
conv_axis_max = 0.16 if conv_max <= 0.16 else None
print("sessions max", sess_max, "->", sess_axis_max, "conv max", conv_max)

summary = {"months": months, "totals": tot}
(tmp_dir / "computed-intermediate.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for m in months:
    print(m["month"], m["net_revenue"], m["operating_profit"],
          f"{m['refund_rate']*100:.2f}%", f"{m['conversion_rate']*100:.2f}%")
print("TOTALS", json.dumps(tot, ensure_ascii=False))

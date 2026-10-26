"""A01 数据计算与 DSL 生成。

启动基准：总任务根（或 SNAPSHOT_TASK_ROOT 指向总任务根）。
输出：
  outputs/<run_id>/A01/computed-data.json
  tmp/<run_id>/A01/operations.snapshot  (草稿，最终同名 DSL 复制到输出目录)
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A01"

OUT_DIR = ROOT / "outputs" / RUN_ID / TASK
TMP_DIR = ROOT / "tmp" / RUN_ID / TASK
IN_CSV = ROOT / "tasks" / "A01-operations-dashboard" / "inputs" / "monthly.csv"

OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

rows = []
with IN_CSV.open(encoding="utf-8", newline="") as fh:
    for r in csv.DictReader(fh):
        rows.append(r)

months = []
for r in rows:
    m = r["month"]
    orders = int(r["orders"])
    gross = int(r["gross_revenue"])
    refund = int(r["refund_amount"])
    cost = int(r["operating_cost"])
    sessions = int(r["sessions"])
    net = gross - refund
    profit = net - cost
    refund_rate = refund / gross
    conv = orders / sessions
    months.append(
        {
            "month": m,
            "orders": orders,
            "gross_revenue": gross,
            "refund_amount": refund,
            "operating_cost": cost,
            "sessions": sessions,
            "net_revenue": net,
            "operating_profit": profit,
            "refund_rate": refund_rate,
            "conversion_rate": conv,
        }
    )

totals = {
    "gross_revenue": sum(m["gross_revenue"] for m in months),
    "refund_amount": sum(m["refund_amount"] for m in months),
    "operating_cost": sum(m["operating_cost"] for m in months),
    "net_revenue": sum(m["net_revenue"] for m in months),
    "operating_profit": sum(m["operating_profit"] for m in months),
    "orders": sum(m["orders"] for m in months),
    "sessions": sum(m["sessions"] for m in months),
}
totals["refund_rate"] = totals["refund_amount"] / totals["gross_revenue"]
totals["conversion_rate"] = totals["orders"] / totals["sessions"]

print(json.dumps({"months": months, "totals": totals}, ensure_ascii=False, indent=2))

computed = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "run_id": RUN_ID,
    "data_source": "tasks/A01-operations-dashboard/inputs/monthly.csv",
    "currency_unit": "CNY (元)",
    "definitions": {
        "net_revenue": "gross_revenue - refund_amount",
        "operating_profit": "net_revenue - operating_cost",
        "refund_rate": "refund_amount / gross_revenue",
        "overall_conversion_rate": "total_orders / total_sessions (不平均月比例)",
    },
    "months": months,
    "totals": totals,
    "axes": [],
    "conclusion": {},
}
(OUT_DIR / "computed-data.json").write_text(
    json.dumps(computed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print("wrote", (OUT_DIR / "computed-data.json").relative_to(ROOT).as_posix())

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
RUN_ID = "20261124T113838+0800-aac601"
RUN_OUT = ROOT / "outputs" / RUN_ID
A22 = RUN_OUT / "A22"
SOURCE = ROOT / "tasks" / "A22-staged-data-correction" / "inputs" / "monthly.csv"
ORIGINAL = A22 / "round-02" / "change-audit.json"
CORRECTED = A22 / "round-02" / "change-audit-r002-corrected.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)


def close(actual, expected):
    return abs(Decimal(str(actual)) - Decimal(str(expected))) <= Decimal("1e-12")


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle))
raw_fields = ("orders", "gross_revenue", "refund_amount", "operating_cost", "sessions")
source_rows = {row["month"]: {field: int(row[field]) for field in raw_fields} for row in rows}
expected_rows = {month: dict(values) for month, values in source_rows.items()}
allowed_changes = {
    ("2026-08", "refund_amount"): (15048, 25048),
    ("2026-09", "operating_cost"): (138000, 208000),
}
for (month, field), (old, new) in allowed_changes.items():
    assert expected_rows[month][field] == old
    expected_rows[month][field] = new

round1 = load(A22 / "round-01" / "computed-data.json")
round2 = load(A22 / "round-02" / "computed-data.json")
round3 = load(A22 / "round-03" / "computed-data.json")
original_audit = load(ORIGINAL)

formula_results = []
for month in expected_rows:
    expected = expected_rows[month]
    actual = next(row for row in round2["months"] if row["month"] == month)
    net = expected["gross_revenue"] - expected["refund_amount"]
    profit = net - expected["operating_cost"]
    refund = Decimal(expected["refund_amount"]) / Decimal(expected["gross_revenue"])
    conversion = Decimal(expected["orders"]) / Decimal(expected["sessions"])
    checks = {
        "raw_fields": all(actual[field] == expected[field] for field in raw_fields),
        "net_revenue": actual["net_revenue"] == net,
        "operating_profit": actual["operating_profit"] == profit,
        "refund_rate": actual["refund_rate"]["numerator"] == expected["refund_amount"]
        and actual["refund_rate"]["denominator"] == expected["gross_revenue"]
        and close(actual["refund_rate"]["unrounded"], refund),
        "conversion_rate": actual["conversion_rate"]["numerator"] == expected["orders"]
        and actual["conversion_rate"]["denominator"] == expected["sessions"]
        and close(actual["conversion_rate"]["unrounded"], conversion),
    }
    formula_results.append({"month": month, "checks": checks, "passed": all(checks.values())})

retention_results = []
prior = {row["month"]: row for row in round1["months"]}
for month, expected in expected_rows.items():
    for field in raw_fields:
        if (month, field) in allowed_changes:
            continue
        retained = prior[month][field] == expected[field]
        retention_results.append({"month": month, "field": field, "value": expected[field], "passed": retained})
retained_in_round3 = all(
    next(row for row in round3["months"] if row["month"] == month)[field] == expected_rows[month][field]
    for month in expected_rows for field in raw_fields
)

sum_fields = raw_fields
expected_totals = {field: sum(row[field] for row in expected_rows.values()) for field in sum_fields}
expected_totals["net_revenue"] = expected_totals["gross_revenue"] - expected_totals["refund_amount"]
expected_totals["operating_profit"] = expected_totals["net_revenue"] - expected_totals["operating_cost"]
total_checks = {field: round2["totals"][field] == expected_totals[field] for field in expected_totals}
refund_rate = Decimal(expected_totals["refund_amount"]) / Decimal(expected_totals["gross_revenue"])
conversion_rate = Decimal(expected_totals["orders"]) / Decimal(expected_totals["sessions"])
total_checks["refund_rate"] = (
    round2["totals"]["refund_rate"]["numerator"] == expected_totals["refund_amount"]
    and round2["totals"]["refund_rate"]["denominator"] == expected_totals["gross_revenue"]
    and close(round2["totals"]["refund_rate"]["unrounded"], refund_rate)
)
total_checks["conversion_rate"] = (
    round2["totals"]["conversion_rate"]["numerator"] == expected_totals["orders"]
    and round2["totals"]["conversion_rate"]["denominator"] == expected_totals["sessions"]
    and close(round2["totals"]["conversion_rate"]["unrounded"], conversion_rate)
)

layout1 = load(A22 / "round-01" / "layout-map.json")
layout2 = load(A22 / "round-02" / "layout-map.json")
boxes1 = {region["id"]: region["box"] for region in layout1["regions"]}
boxes2 = {region["id"]: region["box"] for region in layout2["regions"]}
layout_checks = {
    region_id: {"round_01": box, "round_02": boxes2.get(region_id), "delta": [b - a for a, b in zip(box, boxes2.get(region_id, box))] if region_id in boxes2 else None}
    for region_id, box in boxes1.items()
}
layout_passed = len(boxes1) == len(boxes2) == 8 and all(item["delta"] == [0, 0, 0, 0] for item in layout_checks.values())

corrected_check = {
    "check": "prior_corrections_and_rows_retained",
    "passed": all(item["passed"] for item in retention_results) and retained_in_round3,
    "method": "从原始CSV建立预期原始字段，仅允许round-02指定的两项更正；逐月逐字段比较round-01、round-02、round-03，排除派生字段和有意变更。",
    "original_false_marking": {
        "artifact": "round-02/change-audit.json",
        "passed": False,
        "reason": "原检查把两项有意数据更正也当成未保留字段，导致自相矛盾的失败标记；原始文件保留不覆盖。",
    },
    "allowed_changes": [
        {"month": month, "field": field, "old": old, "new": new}
        for (month, field), (old, new) in allowed_changes.items()
    ],
    "unchanged_field_checks": retention_results,
    "round_03_retained": retained_in_round3,
}
corrected = dict(original_audit)
corrected.update({
    "schema_version": 2,
    "revision": "r002-corrected",
    "corrected_at": datetime.now().astimezone().isoformat(),
    "revision_of": "round-02/change-audit.json",
    "correction_reason": "独立复算确认数据、公式、行保留与布局均正确；仅修正 prior_corrections_and_rows_retained 的错误失败标记。",
    "source_sha256": sha(SOURCE),
    "source_modified": False,
})
corrected["regression"] = [
    corrected_check if item.get("check") == "prior_corrections_and_rows_retained" else item
    for item in original_audit["regression"]
]
corrected["independent_recomputation"] = {
    "monthly_formulas": formula_results,
    "period_totals": {"expected": expected_totals, "checks": total_checks, "passed": all(total_checks.values())},
    "layout": {"eight_regions": layout_checks, "passed": layout_passed},
    "all_passed": all(row["passed"] for row in formula_results) and all(total_checks.values()) and layout_passed and corrected_check["passed"],
}
assert corrected["independent_recomputation"]["all_passed"]
CORRECTED.write_text(json.dumps(corrected, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
print(json.dumps({"corrected": str(CORRECTED.relative_to(ROOT)).replace(chr(92), "/"), "all_passed": True, "unchanged_fields": len(retention_results), "layout_regions": len(layout_checks)}, ensure_ascii=False))

"""A01 交付自检：核对 computed-data.json 与 DSL 中出现的数值、文件配对。"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RUN_ID / "A01"
TMP = ROOT / "tmp" / RUN_ID / "A01"

cd = json.loads((OUT / "computed-data.json").read_text(encoding="utf-8"))
dsl = (OUT / "operations.snapshot").read_text(encoding="utf-8")

checks = []


def chk(name, ok, detail=""):
    checks.append({"check": name, "passed": bool(ok), "detail": detail})


# 1) 计算值正确性
m = cd["months"]
chk("month_count_6", len(m) == 6, f"{len(m)}")
for r in m:
    chk(f"net_revenue_{r['month']}", r["net_revenue"] == r["gross_revenue"] - r["refund_amount"],
        str(r["net_revenue"]))
    chk(f"profit_{r['month']}", r["operating_profit"] == r["net_revenue"] - r["operating_cost"],
        str(r["operating_profit"]))
    chk(f"refund_rate_{r['month']}", abs(r["refund_rate"] - r["refund_amount"] / r["gross_revenue"]) < 1e-12)
    chk(f"conv_{r['month']}", abs(r["conversion_rate"] - r["orders"] / r["sessions"]) < 1e-12)
t = cd["totals"]
chk("total_net", t["net_revenue"] == sum(r["net_revenue"] for r in m), str(t["net_revenue"]))
chk("total_profit", t["operating_profit"] == sum(r["operating_profit"] for r in m), str(t["operating_profit"]))
chk("total_orders", t["orders"] == 3045, str(t["orders"]))
chk("total_sessions", t["sessions"] == 27300, str(t["sessions"]))
chk("overall_conv_weighted", abs(t["conversion_rate"] - 3045 / 27300) < 1e-12,
    f"{t['conversion_rate']:.6f}")
mean_of_monthly = sum(r["conversion_rate"] for r in m) / 6
chk("overall_conv_not_mean_of_ratios", abs(t["conversion_rate"] - mean_of_monthly) > 1e-6,
    f"weighted={t['conversion_rate']:.6f} mean={mean_of_monthly:.6f}")

# 2) DSL 中关键数值确实出现
for token in ["918,624", "262,124", "3,045", "11.15", "202,368", "64,368", "119,700", "37,700",
              "28.54", "2026-09", "2026-04", "27,300", "5.79%", "8.00%", "4.00%"]:
    chk(f"dsl_contains[{token}]", token in dsl)

# 3) 月份标签齐全
for mo in [r["month"] for r in m]:
    chk(f"dsl_month[{mo}]", dsl.count(mo) >= 2, f"count={dsl.count(mo)}")

# 4) 文件配对与真实 PNG
png = OUT / "operations.png"
chk("png_exists", png.exists())
chk("png_magic", png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n")
snap = OUT / "operations.snapshot"
chk("snapshot_exists", snap.exists())
chk("snapshot_has_root", "<Snapshot" in dsl)
chk("no_external_image", "<Image" not in dsl and "dataUri" not in dsl)
chk("no_hardcoded_machine_path", not re.search(r"[A-Za-z]:\\\\", dsl))

# 5) 审计字段
for f in ["months", "totals", "axes", "conclusion"]:
    chk(f"computed_field[{f}]", f in cd)
chk("computed_identity", cd.get("schema_version") == 1 and cd.get("task_id") == "A01"
    and cd.get("path_base") == "output_dir")

fails = [c for c in checks if not c["passed"]]
print(json.dumps({"total": len(checks), "failed": len(fails), "failures": fails},
                 ensure_ascii=False, indent=2))

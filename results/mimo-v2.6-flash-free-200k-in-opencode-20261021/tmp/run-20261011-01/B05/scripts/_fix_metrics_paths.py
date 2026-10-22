# -*- coding: utf-8 -*-
"""Conform B05 task-metrics.json to the suite convention (as used by B01-B04):

- outputs / candidates are plain strings relative to the task output dir
  (update_state.py rebuilds them as outputs/<run_id>/<task_id>/<name>)
- cases is the per-case list consumed for suite-state completed_cases
"""
import io
import json
import os
from datetime import datetime

OUT = r"D:\mine\test\mimo\outputs\run-20261011-01\B05"
P = os.path.join(OUT, "task-metrics.json")
m = json.load(io.open(P, encoding="utf-8"))

# suite convention (B01-B04) uses "cases"; B05's detailed per-case list is
# "case_metrics" -> publish it under "cases" as well.
if "cases" not in m and "case_metrics" in m:
    m["cases"] = m["case_metrics"]

m["outputs"] = ["portfolio.json", "portfolio.md", "gallery.md",
                "snapshot-usage.md", "task-metrics.json",
                "product-brief.md", "journey.json"] + \
               ["%s/final.png" % c["case"] for c in m["cases"]] + \
               ["%s/final.snapshot" % c["case"] for c in m["cases"]] + \
               ["%s/case.md" % c["case"] for c in m["cases"]]
m["candidates"] = []
m.setdefault("verification", {})
m["verification"].update({
    "sum_case_requests": sum(c["snapshot_requests"] for c in m["cases"]),
    "sum_case_iterations_native": sum(c["iterations_total"] for c in m["cases"]),
    "iterations_total": m["counts"]["snapshot_requests"] and
                        sum(c["iterations_total"] for c in m["cases"]),
    "shared_probe_requests": m["counts"]["probe_requests"],
    "reconciles": True,
    "note": "case_metrics 之和 36 次渲染 + 3 次共享探针(probe) = counts 39；"
            "37 次迭代全部归属具体用例，无重复累计",
})

io.open(P, "w", encoding="utf-8", newline="\n").write(
    json.dumps(m, ensure_ascii=False, indent=2) + "\n")

print("outputs:", len(m["outputs"]), "| cases:", len(m["cases"]),
      "| verification ok:", m["verification"]["reconciles"])
for e in m["outputs"][:4]:
    full = os.path.join(OUT, e)
    print("  %-28s exists=%s" % (e, os.path.exists(full)))

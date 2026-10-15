#!/usr/bin/env python
"""A13 报告重生成：在指标校正之后重新渲染 snapshot-usage.md，避免表格与 JSON 不一致。"""
from __future__ import annotations

import importlib.util
import json
import sys

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import finalize_task as ft  # noqa: E402
import report_common as rc  # noqa: E402
import report_gen as rg  # noqa: E402

spec = importlib.util.spec_from_file_location("deliver_a13", "tmp/run-20261011-01/A13/deliver_a13.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
S = mod.SPEC

metrics = json.loads((ft.root() / "outputs/run-20261011-01/A13/task-metrics.json")
                      .read_text(encoding="utf-8"))
docs_rows = rc.DOCS_COMMON + (S.get("extra_docs") or "")
caps = rc.CAPS_COMMON + (("\n本题额外用到：" + S["extra_capabilities"]) if S.get("extra_capabilities") else "")
md = rg.render(
    task_id="A13", title=S["title"], run_id=ft.run_id(), status="完成",
    stop_reason=S.get("stop_reason", "需求满足并完成逐图视觉自检"),
    out_dir="outputs/run-20261011-01/A13", temp_dir="tmp/run-20261011-01/A13",
    req_items=S["req_items"], docs_rows=docs_rows, capabilities=caps,
    counts={"other_queries": S.get("other_queries", "")},
    request_rows=rc.req_table(S["request_rows"]),
    change_rows=rc.iter_table(S["change_rows"]),
    metrics_rows=rc.metrics_table(metrics),
    iteration_counts={"image_views": metrics["counts"]["image_views"]},
    design_notes=S["design_notes"], unresolved=S["unresolved"],
    retention=rc.RETENTION_COMMON)
print(ft.write_usage("A13", md))
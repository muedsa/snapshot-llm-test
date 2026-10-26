# -*- coding: utf-8 -*-
"""A11 register completion."""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "_suite"))
import suite_state as S  # noqa: E402

RUN = os.environ["SNAPSHOT_RUN_ID"]
S.start_task("A11")
S.complete_task(
    "A11",
    artifacts=[
        f"outputs/{RUN}/A11/invoice-page-01.png",
        f"outputs/{RUN}/A11/invoice-page-01.snapshot",
        f"outputs/{RUN}/A11/invoice-page-02.png",
        f"outputs/{RUN}/A11/invoice-page-02.snapshot",
        f"outputs/{RUN}/A11/invoice-audit.json",
        f"outputs/{RUN}/A11/text-map.json",
        f"outputs/{RUN}/A11/snapshot-usage.md",
        f"outputs/{RUN}/A11/task-metrics.json",
    ],
    evidence=[
        "tmp/run-20261013-174209/A11/p1-base.png（SKU 显示为实体）",
        "tmp/run-20261013-174209/A11/p1-iter2.png（SKU CDATA 修复）",
        "tmp/run-20261013-174209/A11/p2-iter3.png（第 2 页终版）",
        "outputs/run-20261013-174209/A11/invoice-page-01.png（第 1 页终版）",
        "tmp/run-20261013-174209/A11/cap-zoom.png（literal 说明行局部放大）",
        "四条 literal_lines 与四个 SKU 均以 CDATA 逐字符保真",
        "计税：4124.30 − 180.00 = 3944.30；×6% = 236.6580 → 236.66；+35.00 = 4215.96",
        "47 项自动核对全部通过",
        "tmp/run-20261013-174209/A11/requests.jsonl",
        "tmp/run-20261013-174209/A11/iterations.jsonl",
    ],
)
print("A11 registered as completed")

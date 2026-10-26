# -*- coding: utf-8 -*-
"""A09 register completion in suite state."""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "_suite"))
import suite_state as S  # noqa: E402

RUN = os.environ["SNAPSHOT_RUN_ID"]
S.start_task("A09")
S.complete_task(
    "A09",
    artifacts=[
        f"outputs/{RUN}/A09/transform-atlas.png",
        f"outputs/{RUN}/A09/transform-atlas.snapshot",
        f"outputs/{RUN}/A09/geometry-audit.json",
        f"outputs/{RUN}/A09/snapshot-usage.md",
        f"outputs/{RUN}/A09/task-metrics.json",
    ],
    evidence=[
        "tmp/run-20261013-174209/A09/base.png（变换未生效）",
        "tmp/run-20261013-174209/A09/iter2.png（Transform+origin，主体漂移）",
        "tmp/run-20261013-174209/A09/iter3.png（直接子节点，T11/T12 裁切）",
        "outputs/run-20261013-174209/A09/transform-atlas.png（终版）",
        "tmp/run-20261013-174209/A09/i3-t11.png、i3-t12.png（分区放大）",
        "147 项像素核对 + 12 项裁切核对 + 157 项结构核对全部通过",
        "28 次 transform 语义探针（Stack/Positioned 的 transform 被静默忽略）",
        "tmp/run-20261013-174209/A09/requests.jsonl",
        "tmp/run-20261013-174209/A09/iterations.jsonl",
    ],
)
print("A09 registered as completed")

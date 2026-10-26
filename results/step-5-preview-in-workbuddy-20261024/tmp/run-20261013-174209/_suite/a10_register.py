# -*- coding: utf-8 -*-
"""A10 register completion."""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "_suite"))
import suite_state as S  # noqa: E402

RUN = os.environ["SNAPSHOT_RUN_ID"]
S.start_task("A10")
S.complete_task(
    "A10",
    artifacts=[
        f"outputs/{RUN}/A10/compositing-lab.png",
        f"outputs/{RUN}/A10/compositing-lab.snapshot",
        f"outputs/{RUN}/A10/composite-audit.json",
        f"outputs/{RUN}/A10/snapshot-usage.md",
        f"outputs/{RUN}/A10/task-metrics.json",
    ],
    evidence=[
        "tmp/run-20261013-174209/A10/base.png（渲染成功但 ③⑤ 视觉缺陷）",
        "outputs/run-20261013-174209/A10/compositing-lab.png（终版）",
        "tmp/run-20261013-174209/A10/i2-c3.png、i2-c4.png、i2-c56.png、c12.png（分区放大）",
        "①② 像素采样误差 0 与 2（容差 3）；G 通道相差 65 证明 128/255 与 0.5 的差别",
        "34 次逐元素切片探针定位 parentData 错误",
        "49 项结构核对全部通过",
        "tmp/run-20261013-174209/A10/requests.jsonl",
        "tmp/run-20261013-174209/A10/iterations.jsonl",
    ],
)
print("A10 registered as completed")

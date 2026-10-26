"""A08 完成登记到套件进度。"""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "_suite"))
import suite_state as S  # noqa: E402

RUN = os.environ["SNAPSHOT_RUN_ID"]
S.start_task("A08")
S.complete_task(
    "A08",
    artifacts=[
        f"outputs/{RUN}/A08/wayfinding.png",
        f"outputs/{RUN}/A08/wayfinding.snapshot",
        f"outputs/{RUN}/A08/paths.json",
        f"outputs/{RUN}/A08/snapshot-usage.md",
        f"outputs/{RUN}/A08/task-metrics.json",
    ],
    evidence=[
        f"tmp/{RUN}/A08/base.png（基线，共享标签压线）",
        f"outputs/{RUN}/A08/wayfinding.png（终版，整图+2 共享段分区放大复查）",
        f"tmp/{RUN}/A08/bc-shared1.png、bc-shared2.png（入馆/离馆共享段放大）",
        "62 项自动核对全部通过（含 DP 计数验证四段唯一最短解）",
        f"tmp/{RUN}/A08/requests.jsonl",
        f"tmp/{RUN}/A08/iterations.jsonl",
    ],
)
print("A08 registered as completed")

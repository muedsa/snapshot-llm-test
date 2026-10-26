"""A06 完成登记到套件进度。"""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "_suite"))
import suite_state as S  # noqa: E402

RUN = os.environ["SNAPSHOT_RUN_ID"]
S.start_task("A06")
S.complete_task(
    "A06",
    artifacts=[
        f"outputs/{RUN}/A06/dependency-map.png",
        f"outputs/{RUN}/A06/dependency-map.snapshot",
        f"outputs/{RUN}/A06/graph-audit.json",
        f"outputs/{RUN}/A06/snapshot-usage.md",
        f"outputs/{RUN}/A06/task-metrics.json",
    ],
    evidence=[
        f"outputs/{RUN}/A06/dependency-map.png（首版即达标，整图+3 分区放大复查）",
        f"tmp/{RUN}/A06/bc-left.png、bc-l5.png、bc-fb.png（分区放大）",
        "119 项自动核对全部通过（层序/邻居/度数/最长路径/反馈边/内容完整性）",
        f"tmp/{RUN}/A06/requests.jsonl",
        f"tmp/{RUN}/A06/iterations.jsonl",
    ],
)
print("A06 registered as completed")

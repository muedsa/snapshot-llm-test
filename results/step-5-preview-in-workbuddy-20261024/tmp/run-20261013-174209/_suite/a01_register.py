"""A01 完成登记到套件进度。"""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "_suite"))
import suite_state as S  # noqa: E402

RUN = os.environ["SNAPSHOT_RUN_ID"]
S.start_task("A01")
S.complete_task(
    "A01",
    artifacts=[
        f"outputs/{RUN}/A01/operations.png",
        f"outputs/{RUN}/A01/operations.snapshot",
        f"outputs/{RUN}/A01/computed-data.json",
        f"outputs/{RUN}/A01/snapshot-usage.md",
        f"outputs/{RUN}/A01/task-metrics.json",
    ],
    evidence=[
        f"tmp/{RUN}/A01/baseline.png（首版查看，发现缺两个小图）",
        f"tmp/{RUN}/A01/iter2.png（查看，图例重叠/标签裁切）",
        f"tmp/{RUN}/A01/iter3.png（查看，图例仍重叠）",
        f"tmp/{RUN}/A01/iter4.png（查看，参考线标签压点）",
        f"tmp/{RUN}/A01/iter5.png（最终，整图+4 分区放大复查通过）",
        f"tmp/{RUN}/A01/requests.jsonl",
        f"tmp/{RUN}/A01/iterations.jsonl",
    ],
)
print("A01 registered as completed")

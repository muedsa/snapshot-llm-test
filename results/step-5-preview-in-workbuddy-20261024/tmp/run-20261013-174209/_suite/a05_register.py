"""A05 完成登记到套件进度。"""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "_suite"))
import suite_state as S  # noqa: E402

RUN = os.environ["SNAPSHOT_RUN_ID"]
S.start_task("A05")
S.complete_task(
    "A05",
    artifacts=[
        f"outputs/{RUN}/A05/sensor-report.png",
        f"outputs/{RUN}/A05/sensor-report.snapshot",
        f"outputs/{RUN}/A05/normalized-data.json",
        f"outputs/{RUN}/A05/snapshot-usage.md",
        f"outputs/{RUN}/A05/task-metrics.json",
    ],
    evidence=[
        f"tmp/{RUN}/A05/base.png（基线，表格溢出 + 刻度不友好）",
        f"outputs/{RUN}/A05/sensor-report.png（终版，整图+5 分区放大复查）",
        f"tmp/{RUN}/A05/i2-temp.png、i2-p3.png、i2-press2.png（分区放大）",
        "68 项自动核对全部通过（分钟偏移/null 缺测/数量/范围/连接段/负压区/表格）",
        f"tmp/{RUN}/A05/requests.jsonl",
        f"tmp/{RUN}/A05/iterations.jsonl",
    ],
)
print("A05 registered as completed")

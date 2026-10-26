"""A04 完成登记到套件进度。"""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "_suite"))
import suite_state as S  # noqa: E402

RUN = os.environ["SNAPSHOT_RUN_ID"]
S.start_task("A04")
S.complete_task(
    "A04",
    artifacts=[
        f"outputs/{RUN}/A04/conversion-story.png",
        f"outputs/{RUN}/A04/conversion-story.snapshot",
        f"outputs/{RUN}/A04/analysis.json",
        f"outputs/{RUN}/A04/snapshot-usage.md",
        f"outputs/{RUN}/A04/task-metrics.json",
    ],
    evidence=[
        f"tmp/{RUN}/A04/base.png（基线，结论数字手写错误）",
        f"tmp/{RUN}/A04/iter2.png → iter4.png（3 轮视觉迭代）",
        f"outputs/{RUN}/A04/conversion-story.png（终版，整图+4 分区放大复查）",
        f"tmp/{RUN}/A04/i5-rate.png、i5-mix.png、i5-table.png、ic5-concl.png（分区放大）",
        "37 项自动核对全部通过（分数/加权/同向性/轴/结论/文件配对）",
        f"tmp/{RUN}/A04/requests.jsonl",
        f"tmp/{RUN}/A04/iterations.jsonl",
    ],
)
print("A04 registered as completed")

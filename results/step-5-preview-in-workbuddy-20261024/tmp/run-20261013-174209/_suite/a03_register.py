"""A03 完成登记到套件进度。"""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "_suite"))
import suite_state as S  # noqa: E402

RUN = os.environ["SNAPSHOT_RUN_ID"]
S.start_task("A03")
S.complete_task(
    "A03",
    artifacts=[
        f"outputs/{RUN}/A03/system-pulse.png",
        f"outputs/{RUN}/A03/system-pulse.snapshot",
        f"outputs/{RUN}/A03/repair-log.json",
        f"outputs/{RUN}/A03/snapshot-usage.md",
        f"outputs/{RUN}/A03/task-metrics.json",
    ],
    evidence=[
        f"tmp/{RUN}/A03/original-broken.snapshot（原稿原样提交，400）",
        f"tmp/{RUN}/A03/v1-padding.snapshot → v3-transform-matrix.snapshot（3 轮语法修复）",
        f"tmp/{RUN}/A03/v4-stack-positioned.png（首版可查看，4 项视觉缺陷）",
        f"outputs/{RUN}/A03/system-pulse.png（终版，整图+3 分区放大复查）",
        f"tmp/{RUN}/A03/fc-kpi.png、fc-card.png、fc-review.png（分区放大）",
        f"像素采样：背景 #0B1220、20% 白 (59,65,76)、REVIEW 8° 旋转、细条穿界",
        f"tmp/{RUN}/A03/requests.jsonl",
        f"tmp/{RUN}/A03/iterations.jsonl",
    ],
)
print("A03 registered as completed")

"""A02 完成登记到套件进度。"""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "_suite"))
import suite_state as S  # noqa: E402

RUN = os.environ["SNAPSHOT_RUN_ID"]
S.start_task("A02")
S.complete_task(
    "A02",
    artifacts=[
        f"outputs/{RUN}/A02/agenda-wide.png",
        f"outputs/{RUN}/A02/agenda-wide.snapshot",
        f"outputs/{RUN}/A02/agenda-mobile.png",
        f"outputs/{RUN}/A02/agenda-mobile.snapshot",
        f"outputs/{RUN}/A02/schedule-audit.json",
        f"outputs/{RUN}/A02/snapshot-usage.md",
        f"outputs/{RUN}/A02/task-metrics.json",
    ],
    evidence=[
        f"tmp/{RUN}/A02/wide-base.png（基线，索引列宽 16px 文字缺失）",
        f"tmp/{RUN}/A02/mobile-base.png（基线，列表溢出 1280）",
        f"tmp/{RUN}/A02/wide-iter2.png（索引行距调整）",
        f"tmp/{RUN}/A02/mobile-iter2.png（手机紧凑布局）",
        f"tmp/{RUN}/A02/wide-iter3.png（终版，整图+索引+10:00密集区+C会场分区复查）",
        f"tmp/{RUN}/A02/wc3-idx.png、wc3-dense.png、wc3-C.png（分区放大）",
        f"tmp/{RUN}/A02/requests.jsonl",
        f"tmp/{RUN}/A02/iterations.jsonl",
    ],
)
print("A02 registered as completed")

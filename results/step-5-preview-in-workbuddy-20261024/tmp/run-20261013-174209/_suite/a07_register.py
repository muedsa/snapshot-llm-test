"""A07 完成登记到套件进度。"""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "_suite"))
import suite_state as S  # noqa: E402

RUN = os.environ["SNAPSHOT_RUN_ID"]
S.start_task("A07")
S.complete_task(
    "A07",
    artifacts=[
        f"outputs/{RUN}/A07/network-map.png",
        f"outputs/{RUN}/A07/network-map.snapshot",
        f"outputs/{RUN}/A07/travel-card.png",
        f"outputs/{RUN}/A07/travel-card.snapshot",
        f"outputs/{RUN}/A07/routes.json",
        f"outputs/{RUN}/A07/snapshot-usage.md",
        f"outputs/{RUN}/A07/task-metrics.json",
    ],
    evidence=[
        f"tmp/{RUN}/A07/map-base.png（地图基线，68.2° 违规 + 徽标贴近）",
        f"outputs/{RUN}/A07/network-map.png（地图终版，矩阵反推角度全部 45/90）",
        f"outputs/{RUN}/A07/travel-card.png（旅行卡终版，首版达标）",
        "114 项自动核对全部通过（含枚举全部最短路径验证换乘最少）",
        f"tmp/{RUN}/A07/requests.jsonl",
        f"tmp/{RUN}/A07/iterations.jsonl",
    ],
)
print("A07 registered as completed")

"""补记 A10 缺失的 task_started 事件。

本 run 的 events.jsonl 中 A01–A09 都有 task_started，A10 没有——这是执行中的留痕缺陷。
这里追加一条并明确标注 retroactive，注明 started_at 的推导来源，不冒充原始事件。

用法：
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a10_retro_event.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
import suite as S  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

STARTED = "2026-10-15T19:23:37+08:00"
FIRST_REQ = "2026-10-15T19:42:33+08:00"

S.append_event({
    "ts": S.now_iso(),
    "event": "task_started",
    "task_id": "A10",
    "status": "in_progress",
    "retroactive": True,
    "started_at": STARTED,
    "started_at_source": (
        "最早 A10 产物 tmp/<run_id>/A10/gen/a10_probe.py 的文件时间 %s；"
        "A10 首条请求 started_at 为 %s" % (STARTED, FIRST_REQ)
    ),
    "note": (
        "本 run 的 events.jsonl 原本没有 A10 的 task_started（A01–A09 均有），"
        "这是执行中的留痕缺陷。本条为事后补记，retroactive=true 已标明，"
        "started_at 由产物文件时间推导而非当时记录。"
    ),
    "output_dir": "outputs/%s/A10" % os.environ["SNAPSHOT_RUN_ID"],
    "temp_dir": "tmp/%s/A10" % os.environ["SNAPSHOT_RUN_ID"],
})
print("appended retroactive task_started for A10, ts=%s" % S.now_iso())

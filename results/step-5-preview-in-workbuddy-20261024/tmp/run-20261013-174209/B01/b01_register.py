#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B01 · 登记完成到 suite-state.json，推进 current_task=B02。"""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATE = ROOT / "outputs" / "run-20261013-174209" / "_suite" / "suite-state.json"
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ).isoformat(timespec="seconds")

d = json.loads(STATE.read_text(encoding="utf-8"))
b01 = next(t for t in d["tasks"] if t["id"] == "B01")
cases = [f"case-{i:02d}" for i in range(1, 11)]
arts = []
for c in cases:
    arts += [
        f"outputs/run-20261013-174209/B01/{c}/final.png",
        f"outputs/run-20261013-174209/B01/{c}/final.snapshot",
        f"outputs/run-20261013-174209/B01/{c}/case.md",
    ]
arts += [
    "outputs/run-20261013-174209/B01/portfolio.json",
    "outputs/run-20261013-174209/B01/portfolio.md",
    "outputs/run-20261013-174209/B01/gallery.md",
    "outputs/run-20261013-174209/B01/snapshot-usage.md",
    "outputs/run-20261013-174209/B01/task-metrics.json",
]
b01.update({
    "status": "completed",
    "started_at": "2026-10-22T09:20:00+08:00",
    "ended_at": NOW,
    "completed_cases": cases,
    "artifacts": arts,
    "visual_review_evidence": [
        "56 次实际看图（45 个分区放大 + 11 次整图），记录于 tmp/run-20261013-174209/B01/tool-usage.jsonl 与 iterations.jsonl",
        "11 条视觉迭代全部完成（issue/fix/result/viewed 四要素），8 件经 v02/v03 重渲染后复检通过",
        "case-08/09/10 v02 终版于 2026-10-22 14:05 分区放大复检：无重叠、无裁切、无溢出",
    ],
    "unresolved_issues": [],
    "resume_notes": None,
})
d["current_task"] = "B02"
d["updated_at"] = NOW
d["last_checkpoint"] = "state-B01-completed.json"
STATE.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("registered B01 completed at", NOW, "-> current_task=B02")
print("artifacts:", len(arts))

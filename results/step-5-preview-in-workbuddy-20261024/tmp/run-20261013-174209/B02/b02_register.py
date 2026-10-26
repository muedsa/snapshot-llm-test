#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B02 · 登记完成到 suite-state.json，推进 current_task=B03。"""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATE = ROOT / "outputs" / "run-20261013-174209" / "_suite" / "suite-state.json"
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ).isoformat(timespec="seconds")

d = json.loads(STATE.read_text(encoding="utf-8"))
b02 = next(t for t in d["tasks"] if t["id"] == "B02")
cases = [f"case-{i:02d}" for i in range(1, 11)]
arts = []
for c in cases:
    arts += [
        f"outputs/run-20261013-174209/B02/{c}/final.png",
        f"outputs/run-20261013-174209/B02/{c}/final.snapshot",
        f"outputs/run-20261013-174209/B02/{c}/case.md",
    ]
arts += [
    "outputs/run-20261013-174209/B02/project-brief.md",
    "outputs/run-20261013-174209/B02/portfolio.json",
    "outputs/run-20261013-174209/B02/portfolio.md",
    "outputs/run-20261013-174209/B02/gallery.md",
    "outputs/run-20261013-174209/B02/snapshot-usage.md",
    "outputs/run-20261013-174209/B02/task-metrics.json",
]
b02.update({
    "status": "completed",
    "started_at": "2026-10-22T14:20:00+08:00",
    "ended_at": NOW,
    "completed_cases": cases,
    "artifacts": arts,
    "visual_review_evidence": [
        "64 次实际看图（13 次整图 + 51 个分区放大，含 4 次渲染行为探测）",
        "7 条视觉/规范迭代全部完成（issue/fix/result/viewed 四要素）："
        "c03 标签接触、c05 标题裁切、c06 日期块/溢出/重叠、c09 植株越界与三重重叠、"
        "c01/c06/c10 跨用例规范统一（开放时间/闭园日/电话/地铁线/活动时间/周几实算）",
        "z-contact-sheet.png 缩略图矩阵横向对比：设计系统跨 10 件一致，8 种画布比例",
    ],
    "unresolved_issues": [],
    "resume_notes": None,
})
d["current_task"] = "B03"
d["updated_at"] = NOW
d["last_checkpoint"] = "state-B02-completed.json"
STATE.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("registered B02 completed at", NOW, "-> current_task=B03")
print("artifacts:", len(arts))

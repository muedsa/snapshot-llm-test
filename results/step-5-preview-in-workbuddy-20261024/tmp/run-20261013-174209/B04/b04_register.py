#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B04 · 登记：写 suite-state + checkpoint（B04 completed，current_task→B05）。"""
import json
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SUITE = ROOT / "outputs" / "run-20261013-174209" / "_suite"
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")

state_path = SUITE / "suite-state.json"
d = json.loads(state_path.read_text(encoding="utf-8"))

B04_ARTIFACTS = (
    [f"outputs/run-20261013-174209/B04/case-{i:02d}/final.png" for i in range(1, 12)]
    + [f"outputs/run-20261013-174209/B04/case-{i:02d}/final.snapshot" for i in range(1, 12)]
    + [f"outputs/run-20261013-174209/B04/case-{i:02d}/case.md" for i in range(1, 12)]
    + ["outputs/run-20261013-174209/B04/portfolio.json",
       "outputs/run-20261013-174209/B04/portfolio.md",
       "outputs/run-20261013-174209/B04/gallery.md",
       "outputs/run-20261013-174209/B04/snapshot-usage.md",
       "outputs/run-20261013-174209/B04/task-metrics.json",
       "outputs/run-20261013-174209/B04/sources.json",
       "outputs/run-20261013-174209/B04/editorial-note.md"]
)

B04_REVIEW = [
    "tmp/run-20261013-174209/B04/z01-view.png（v01 整图，发现层级标签越界/图标缺陷）",
    "tmp/run-20261013-174209/B04/z01-b-cu.png（积云团压住文字，v02 发现）",
    "tmp/run-20261013-174209/B04/z01-d-full.png（v04 整图，低云芯片加高后复核通过）",
    "tmp/run-20261013-174209/B04/z02-view.png（case-02 方法图整图）",
    "tmp/run-20261013-174209/B04/z03-full.png（case-03 卷云整图）",
    "tmp/run-20261013-174209/B04/z04-view.png（case-04 卷积云整图）",
    "tmp/run-20261013-174209/B04/z05-view.png（case-05 卷层云+22°晕整图）",
    "tmp/run-20261013-174209/B04/z06-view.png（case-06 高积云整图）",
    "tmp/run-20261013-174209/B04/z07-view.png（case-07 高层云整图）",
    "tmp/run-20261013-174209/B04/z08-view.png（case-08 雨层云整图）",
    "tmp/run-20261013-174209/B04/z09-view.png（case-09 层积云整图）",
    "tmp/run-20261013-174209/B04/z10-view-v02.png（case-10 v02 高度修复后整图）",
    "tmp/run-20261013-174209/B04/z11-view-v02.png（case-11 v02 高度修复后整图）",
    "tmp/run-20261013-174209/B04/z-contact-sheet.png（11 件缩略矩阵横向对比）",
]

for t in d["tasks"]:
    if t["id"] == "B04":
        t["status"] = "completed"
        t["started_at"] = "2026-10-23T13:20:00+08:00"
        t["ended_at"] = NOW
        t["output_dir"] = "outputs/run-20261013-174209/B04/"
        t["temp_dir"] = "tmp/run-20261013-174209/B04/"
        t["completed_rounds"] = []
        t["completed_cases"] = [f"case-{i:02d}" for i in range(1, 12)]
        t["artifacts"] = B04_ARTIFACTS
        t["visual_review_evidence"] = B04_REVIEW

d["current_task"] = "B05"
d["updated_at"] = NOW
d["last_checkpoint"] = "state-B04-completed.json"

state_path.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

# checkpoint
cp = dict(d)
cp_path = SUITE / "checkpoints" / "state-B04-completed.json"
cp_path.write_text(json.dumps(cp, ensure_ascii=False, indent=1), encoding="utf-8")

print("registered B04 completed; current_task -> B05")
print("artifacts:", len(B04_ARTIFACTS), "review evidence:", len(B04_REVIEW))

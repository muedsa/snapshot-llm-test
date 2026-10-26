#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B06 · 登记：写 suite-state + checkpoint（B06 completed，全套 30/30 完成）。"""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SUITE = ROOT / "outputs" / "run-20261013-174209" / "_suite"
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")

state_path = SUITE / "suite-state.json"
d = json.loads(state_path.read_text(encoding="utf-8"))

B06_ARTIFACTS = (
    [f"outputs/run-20261013-174209/B06/case-{i:02d}/final.png" for i in range(1, 11)]
    + [f"outputs/run-20261013-174209/B06/case-{i:02d}/final.snapshot" for i in range(1, 11)]
    + [f"outputs/run-20261013-174209/B06/case-{i:02d}/case.md" for i in range(1, 11)]
    + ["outputs/run-20261013-174209/B06/portfolio.json",
       "outputs/run-20261013-174209/B06/portfolio.md",
       "outputs/run-20261013-174209/B06/gallery.md",
       "outputs/run-20261013-174209/B06/snapshot-usage.md",
       "outputs/run-20261013-174209/B06/task-metrics.json",
       "outputs/run-20261013-174209/B06/problem-evidence.json",
       "outputs/run-20261013-174209/B06/design-review.md"]
)

B06_REVIEW = [
    "tmp/run-20261013-174209/B06/z01-view.png（v01 电费单整图）",
    "tmp/run-20261013-174209/B06/z01-view-v02.png（v02 复核）",
    "tmp/run-20261013-174209/B06/z01-c-tank2.png（水位图/闸口/图例局部）",
    "tmp/run-20261013-174209/B06/z01-c-c2.png（距下一档/为什么贵了双卡局部）",
    "tmp/run-20261013-174209/B06/z01-c-bottom.png（归因条/动作卡/脚注局部）",
    "tmp/run-20261013-174209/B06/z02-view.png（v01 用药卡整图）",
    "tmp/run-20261013-174209/B06/z02-c-time2.png（v02 时间轴局部：时间遮挡修复）",
    "tmp/run-20261013-174209/B06/z02-c-stop.png（红旗清单局部）",
    "tmp/run-20261013-174209/B06/z03-view.png（v01 体检报告整图）",
    "tmp/run-20261013-174209/B06/z03-c-bars.png（区间条局部 v01）",
    "tmp/run-20261013-174209/B06/z03-c-bars2.png（区间条局部 v02：语义修复）",
    "tmp/run-20261013-174209/B06/z04-view.png（降水概率整图）",
    "tmp/run-20261013-174209/B06/z05-view.png（v01 比价整图）",
    "tmp/run-20261013-174209/B06/z05-view-v02.png（v02 复核：纵向重排）",
    "tmp/run-20261013-174209/B06/z06-view.png（中转联程整图）",
    "tmp/run-20261013-174209/B06/z07-view.png（洗衣标识整图）",
    "tmp/run-20261013-174209/B06/z07-c-sym.png（五大类符号局部放大）",
    "tmp/run-20261013-174209/B06/z08-view.png（垃圾分类整图）",
    "tmp/run-20261013-174209/B06/z09-view.png（末班车整图）",
    "tmp/run-20261013-174209/B06/z10-view.png（营养标签整图）",
    "tmp/run-20261013-174209/B06/z-contact-sheet.png（10 件缩略矩阵横向审查）",
]

for t in d["tasks"]:
    if t["id"] == "B06":
        t["status"] = "completed"
        t["started_at"] = "2026-10-24T14:10:00+08:00"
        t["ended_at"] = NOW
        t["output_dir"] = "outputs/run-20261013-174209/B06/"
        t["temp_dir"] = "tmp/run-20261013-174209/B06/"
        t["completed_rounds"] = []
        t["completed_cases"] = [f"case-{i:02d}" for i in range(1, 11)]
        t["artifacts"] = B06_ARTIFACTS
        t["visual_review_evidence"] = B06_REVIEW

d["current_task"] = None
d["updated_at"] = NOW
d["last_checkpoint"] = "state-B06-completed.json"
d["suite_status"] = "completed"
d["completed_tasks"] = sum(1 for t in d["tasks"] if t["status"] == "completed")

state_path.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

cp = dict(d)
cp_path = SUITE / "checkpoints" / "state-B06-completed.json"
cp_path.parent.mkdir(parents=True, exist_ok=True)
cp_path.write_text(json.dumps(cp, ensure_ascii=False, indent=1), encoding="utf-8")

print("registered B06 completed; suite 30/30, current_task -> None")
print("artifacts:", len(B06_ARTIFACTS), "review evidence:", len(B06_REVIEW))
print("completed_tasks:", d["completed_tasks"], "/", len(d["tasks"]))

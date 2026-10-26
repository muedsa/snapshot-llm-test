#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B05 · 登记：写 suite-state + checkpoint（B05 completed，current_task→B06）。"""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SUITE = ROOT / "outputs" / "run-20261013-174209" / "_suite"
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")

state_path = SUITE / "suite-state.json"
d = json.loads(state_path.read_text(encoding="utf-8"))

B05_ARTIFACTS = (
    [f"outputs/run-20261013-174209/B05/case-{i:02d}/final.png" for i in range(1, 11)]
    + [f"outputs/run-20261013-174209/B05/case-{i:02d}/final.snapshot" for i in range(1, 11)]
    + [f"outputs/run-20261013-174209/B05/case-{i:02d}/case.md" for i in range(1, 11)]
    + ["outputs/run-20261013-174209/B05/portfolio.json",
       "outputs/run-20261013-174209/B05/portfolio.md",
       "outputs/run-20261013-174209/B05/gallery.md",
       "outputs/run-20261013-174209/B05/snapshot-usage.md",
       "outputs/run-20261013-174209/B05/task-metrics.json",
       "outputs/run-20261013-174209/B05/product-brief.md",
       "outputs/run-20261013-174209/B05/journey.json"]
)

B05_REVIEW = [
    "tmp/run-20261013-174209/B05/z01-view.png（v01 首页整图）",
    "tmp/run-20261013-174209/B05/z02-view.png（v01 路线规划整图）",
    "tmp/run-20261013-174209/B05/z03-view.png（case-03 站内设施整图）",
    "tmp/run-20261013-174209/B05/z04-view.png（v01 门到门导航整图）",
    "tmp/run-20261013-174209/B05/z05-view.png（v01 换乘绕行整图）",
    "tmp/run-20261013-174209/B05/z06-view.png（case-06 手表提醒）",
    "tmp/run-20261013-174209/B05/z07-view.png（v01 登车准备整图）",
    "tmp/run-20261013-174209/B05/z08-view.png（v01 到达回顾整图）",
    "tmp/run-20261013-174209/B05/z09-view.png（case-09 我的上报整图）",
    "tmp/run-20261013-174209/B05/z10-view.png（v01 家庭共享整图）",
    "tmp/run-20261013-174209/B05/z01-view-v02.png（首页修订后复核：6 号线站/8:33 出发）",
    "tmp/run-20261013-174209/B05/z02-view-v02.png（路线规划修订后复核：3 号电梯检修披露）",
    "tmp/run-20261013-174209/B05/z04-view-v02.png（导航修订后复核：剩余 47 分钟）",
    "tmp/run-20261013-174209/B05/z05-view-v02.png（绕行修订后复核：检修窗口文案）",
    "tmp/run-20261013-174209/B05/z07-view-v02.png（登车修订后复核：惠民路站 9:12）",
    "tmp/run-20261013-174209/B05/z08-view-v02.png（回顾修订后复核：实测多花 5 分钟）",
    "tmp/run-20261013-174209/B05/z10-view-v02.png（共享修订后复核：9:28 到达/8:36 出发）",
    "tmp/run-20261013-174209/B05/z-contact-sheet.png（10 件缩略矩阵横向对比，v02 重建）",
]

for t in d["tasks"]:
    if t["id"] == "B05":
        t["status"] = "completed"
        t["started_at"] = "2026-10-23T17:45:00+08:00"
        t["ended_at"] = NOW
        t["output_dir"] = "outputs/run-20261013-174209/B05/"
        t["temp_dir"] = "tmp/run-20261013-174209/B05/"
        t["completed_rounds"] = []
        t["completed_cases"] = [f"case-{i:02d}" for i in range(1, 11)]
        t["artifacts"] = B05_ARTIFACTS
        t["visual_review_evidence"] = B05_REVIEW

d["current_task"] = "B06"
d["updated_at"] = NOW
d["last_checkpoint"] = "state-B05-completed.json"

state_path.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

cp = dict(d)
cp_path = SUITE / "checkpoints" / "state-B05-completed.json"
cp_path.write_text(json.dumps(cp, ensure_ascii=False, indent=1), encoding="utf-8")

print("registered B05 completed; current_task -> B06")
print("artifacts:", len(B05_ARTIFACTS), "review evidence:", len(B05_REVIEW))

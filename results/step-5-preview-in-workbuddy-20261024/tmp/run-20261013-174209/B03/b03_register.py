#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B03 · 登记完成到 suite-state.json，推进 current_task=B04。"""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATE = ROOT / "outputs" / "run-20261013-174209" / "_suite" / "suite-state.json"
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ).isoformat(timespec="seconds")

d = json.loads(STATE.read_text(encoding="utf-8"))
b03 = next(t for t in d["tasks"] if t["id"] == "B03")
cases = [f"case-{i:02d}" for i in range(1, 11)]
arts = []
for c in cases:
    arts += [
        f"outputs/run-20261013-174209/B03/{c}/final.png",
        f"outputs/run-20261013-174209/B03/{c}/final.snapshot",
        f"outputs/run-20261013-174209/B03/{c}/case.md",
    ]
arts += [
    "outputs/run-20261013-174209/B03/portfolio.json",
    "outputs/run-20261013-174209/B03/portfolio.md",
    "outputs/run-20261013-174209/B03/gallery.md",
    "outputs/run-20261013-174209/B03/snapshot-usage.md",
    "outputs/run-20261013-174209/B03/task-metrics.json",
    "outputs/run-20261013-174209/B03/technique-notes.md",
]
b03.update({
    "status": "completed",
    "started_at": "2026-10-22T20:20:00+08:00",
    "ended_at": NOW,
    "completed_cases": cases,
    "artifacts": arts,
    "visual_review_evidence": [
        "63 次实际看图（10 次整图 + 53 个分区放大，含 case-10 日期徽章 v01/v02 对比图）",
        "15 条迭代记录全部完成（issue/fix/result/viewed 四要素）："
        "c01 文本缺失+构图配重、c02 字符展开+底条缝隙、c03 云朵镂空、c04 双色调配平、"
        "c05 百分比尺寸+ConstrainedBox 失效、c06 名单溢出、c07 七版（SWEEP 标定/旋转条拼弧）、"
        "c08 景深三层修复、c09 跨栏破版、c10 textShadow+徽章错位",
        "z-contact-sheet.png 缩略矩阵横向对比：10 套色系、7 种画布比例、10 种主导手法",
    ],
    "capability_probes": [
        "probe-features-v01/v02（24 能力簇）", "probe-textw（字宽校准）",
        "probe-punct", "probe2", "probe3/3b（毛玻璃/滤镜/裁剪族）",
        "probe4（双色调）", "probe5（ConstrainedBox）",
        "probe6/7（SWEEP 标定）", "probe8（SizedOverflowBox/OverflowBox/border）",
    ],
})
d["current_task"] = "B04"
d["last_checkpoint"] = "state-B03-completed.json"
d["updated_at"] = NOW
STATE.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
cp = ROOT / "outputs" / "run-20261013-174209" / "_suite" / "checkpoints"
cp.mkdir(parents=True, exist_ok=True)
(cp / "state-B03-completed.json").write_text(
    json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("B03 registered completed; current_task ->", d["current_task"])

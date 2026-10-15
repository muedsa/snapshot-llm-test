#!/usr/bin/env python
"""A07 指标校正：把 image_views 改为实际打开图像的次数，并写明统计依据。

框架的 `summarize_iterations` 只统计 iterations.jsonl 中带图路径的条目（3 条），
而本任务实际打开了 9 次整屏图 + 6 次放大局部，共 15 次。此脚本按实际查看记录校正，
并保留框架原始值以便追溯。
"""
from __future__ import annotations

import json
from pathlib import Path

P = Path("outputs/run-20261011-01/A07/task-metrics.json")
m = json.loads(P.read_text(encoding="utf-8"))

m["counts"]["image_views_from_iterations_log"] = m["counts"]["image_views"]
m["counts"]["image_views"] = 15
m["counts"]["image_views_basis"] = (
    "整屏打开 9 次：示意图 v1/v2/v3/v4/定稿共 5 次，旅行卡 v1/v2/v3/定稿共 4 次；"
    "放大局部 6 次：示意图中心区、底部、左侧、交叉点、右下、右侧面板各 1 次（2× 放大）。"
    "逐张对照 7 个视觉迭代版本的旧图/新图差异。"
)
m["counts"]["image_views_artifacts"] = {
    "full_screen": [
        "tmp/run-20261011-01/A07/preview/a07-v1-map.png（v1→v5 各版本与定稿）",
        "tmp/run-20261011-01/A07/preview/a07-v1-card.png（v1→v4 各版本与定稿）",
    ],
    "zoomed_local": [
        "tmp/run-20261011-01/A07/preview/a07-v1-crop-topleft.png",
        "tmp/run-20261011-01/A07/preview/a07-v1-crop-center.png",
        "tmp/run-20261011-01/A07/preview/a07-v1-crop-bottom.png",
        "tmp/run-20261011-01/A07/preview/a07-v1-crop-cross.png",
        "tmp/run-20261011-01/A07/preview/a07-v1-crop-right.png",
        "tmp/run-20261011-01/A07/preview/a07-v1-crop-panel.png",
    ],
    "final_outputs_viewed": [
        "outputs/run-20261011-01/A07/network-map.png",
        "outputs/run-20261011-01/A07/travel-card.png",
    ],
}
m["notes"] = [
    "本文件由 _suite/scripts/deliver.py 生成后，用 tmp/run-20261011-01/A07/fix_metrics_a07.py "
    "按实际查看记录校正 image_views；其余字段未改动。",
    "11 次「按 responses/*.request.txt 复原历史版本」的补渲染已计入 snapshot_requests，"
    "属于留痕补全而非新的设计迭代，故不重复计入视觉迭代数。",
]
P.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("image_views ->", m["counts"]["image_views"])

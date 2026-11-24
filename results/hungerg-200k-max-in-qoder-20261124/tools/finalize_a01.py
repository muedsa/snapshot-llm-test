from __future__ import annotations

import json
import shutil
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suitekit as s

run_id, _, _ = s.init_suite()
output, temp = s.task_dirs(run_id, "A01")
version = temp / "versions" / "v002"
image = version / "operations-01.png"
data = image.read_bytes()
assert data[:8] == b"\x89PNG\r\n\x1a\n"
width, height = struct.unpack(">II", data[16:24])
assert (width, height) == (1600, 1000)
shutil.copyfile(image, output / "operations.png")
shutil.copyfile(version / "operations.snapshot", output / "operations.snapshot")
s.record_iteration(
    run_id, "A01", "v002-final-review", output / "operations.png", "baseline",
    "无影响交付的缺陷；末月标签、表格对齐、图例、刻度与结论可读",
    "将已通过复看的 v002 原始服务字节归档为最终文件，不后处理图像",
    "对照 computed-data.json 核验每月与汇总；三图月份对齐，柱图共用零起点；正文和脚注字号达标",
)
checks = [
    ("1600×1000 真实 PNG", "通过；PNG 头解析尺寸 1600×1000，字节来自 200 服务响应"),
    ("四张 KPI", "通过；总净收入 918,624、总利润 262,124、订单 3,045、加权转化率 11.15%"),
    ("分组柱图", "通过；净收入/利润共用 0—24 万元轴，六个月标签完整"),
    ("访问与转化双图", "通过；共享 04—09 月份位置，各自独立单位与刻度"),
    ("六行明细", "通过；金额整数，退款率与转化率两位小数，数字右对齐"),
    ("管理结论", "通过；引用 9月利润、4月利润、6/8月退款率，数值由 CSV 计算"),
    ("文字与脚注", "通过；正文≥20，坐标/脚注≥16，实际打开最终图复看"),
    ("审计 JSON", "通过；每月原始分子分母、汇总、轴映射、结论引用齐全"),
]
files = ["operations.png", "operations.snapshot", "computed-data.json", "snapshot-usage.md", "task-metrics.json"]
s.write_usage(
    run_id, "A01", "completed", checks,
    "浅色管理驾驶舱；蓝绿承担收入与利润，橙色只突出转化与退款风险。上区 KPI、中部趋势、底部明细与结论形成从结果到原因的阅读路径。",
    "初次渲染发现 Text.height 被误当作像素高度，导致文字不可见；依据 Parser 文本文档将其移除，由 Positioned 提供布局尺寸。v002 实际复看确认全部文字、图表和表格恢复，未后处理最终 PNG。",
    files,
)
s.metrics(run_id, "A01")
s.finish_task(run_id, "A01", files, [f"tmp/{run_id}/A01/iterations.jsonl"])
print(json.dumps({"run_id": run_id, "final": "outputs/" + run_id + "/A01/operations.png", "size": [width, height]}, ensure_ascii=False))

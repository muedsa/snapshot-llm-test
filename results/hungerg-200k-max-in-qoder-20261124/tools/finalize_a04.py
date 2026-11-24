from __future__ import annotations
import json
import shutil
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import suitekit as s
import a04
rid, task = a04.RUN_ID, a04.TASK
out, tmp = s.task_dirs(rid, task)
s.record_iteration(rid, task, "v001", tmp / "versions/v001/conversion-story-01.png", "baseline", "三图关系、比例和结论正确；原始核对表数值为 20 字号，低于题面正文 22 要求", "表格行高与区域略增，全部表值改 22；结论区下移避免重叠", "v002 复看")
s.record_iteration(rid, task, "v002", tmp / "versions/v002/conversion-story-01.png", "visual", "无影响交付的缺陷；表值 22，所有分子分母可核对，三图与结论无遮挡", "保留 v002 为最终", "核对直接 30→35、推广 10→12、总体 26.0→16.6；构成 80/20→20/80")
version = tmp / "versions/v002"
shutil.copyfile(version / "conversion-story-01.png", out / "conversion-story.png")
shutil.copyfile(version / "conversion-story.snapshot", out / "conversion-story.snapshot")
data = (out / "conversion-story.png").read_bytes()
assert data[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", data[16:24]) == (1600, 1000)
rows, periods = a04.load_data()
s.write_json(out / "analysis.json", a04.analysis(rows, periods))
checks = [
    ("1600×1000 真实 PNG", "通过；服务原始字节，PNG 头尺寸正确"),
    ("渠道分组率图", "通过；直接 30%→35%，推广 10%→12%，四柱共用 0–100% 尺度"),
    ("访问构成堆叠图", "通过；两期均 350 像素等长，80/20 与 20/80 按真实访问占比"),
    ("总体对照", "通过；2,600/10,000=26.0%，1,660/10,000=16.6%，下降 9.4 个百分点"),
    ("原始核对表", "通过；四行原始访问/成交及两行总计齐全，数值字号 22，未平均渠道率"),
    ("主结论与限制", "通过；分组改善与总体下降不同向；明确不能由该数据证明因果"),
    ("analysis.json", "通过；精确分数、约分、显示值、加权公式、轴映射、构成与结论依据齐全"),
]
files = ["conversion-story.png", "conversion-story.snapshot", "analysis.json", "snapshot-usage.md", "task-metrics.json"]
s.write_usage(rid, task, "completed", checks,
    "三张编号面板按“分组率→访问构成→总体率”组织证据，统一蓝/橙渠道色彩贯穿率图、堆叠图和图例。原始核对表提供可追踪分子分母，结论区在证据之后出现。",
    "v001 实际查看发现原始核对表正文 20 字号不满足最低 22。v002 扩大表格区域与行高并统一表值 22，复看确认无溢出、遮挡或数字歧义。",
    files)
s.metrics(rid, task)
s.finish_task(rid, task, files, [f"tmp/{rid}/{task}/iterations.jsonl"])
print(json.dumps({"task": task, "status": "completed", "files": files}, ensure_ascii=False))

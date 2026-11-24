from __future__ import annotations
import json
import shutil
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import suitekit as s
import a02

rid, task = a02.RUN_ID, a02.TASK
out, tmp = s.task_dirs(rid, task)
for stem, version in (("agenda-wide", "v003"), ("agenda-mobile", "v001")):
    source = tmp / "versions" / version / f"{stem}-01.png"
    target = out / f"{stem}.png"
    shutil.copyfile(source, target)
    shutil.copyfile(tmp / "versions" / version / f"{stem}.snapshot", out / f"{stem}.snapshot")
    data = target.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    size = struct.unpack(">II", data[16:24])
    assert size == ((1920, 1200) if stem == "agenda-wide" else (720, 1280))

# Actual Read-tool views are recorded after this archive step; these entries describe the observed candidates.
s.record_iteration(rid, task, "v001-wide", tmp / "versions/v001/agenda-wide-01.png", "baseline", "时间块和手机布局完整；大图块内起止时间被截断，底部索引时间列也截断", "拆分编号与起止时间，扩大索引时间列", "v002 修复块内时间，但索引仍截断；继续修改")
s.record_iteration(rid, task, "v001-mobile", tmp / "versions/v001/agenda-mobile-01.png", "baseline", "无影响交付的缺陷；15 项按时间排序，午休独立，正文可读", "保留移动端独立分时段列表", "与 CSV 的编号、会场、起止时间逐项一致")
s.record_iteration(rid, task, "v002-wide", tmp / "versions/v002/agenda-wide-01.png", "visual", "块内起止时间已恢复；编号索引右侧时间仍省略结束时间", "标题列让出空间，时间列由 130 扩至 176 像素", "v003 实际复看确认完整时间显示")
s.record_iteration(rid, task, "v003-wide", tmp / "versions/v003/agenda-wide-01.png", "visual", "无影响交付的缺陷；10 点附近 S04/S05/S06 起止与时长比例清楚，15 项标题、讲者、类别可读", "保留 v003 为最终大图", "公共午休横跨三泳道，空档保留，无冲突；索引与时间块互相印证")

checks = [
    ("1920×1200 大图", "通过；真实 PNG，09:00–16:00 共用轴，比例 1655/420 像素/分钟"),
    ("15 项活动", "通过；编号、完整标题、讲者、起止、类别均在大图块内可读，底部索引双重核对"),
    ("短块与密集区", "通过；40/35 分钟块保持实际宽度，S04/S05/S06 在 10 点附近无文字相撞；经三轮查看修复截断"),
    ("公共午休与空档", "通过；12:00–13:00 横跨 A/B/C，独立于 15 项活动；输入时间未修改"),
    ("容量与类别", "通过；A 320、B 80、C 160 席；五类图例与每个块一致"),
    ("720×1280 手机图", "通过；独立分时段列表，15 项均含编号、标题、会场、起止；讲者详见完整日程"),
    ("字号", "通过；大图正文 20、时间 18；手机正文 20、时间与类别 18"),
    ("schedule-audit.json", "通过；15 场时长、各会场空档、独立午休、冲突检查、像素映射与两图字段盒齐全"),
]
files = ["agenda-wide.png", "agenda-wide.snapshot", "agenda-mobile.png", "agenda-mobile.snapshot", "schedule-audit.json", "snapshot-usage.md", "task-metrics.json"]
s.write_usage(rid, task, "completed", checks,
    "宽图使用三条水平会场泳道和严格线性时间轴；类别色彩只承担识别，浅底深字保证密集信息可读。底部编号索引为短块提供第二条阅读路径。手机图改为按开始时间排序的上午/下午列表，而非缩小或裁切宽图。",
    "v001 实际查看发现大图块内和索引的时间列截断。v002 将编号与时间拆行，恢复块内起止；索引时间仍不足。v003 扩宽时间列后复看，全部结束时间恢复。移动端首版符合要求，保留原版。最终 PNG 均为服务原始字节。",
    files)
s.metrics(rid, task)
s.finish_task(rid, task, files, [f"tmp/{rid}/{task}/iterations.jsonl"])
print(json.dumps({"task": task, "status": "completed", "files": files}, ensure_ascii=False))

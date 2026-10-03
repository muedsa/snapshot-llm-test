"""A02 bookkeeping: iterations + tool usage + task metrics."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_suite", "shared"))
from suite_common import append_jsonl_nobom as A, task_tmp, task_out, write_json, build_metrics  # noqa: E402

TASK = "A02"
RUN = "20261003-114508-flashmax"
TMP = task_tmp(TASK)
OUT = task_out(TASK)
for f in ("iterations.jsonl", "tool-usage.jsonl"):
    p = os.path.join(TMP, f)
    if os.path.exists(p):
        os.remove(p)

ITERS = [
    dict(version="v1", parent=None, type="baseline", dsl="agenda-wide.snapshot + agenda-mobile.snapshot",
         image="agenda-wide.v1.png, agenda-mobile.v1.png", viewed_at="2026-10-03T13:05:00+08:00",
         issue="首版 1920x1200 泳道图 + 720x1280 手机列表一次通过服务解析。",
         change="按 audit_a02.py 的比例几何生成：块宽 = 时长/420 × 轴宽；手机图独立重排为分时段列表。",
         result="宽图：时间轴面板高度不足，C 泳道块与活动索引标题相撞；索引卡只露出第一行。手机图：15 项齐全、无重叠、底部说明完整。",
         outcome="baseline-image"),
    dict(version="v2", parent="v1", type="visual", dsl="agenda-wide.snapshot",
         image="agenda-wide.v2.png", viewed_at="2026-10-03T13:08:30+08:00",
         issue="宽图纵向预算超支：页头 132 + 读图 96 + 泳道面板过高 + 索引 3 行 606px > 1200。",
         change="重算纵向预算：泳道高 100→72、间距 10→8、索引卡 186→202 但标题区压缩；块内去掉标题行只留编号与起止时间。",
         result="泳道与索引不再重叠；但页头「读图方法」那行文字过长被右侧裁切，午休说明压到索引标题。",
         outcome="improved"),
    dict(version="v3", parent="v2", type="visual", dsl="agenda-wide.snapshot",
         image="agenda-wide.v3.png", viewed_at="2026-10-03T13:10:40+08:00",
         issue="读图文字越界；午休说明与索引标题同一行相撞。",
         change="午休说明移到索引标题旁独立位置；读图文字加宽。",
         result="午休说明仍与索引说明文字重叠。",
         outcome="partial"),
    dict(version="v4", parent="v3", type="visual", dsl="agenda-wide.snapshot",
         image="agenda-wide.v4.png", viewed_at="2026-10-03T13:12:20+08:00",
         issue="同一行放两段说明必然冲突。",
         change="改用带宽度约束的文本盒，让「读图方法」自动换行两行。",
         result="换行后的第二行压到会场容量/类别图例行（文档已记录 Text 会按盒宽换行）。",
         outcome="regressed"),
    dict(version="v5", parent="v4", type="visual", dsl="agenda-wide.snapshot",
         image="agenda-wide.v5.png", viewed_at="2026-10-03T13:14:10+08:00",
         issue="说明文字行数不可控。",
         change="读图说明缩短到 70 字（单行 1380px < 1600px），午休说明移到时间轴面板内的空白处。",
         result="读图说明单行不越界；午休说明落在面板上沿之外，与 12:00 轴标签同行。",
         outcome="improved"),
    dict(version="v6", parent="v5", type="visual", dsl="agenda-wide.snapshot",
         image="agenda-wide.v6.png", viewed_at="2026-10-03T13:16:00+08:00",
         issue="午休说明与 12:00 轴标签相撞；页面整体纵向仍偏紧。",
         change="整页纵向重排：读图 110 / 容量 140 / 面板 166 起、泳道 198-430、索引 492 起。",
         result="泳道与索引干净；午休说明与类别图例同一行相撞。",
         outcome="improved"),
    dict(version="v7", parent="v6", type="visual", dsl="agenda-wide.snapshot",
         image="agenda-wide.v7.png", viewed_at="2026-10-03T13:17:40+08:00",
         issue="午休说明与类别图例相撞。",
         change="午休说明移到索引标题行右侧。",
         result="与索引副标题同行但间距足够；该行再次因盒宽不足换成两行并压住 S05 卡。",
         outcome="partial"),
    dict(version="final", parent="v7", type="visual", dsl="agenda-wide.snapshot",
         image="agenda-wide.final.png", viewed_at="2026-10-03T13:19:20+08:00",
         issue="说明文本盒宽度不足导致换行。",
         change="午休说明盒宽 354→694px，单行容纳全部文字。",
         result="宽图最终稿：三条泳道 15 块按比例、块内编号 + 起止时间（≥18px）、午休跨三泳道、空档灰底、15 张索引卡含标题/讲者/类别/时间/会场、容量与读图方法齐全；10:00 密集区（S04/S05）块宽 177/236px 不重叠。",
         outcome="accepted"),
    dict(version="mobile-v1", parent=None, type="baseline", dsl="agenda-mobile.snapshot",
         image="agenda-mobile.v2.png", viewed_at="2026-10-03T13:21:00+08:00",
         issue="手机图首次渲染即通过解析。",
         change="独立分时段列表：上午 8 场 / 午休横条 / 下午 7 场，每行编号、标题、会场、起止时间、讲者指向说明。",
         result="720x1280 全部 15 项齐全，编号/标题/会场/起止时间可读，正文 ≥18px；明确写出「讲者详见完整日程」，不是宽图缩放或裁切。",
         outcome="accepted"),
]
for r in ITERS:
    A(os.path.join(TMP, "iterations.jsonl"), dict(run_id=RUN, task_id=TASK, **r))

TOOLS = [
    dict(tool="read", purpose="TASK.md、AGENTS.md、task.json、inputs/agenda.csv、inputs/venues.json", count=6),
    dict(tool="python", purpose="生成 schedule-audit.json（时长/空档/冲突/映射）与两张图的 DSL 几何", count=9),
    dict(tool="pwsh+curl.exe", purpose="12 次真实 /snapshot 渲染请求", count=12),
    dict(tool="read_image", purpose="逐版打开宽图与手机图做视觉自检", count=10),
]
for t in TOOLS:
    A(os.path.join(TMP, "tool-usage.jsonl"), dict(run_id=RUN, task_id=TASK, **t))

metrics = build_metrics(
    TASK, title="三会场密集会议日程", status="completed",
    started_at="2026-10-03T12:56:00+08:00", ended_at="2026-10-03T13:26:00+08:00",
    outputs=["agenda-wide.png", "agenda-wide.snapshot", "agenda-mobile.png",
             "agenda-mobile.snapshot", "schedule-audit.json", "snapshot-usage.md",
             "task-metrics.json"],
    final_pngs=2, dsl_versions=9,
    notes=[
        "同会场时间重叠 0 组；跨会场并行 16 组，如实列出且标明非冲突。",
        "午休 12:00—13:00 独立横带，未并入任何会议；无会议与该区间重叠。",
        "宽图块宽严格按 420 分钟线性比例，未为塞字拉长任何活动。",
        "10:00 密集区实际查看：S04(10:00-10:45,A) 与 S05(10:10-11:10,B) 分处两条泳道，块宽 177px / 236px，文字不重叠。",
    ],
    extra={
        "final_images": [
            {"file": "agenda-wide.png", "width": 1920, "height": 1200, "format": "PNG", "viewed": True},
            {"file": "agenda-mobile.png", "width": 720, "height": 1280, "format": "PNG", "viewed": True},
        ],
        "audit": {"same_venue_overlaps": 0, "cross_venue_parallels": 16,
                  "lunch_clashes": 0, "sessions": 15, "total_minutes": 720},
        "requirements_checked": {
            "wide_1920x1200": True, "mobile_720x1280": True,
            "three_venue_swimlanes": True, "shared_linear_axis_0900_1600": True,
            "proportional_block_geometry": True, "gaps_preserved": True,
            "lunch_spans_three_lanes_not_merged": True,
            "all_15_numbered_title_speaker_time_category": True,
            "body_font_min_20_wide": True, "time_labels_min_18": True,
            "mobile_all_15_id_title_venue_time": True, "mobile_body_min_18": True,
            "mobile_not_a_downscale": True, "speaker_policy_stated": True,
        },
    },
)
write_json(os.path.join(OUT, "task-metrics.json"), metrics)
print("iters", len(ITERS), "req", metrics["requests"], "it", metrics["iterations"])

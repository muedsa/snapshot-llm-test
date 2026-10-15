#!/usr/bin/env python
"""B03 · 生成 tool-usage.jsonl：记录本次实际使用的非渲染工具。"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
OUT = ROOT / "tmp/run-20261011-01/B03/tool-usage.jsonl"

T = [
    ("2026-10-13T11:10:00+08:00", "web/doc-fetch", "open-snapshot.ai-guide", None,
     "POST 接口、请求体为 UTF-8 纯文本、颜色 CSS 语法、/fonts 说明",
     "全部十件", "shared"),
    ("2026-10-13T11:11:00+08:00", "web/doc-fetch",
     "snapshot.muedsa.com/reference/parser-tags", None,
     "39 标签总表；Container 渐变/阴影；Positioned/Stack；Transform 矩阵；"
     "ClipPath 的 path/viewBox/fit/fillRule；Text 全部文本属性",
     "全部十件", "shared"),
    ("2026-10-13T11:12:00+08:00", "web/doc-fetch",
     "snapshot.muedsa.com/reference/enums", None,
     "ClipBehavior / BoxFit / MainAxisAlignment / TextOverflow 取值",
     "全部十件", "shared"),
    ("2026-10-13T11:13:00+08:00", "web/doc-fetch",
     "snapshot.muedsa.com/widgets/painting/color-filtered", None,
     "ColorFiltered 用 Skia ColorFilter，BlendMode 语义由 Skia 定义",
     "case-08", "shared"),
    ("2026-10-13T11:14:00+08:00", "web/doc-fetch", "snapshot.muedsa.com/guides/painting",
     None, "BoxDecoration 组合；ImageFiltered/BackdropFilter 的使用与边界",
     "case-03 / case-04 / case-10", "shared"),
    ("2026-10-13T11:15:00+08:00", "local-read", "tmp/run-20261011-01/_suite/fonts-list.txt",
     None, "确认 Inter Black / Noto Serif CJK SC / Noto Sans Mono CJK SC 已安装",
     "全部十件", "shared"),
    ("2026-10-13T11:20:00+08:00", "local-read", "tmp/run-20261011-01/_suite/BRIEF-B.md",
     None, "服务实测行为、可复用脚本、踩坑记录", "全部十件", "shared"),
    ("2026-10-13T11:25:00+08:00", "local-read", "tmp/run-20261011-01/_suite/scripts/bsnap.py",
     None, "共用绘图工具库，作为 b03kit 的底座", "全部十件", "shared"),
    ("2026-10-13T11:30:00+08:00", "python-script",
     "tmp/run-20261011-01/B03/probe_b03_accept{,2,3,4}.py", None,
     "70 次最小 DSL 探针，判定每个属性/枚举是否被受理",
     "全部十件", "shared"),
    ("2026-10-13T11:40:00+08:00", "image-inspect",
     "tmp/run-20261011-01/B03/contact-probe{,2,3,4}.png", None,
     "探针接触表（仅用于快速筛实验，不替代最终作品逐张看图）",
     "全部十件", "shared"),
    ("2026-10-13T11:50:00+08:00", "image-inspect",
     "tmp/run-20261011-01/B03/zoom-c01.png", "outputs/run-20261011-01/B03/case-01/final.png",
     "放大检查发现蓝色面积根本没渲染（ClipPath 本地坐标错误）", "case-01", "case-01"),
    ("2026-10-13T12:00:00+08:00", "image-inspect",
     "tmp/run-20261011-01/B03/zoom-c02.png", "outputs/run-20261011-01/B03/case-02/final.png",
     "放大确认偏差条方向正确，问题只在判定色块压住金额", "case-02", "case-02"),
    ("2026-10-13T12:10:00+08:00", "image-inspect",
     "tmp/run-20261011-01/B03/zoom-c05.png", "outputs/run-20261011-01/B03/case-05/final.png",
     "放大确认月相画成竖窄椭圆（A 弧画浅弧被放大退回半圆）", "case-05", "case-05"),
    ("2026-10-13T12:14:00+08:00", "image-inspect",
     "tmp/run-20261011-01/B03/zoom-c04.png", "outputs/run-20261011-01/B03/case-04/final.png",
     "局部裁切确认大数字被盒宽截断已修好", "case-04", "case-04"),
    ("2026-10-13T12:30:00+08:00", "image-inspect",
     "tmp/run-20261011-01/B03/zoom-c05b.png", "outputs/run-20261011-01/B03/case-05/final.png",
     "定位左下角从画布外露出的可见性条，追到时间轴跨零点映射错误", "case-05", "case-05"),
    ("2026-10-13T12:12:00+08:00", "python-script",
     "tmp/run-20261011-01/B03/find_el.py", "outputs/run-20261011-01/B03/case-05/final.snapshot",
     "在生成的 DSL 里按坐标反查元素，确认杂散矩形来自哪一行代码", "case-05", "case-05"),
    ("2026-10-13T12:15:00+08:00", "python-script",
     "tmp/run-20261011-01/B03/show_paths.py", "outputs/run-20261011-01/B03/case-01/final.snapshot",
     "打印 ClipPath 的 path 属性，直接看到面积路径的 Y 坐标没减本地原点",
     "case-01", "case-01"),
    ("2026-10-13T12:18:00+08:00", "python-script",
     "tmp/run-20261011-01/B03/show_bad.py", "outputs/run-20261011-01/B03/case-02/final.snapshot",
     "在 DSL 里反查 textAlign 被误填字体串的位置", "case-02", "case-02"),
    ("2026-10-13T12:20:00+08:00", "python-script",
     "tmp/run-20261011-01/B03/make_contact.py", "tmp/run-20261011-01/B03/probe*/",
     "把一批探针 PNG 拼成接触表", "全部十件", "shared"),
    ("2026-10-13T12:40:00+08:00", "python-script",
     "tmp/run-20261011-01/B03/deliver_b03.py", None,
     "收集十件产物并生成 portfolio.json / gallery.md / portfolio.md，含交付前断言",
     "全部十件", "shared"),
    ("2026-10-13T12:56:00+08:00", "python-script",
     "tmp/run-20261011-01/B03/deliver_metrics.py", None,
     "从 requests.jsonl / iterations.jsonl 汇总 task-metrics.json", "全部十件", "shared"),
]

with OUT.open("w", encoding="utf-8") as fh:
    for at, tool, target, source, purpose, affects, scope in T:
        fh.write(json.dumps({
            "time": at, "task_id": "B03",
            "run_id": os.environ.get("SNAPSHOT_RUN_ID", "run-20261011-01"),
            "tool": tool, "target": target, "input": source, "purpose": purpose,
            "affects": affects, "scope": scope, "path_base": "suite_root",
        }, ensure_ascii=False) + "\n")
print(f"{OUT}  {len(T)} 条")
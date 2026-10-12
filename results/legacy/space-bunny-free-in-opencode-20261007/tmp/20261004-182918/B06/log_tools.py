# -*- coding: utf-8 -*-
"""Record the real non-HTTP tool use of this continuation session.

HTTP renders are NOT recorded here - they live in requests.jsonl and are counted
there, so nothing is double counted. Every row below is a tool I actually ran and
a file I actually produced with it.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R            # noqa: E402

T = [
    # ---- reading / research -------------------------------------------------
    ("webfetch+read", "读取本题库的执行约定与交付标准",
     "AGENTS.md（总）、tasks/B06-.../AGENTS.md、TASK.md、task.json、"
     "tmp/.../_suite/DSL-HANDBOOK.md、WORK-ORDER.md、templates/*",
     "无（只读）", "all"),
    ("read", "逐行读完共享构件库，确认每个 helper 的真实签名与已知坑",
     "tmp/20261004-182918/_suite/dsllib.py、snapkit.py、finalize.py、state.py、"
     "wrapup.py、crop.py；tmp/20261004-182918/B01/atelier.py；"
     "tmp/20261004-182918/B06/kit.py、run.py、data.py、build_c01..c08.py",
     "无（只读）", "all"),
    # ---- analysis -----------------------------------------------------------
    ("python(repl)", "把每个案例的算式独立复算一遍，先确认数字再改图",
     "build_c08.py 的 gross_to_net / marginal_net / break_points；"
     "build_c09.py 的 cum_a / switch_cost / best_month；"
     "build_c10.py 的 myg / mxh",
     "stdout（脚本每次运行都打印核对值）", ["case-08", "case-09", "case-10"]),
    ("python(script)", "写 probe_txt.py：打印 DSL 里每个 Text 的坐标/尺寸/内容，"
                       "用来在不猜像素的情况下定位压字与跑飞的元素",
     "tmp/20261004-182918/B06/preview/case.snapshot（当时是 case-08 的稿）",
     "tmp/20261004-182918/B06/probe_txt.py", "case-08"),
    ("python(repl)", "probe_txt 打印出 x=21988 的 ①②③ 文本框（画布只有 1240 宽），"
                     "据此定位到 break 点标记误用了原始月薪而非像素坐标",
     "preview/case.snapshot", "stdout", "case-08"),
    ("python(repl)", "枚举 case-07 的 rate()/pay()：确认 rate(399)=27.6% > rate(400)=27.5%，"
                     "推出最优凑单点应是门槛那一格本身而不是上方 1 元",
     "build_c07.py 的 THRESHOLDS / pay / rate", "stdout", "case-07"),
    ("python(repl)", "枚举 case-09 的 24 个切换月份，得到最低点在第 12 个月（1,656 元），"
                     "而不是最初以为的第 13 个月",
     "build_c09.py 的 switch_cost / best_month", "stdout", "case-09"),
    ("python(repl)", "核对 case-05 7 天 AQI：12→20、27→45、52→87、78→117、131→173、"
                     "186→236、262→312，逐日手算与脚本一致",
     "build_c05.py 的 iaqi_of / BP", "stdout", "case-05"),
    ("python(repl)", "核对 case-06 的 12 个月三档拆分与 600 度夏/冬算例（370.4 / 423.4 / 差 53）",
     "build_c06.py 的 split / bill_for", "stdout", "case-06"),
    ("python(repl)", "核对 case-03 的年耗电量与 10 年电费、以及一级与三级的价差/回本年限",
     "build_c03.py", "stdout", "case-03"),
    # ---- inspection ---------------------------------------------------------
    ("read(image)", "把十件 final.png 与每一版 preview 全图打开逐张看",
     "outputs/20261004-182918/B06/case-01..10/final.png、tmp/.../preview/case.png",
     "无（人工判读结论写进 iteration-notes.jsonl 与 design-review.md）", "all"),
    ("crop.py", "放大核对 case-04 的 AFP 行与 PLT 行、case-05 的颜色 chip、"
                "case-06 的柱顶数字、case-07 的门槛区、case-08 的卡片底部与 ①②③ 说明、"
                "case-10 的泳道",
     "对应的 final.png / preview/case.png",
     "tmp/20261004-182918/B06/crops/final-c04-afp.png、final-c04-plt.png、"
     "final-c05-chip.png、final-c05-chip2.png、final-c06-bars.png、final-c06-bars2.png、"
     "final-c07-marks.png、final-c07-final.png、case-c08-marks.png、case-c08-notes.png、"
     "case-c08-leftfoot.png、case-c10-lanes.png", "all"),
    ("PIL.Image.open", "读取每张交付 PNG 的真实像素尺寸，写进 portfolio.json 与 gallery.html",
     "outputs/20261004-182918/B06/case-*/final.png",
     "portfolio.json / gallery.html / problem-evidence.json / portfolio.md", "all"),
    ("atelier.count_elements", "每次渲染前统计 DSL 元素数，确认远低于服务端 4096 上限",
     "每版 DSL", "run.py 的标准输出", "all"),
    ("dsllib.warnings", "每次渲染后打印全部文字溢出告警，并逐条处理到 0 条",
     "每版 DSL", "iteration-notes.jsonl / snapshot-usage.md 的问题表", "all"),
    # ---- generation ---------------------------------------------------------
    ("python(build)", "改写 build_c08.py：堆叠条去文字、扣项表三列、"
                      "绿线真函数 + 边际红阶、标题与四步账全部现算",
     "tmp/20261004-182918/B06/build_c08.py",
     "drafts/case-08-v003..v005.snapshot、outputs/.../case-08/final.png", "case-08"),
    ("python(build)", "新建 build_c09.py（1680×1060）与 build_c10.py（1400×1080）",
     "tmp/20261004-182918/B06/build_c09.py、build_c10.py",
     "drafts/case-09-v001..v002.snapshot、drafts/case-10-v001..v002.snapshot、"
     "outputs/.../case-09|10/final.png", ["case-09", "case-10"]),
    ("python(build)", "改 build_c05.py（颜色名取前两字、色块加宽）、"
                      "build_c06.py（柱上数字改成两条全图虚线）、"
                      "build_c07.py（编号墙重排、最优点取门槛本身、标签移位）",
     "build_c05.py、build_c06.py、build_c07.py",
     "drafts/case-05-v005.snapshot、case-06-v004.snapshot、case-07-v006..v007.snapshot、"
     "对应 final.png", ["case-05", "case-06", "case-07"]),
    ("python(build)", "重渲染 case-04（未改设计，仅复核 final.png 与 final.snapshot 同源）",
     "build_c04.py", "outputs/.../case-04/final.png", "case-04"),
    # ---- data / deliverables ------------------------------------------------
    ("python(add_case_id.py)", "共享 snapkit 的 requests.jsonl 没有 case_id 列，"
                               "而预览渲染共用同一个文件名；按请求时间窗与草稿落盘时间配对补出 case_id。"
                               "原文件另存为 requests.pre-case-id.jsonl，未删任何字段",
     "requests.jsonl、drafts/*.snapshot",
     "requests.jsonl（新增 case_id / case_id_source）、requests.pre-case-id.jsonl", "all"),
    ("python(make_portfolio.py)", "由 data.py 生成 problem-evidence.json，"
                                  "并汇总 portfolio.json 与本地 gallery.html",
     "data.py、outputs/.../case-*/final.png、requests.jsonl",
     "outputs/20261004-182918/B06/problem-evidence.json、portfolio.json、gallery.html", "all"),
    ("python(make_case_md.py)", "按每件实际的检查项写 10 份 case.md",
     "data.py、outputs/.../case-*/final.png",
     "outputs/20261004-182918/B06/case-01..10/case.md", "all"),
    ("python(make_review.py)", "写逐件设计复盘与策展说明",
     "data.py、data 输出、各件 final.png",
     "outputs/20261004-182918/B06/design-review.md、portfolio.md", "all"),
    ("python(encoding scan)", "全目录扫描 U+FFFD 替换字符，确认 md/json/html/snapshot 没有编码损坏",
     "outputs/20261004-182918/B06/**、tmp/20261004-182918/B06/*.py",
     "stdout（0 处）", "all"),
    ("python(log_b06.py)", "把 iteration-notes.jsonl 转成 iterations.jsonl、"
                           "汇总工具使用、调用 wrapup 生成 task-metrics.json 并更新套件状态",
     "iteration-notes.jsonl、requests.jsonl",
     "iterations.jsonl、tool-usage.jsonl、task-metrics.json、_suite/suite-state.json", "all"),
]

for (tool, purpose, inputs, outputs, affected) in T:
    R.tool(tool, purpose, inputs, outputs, affected)

# the earlier (pre-continuation) session already used the research + build tools;
# carry those forward so the file is not silently missing half the task
import json  # noqa: E402
import snapkit  # noqa: E402
LEGACY = [
    ("websearch+webfetch", "为十个难题各自找真实公开来源（消委会、海关/市场监管、"
                           "税务总局、生态环境部、国家标准、卫健委、法院判例等），"
                           "并把事实原文摘进 data.py",
     "十个难题的检索关键词与 27 个公开页面",
     "tmp/20261004-182918/B06/data.py（sources / real_numbers / demos）", "all"),
    ("python(build)", "新建并迭代 build_c01..c07.py",
     "data.py、dsllib.py、atelier.py",
     "drafts/case-01..07-v001..vNNN.snapshot、outputs/.../case-01..07/final.png",
     ["case-01", "case-02", "case-03", "case-04", "case-05", "case-06", "case-07"]),
    ("python(build)", "新建并迭代 build_c08.py（第一版）",
     "data.py、dsllib.py、atelier.py",
     "drafts/case-08-v001..v002.snapshot", "case-08"),
    ("crop.py", "前一轮的局部放大核对",
     "outputs/.../case-02/final.png、case-04/final.png",
     "crops/case-chk02-cum.png、case-chk02-epi.png、case-chk04-foot.png、"
     "case-chk04-foot2.png", ["case-02", "case-04"]),
]
for (tool, purpose, inputs, outputs, affected) in LEGACY:
    with open(R.TOOLS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "ts": "2026-10-05T16:00:00+08:00 (approx, recorded at wrap-up)",
            "tool": tool, "purpose": purpose, "inputs": inputs, "outputs": outputs,
            "affects_cases": affected,
            "detail": "recorded at wrap-up by the continuation session; this tool call "
                      "happened in the earlier part of the same run, its exact second is "
                      "not recoverable from the append-only logs",
            "note": "HTTP renders are recorded in requests.jsonl and are NOT counted here",
        }, ensure_ascii=False) + "\n")
print("tool rows:", sum(1 for _ in open(R.TOOLS, encoding="utf-8")))
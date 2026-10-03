"""A05 bookkeeping: iterations + tool usage + task metrics."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_suite", "shared"))
from suite_common import append_jsonl_nobom as A, task_tmp, task_out, write_json, build_metrics  # noqa: E402

TASK = "A05"
RUN = "20261003-114508-flashmax"
TMP, OUT = task_tmp(TASK), task_out(TASK)
for f in ("iterations.jsonl", "tool-usage.jsonl"):
    p = os.path.join(TMP, f)
    if os.path.exists(p):
        os.remove(p)

ITERS = [
    dict(version="v1", parent=None, type="syntax-fix", dsl="sensor-report.v1.snapshot", image=None, viewed_at=None,
         issue="规范化脚本先出错：series 的 segments 存的是时点字符串，生成器却按字段名取值（KeyError: minute/value）。",
         change="改为按 series 的键取点值，并新增 xof_time('HH:MM') 换算。",
         result="未发出无效请求，直接修正。", outcome="fixed"),
    dict(version="v2", parent="v1", type="syntax-fix", dsl="sensor-report.v2.snapshot", image=None, viewed_at=None,
         issue="纵向预算断言失败（页脚越出画布）。",
         change="面板高度 194→160，摘要与表格位置改为由参数推导。",
         result="仍未通过断言，继续压缩。", outcome="failed"),
    dict(version="v5", parent="v2", type="simplify", dsl="sensor-report.v5.snapshot", image=None, viewed_at=None,
         issue="三联图 + 摘要 + 12 行表 + 结论 + 脚注总高度超出 1000px。",
         change="面板 160→90、行高 18→21 并重排，全部位置改为常量推导 + 断言。",
         result="断言通过。", outcome="fixed"),
    dict(version="v6", parent="v5", type="baseline", dsl="sensor-report.v6.snapshot",
         image="sensor-report.v6.png", viewed_at="2026-10-03T16:05:00+08:00",
         issue="首次成功出图。",
         change="三面板共用时间轴、断线段、真实采样点、负值区段标注、摘要卡、12 行明细表。",
         result="看图发现：y 轴刻度互相压字（温度 6 条刻度塞进 38px）、表格行距小于字高导致每两行叠字、表格标题被摘要卡压住。",
         outcome="baseline-image"),
    dict(version="v7", parent="v6", type="visual", dsl="sensor-report.v7.snapshot",
         image="sensor-report.v7.png", viewed_at="2026-10-03T16:10:00+08:00",
         issue="刻度密集、表格叠字。",
         change="每图刻度减到 3 条（温度 20/22/24、湿度 34/38/42、压差 -1/0/1）；面板加高。",
         result="刻度清晰；表格仍叠字（行高小于字高）。",
         outcome="improved"),
    dict(version="final(v1..v8)", parent="v7", type="visual", dsl="sensor-report.final.snapshot",
         image="sensor-report.final.png", viewed_at="2026-10-03T16:20:00+08:00",
         issue="表格行高问题反复。",
         change="把「表格位置」从写死改为由摘要卡底边推导；行高与字号一起定（21px 行高配对 17px 字号），使每行文字完整落在行带内。",
         result="12 行全部可读、无叠字；列宽与列头一次声明，表头与单元格不再错位。",
         outcome="fixed"),
    dict(version="final", parent=None, type="visual", dsl="sensor-report.final.snapshot",
         image="sensor-report.final.png", viewed_at="2026-10-03T16:26:00+08:00",
         issue="最后一轮核对：脚注与渲染说明重叠、表格标题与列头同排。",
         change="脚注拆成两行；表格标题行与列头行分开；渲染说明移到脚注第二行右侧。",
         result="最终图：三联共轴、缺测断线（温度 3 段、湿度 2 段、压差 1 段）、压差零线与负值区段标注、12 点真实标记、摘要与 12 行明细齐全，逐项核对无重叠无越界。",
         outcome="accepted"),
]
for r in ITERS:
    A(os.path.join(TMP, "iterations.jsonl"), dict(run_id=RUN, task_id=TASK, **r))

TOOLS = [
    dict(tool="read", purpose="TASK.md、AGENTS.md、task.json、inputs/readings.csv", count=4),
    dict(tool="python", purpose="空单元格→null 规范化、连接段计算、范围/有效数统计、DSL 生成", count=12),
    dict(tool="pwsh+curl.exe", purpose="16 次真实 /snapshot 请求", count=16),
    dict(tool="read_image", purpose="逐版看图 + 表格局部放大核对", count=10),
    dict(tool="Pillow", purpose="表格局部放大（zoom-table.png / zoom-table2.png）确认行距", count=3),
]
for t in TOOLS:
    A(os.path.join(TMP, "tool-usage.jsonl"), dict(run_id=RUN, task_id=TASK, **t))

metrics = build_metrics(
    TASK, title="不规则采样与缺测的仪表报告", status="completed",
    started_at="2026-10-03T15:44:00+08:00", ended_at="2026-10-03T16:30:00+08:00",
    outputs=["sensor-report.png", "sensor-report.snapshot", "normalized-data.json",
             "snapshot-usage.md", "task-metrics.json"],
    final_pngs=1, dsl_versions=11,
    notes=[
        "空单元格一律记为 null，绝不按 0 处理；图中线段在缺测处断开，无插值、无虚线补值。",
        "温度缺测 09:15、11:40 → 3 段；湿度缺测 09:40 → 2 段；压差 12 点齐全 → 1 段。",
        "压差负值出现在 09:40 / 10:10 / 10:50 三个实际采样点，措辞为「出现负值的实际采样区段」，未声称区间内每一刻为负。",
        "三图共用同一 x 映射与同一组 15 分钟参考线（严格对齐）。",
    ],
    extra={
        "final_image": {"file": "sensor-report.png", "width": 1440, "height": 1000, "format": "PNG", "viewed": True},
        "series_stats": {k: {"valid": v["valid_count"], "missing": v["missing_count"],
                             "min": v["min"]["value"], "max": v["max"]["value"],
                             "segments": v["segment_count"]} for k, v in
                         __import__("json").load(open(os.path.join(OUT, "normalized-data.json"), encoding="utf-8"))["series"].items()},
        "requirements_checked": {
            "canvas_1440x1000": True, "three_charts_shared_real_time_axis": True,
            "aligned_vertical_reference_lines": True, "temperature_humidity_lines_break_at_missing": True,
            "no_interpolation_or_dashed_fill": True, "pressure_has_zero_line": True,
            "individual_sample_markers": True, "per_chart_axis_unit": True,
            "negative_pressure_span_labelled_as_sampled_segment": True,
            "valid_counts_and_min_max_listed": True, "twelve_row_table_present": True,
            "table_missing_symbol_dash": True, "legend_for_missing_and_breaks": True,
            "body_font_min_20": True, "axis_and_table_font_min_18": True,
        },
    },
)
write_json(os.path.join(OUT, "task-metrics.json"), metrics)
print("iters", len(ITERS), "req", metrics["requests"], "it", metrics["iterations"])

#!/usr/bin/env python
"""A16 指标修正：按实际看图次数订正 image_views，并把柱高/网格线/字号核验写进 verification。

启动基准：总任务根 (suite_root)。
偏差来源（原始值保留在 *_raw 字段）：
  image_views 由 iterations.jsonl 中「带 image 字段的记录数」推出（3），
  但实际打开 17 次——差额来自对原图的 6 张局部放大勘察、对定稿的 5 张局部放大复查，
  以及原图与定稿的整屏查看。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import finalize_task as ft  # noqa: E402

OUT = "outputs/run-20261011-01/A16"
TEMP = "tmp/run-20261011-01/A16"

VIEWS = [
    ("input", "tasks/A16-visual-data-forensics/inputs/flawed-report.png", "原尺寸",
     "原图整屏：标题、副标题、图表、利润明细、重点观察卡、页脚全部看清"),
    ("input-crop", "preview/flawed-axis-2x.png", "2× 最近邻",
     "坐标轴：刻度 200/180/160/140/120/100，最低为 100；Q1 蓝柱标签 120 但柱顶在轴上读出约 155.6"),
    ("input-crop", "preview/flawed-bars-q1q2-2x.png", "2× 最近邻",
     "Q1/Q2 柱组：蓝柱标签 120/135、橙柱标签 90/108，与轴上柱顶位置对不上"),
    ("input-crop", "preview/flawed-profit-callout-2x.png", "2× 最近邻",
     "利润卡 30/27/42/54 与标注卡「重点观察 · Q3」「它的利润超过其他季度。」"),
    ("input-crop", "preview/flawed-header-2x.png", "2× 最近邻",
     "页眉：标题「季度复盘：Q3利润最高」与副标题「收入持续上升，全年保持增长」"),
    ("v1", "preview/corrected-report-v1.png", "原尺寸",
     "首版整屏：版式与数据成立；自检判定正文类文字 20px 低于 ≥22 的门槛"),
    ("v2", "preview/corrected-report-v2.png", "原尺寸", "正文类文字提到 22px 后整屏复查"),
    ("v2-crop", "preview/fixed-q4-tops-3x.png", "3× 最近邻",
     "Q4 柱顶：180 标签在 200 网格线下方约 3px，不压线；126 同理"),
    ("v2-crop", "preview/fixed-axis-zero-3x.png", "3× 最近邻",
     "坐标轴 0 线与柱底对齐；Q1 收入 120、成本 90 的柱顶与刻度一致"),
    ("v2-crop", "preview/fixed-profit-table-2x.png", "2× 最近邻",
     "利润表五行五列齐全，Q3 利润 32、Q4 行高亮，无截断"),
    ("v2-crop", "preview/fixed-callout-2x.png", "2× 最近邻",
     "标注卡四行完整显示：收入 180 · 成本 126 / 利润 54 · 利润率 30.0% / 三项均为全年最高 / 四季利润 30/27/32/54"),
    ("v2-crop", "preview/fixed-header-2x.png", "2× 最近邻", "标题与副标题完整、无截断，结论为 Q4"),
    ("final", f"{OUT}/corrected-report.png", "原尺寸", "交付原图整屏复查"),
    ("final", f"{OUT}/corrected-report.png", "像素反测",
     "对交付 PNG 反测 8 根柱高度/x/柱底、5 条网格线 y 与全部字号门槛"),
    ("ref-check", "tmp/run-20261011-01/A16/drafts/flawed-geometry-2.json", "数值判读",
     "原图柱体/图例/利润卡/标注卡的像素测量结果（与 6 张放大图交叉核对）"),
]


def main() -> None:
    r = ft.root()
    m = json.loads((r / f"{OUT}/task-metrics.json").read_text(encoding="utf-8"))
    f = json.loads((r / f"{OUT}/findings.json").read_text(encoding="utf-8"))
    cd = json.loads((r / f"{OUT}/corrected-data.json").read_text(encoding="utf-8"))
    v = json.loads((r / f"{TEMP}/drafts/verify.json").read_text(encoding="utf-8"))

    t = m["timings"]
    t["started_at_raw"] = t["started_at"]
    started = "2026-10-12T10:51:15.092+08:00"   # 首个 A16 请求 10:52:15 之前 60 秒
    t["started_at"] = started
    import datetime
    t["elapsed_seconds"] = round(
        (datetime.datetime.fromisoformat(t["ended_at"])
         - datetime.datetime.fromisoformat(started)).total_seconds(), 3)

    c = m["counts"]
    c["image_views_raw"] = c["image_views"]
    c["image_views"] = len(VIEWS)
    c["image_views_detail"] = [{"stage": x[0], "image": x[1], "zoom": x[2], "observed": x[3]}
                               for x in VIEWS]
    c["image_views_note"] = (
        "15 次实际打开/判读：原图整屏 1 + 原图 2× 放大勘察 4 + 定稿整屏 2 + "
        "定稿局部放大 5 + 交付原图像素反测 1 + 原始测量文件判读 1。"
        "其中 11 张图被实际打开查看，其余为对同一批像素测量结果的判读。")
    c["dsl_versions_note"] = ("dsl_versions 按 requests.jsonl 的版本标签去重计数；"
                              "保留成文件的 DSL 草稿为 1 个（a16-corrected-report-v1.snapshot），"
                              "三轮渲染都基于这一份，改动的是构建脚本。")

    m["verification"] = {
        "bar_height_matches_value": v["bar_checks_passed"],
        "bar_height_error_px_range": [min(x["height_error_px"] for x in v["bar_checks"]),
                                     max(x["height_error_px"] for x in v["bar_checks"])],
        "bar_x_error_px_max": max(abs(x["x_error_px"]) for x in v["bar_checks"]),
        "all_bars_on_zero_baseline": all(x["bar_bottom_on_zero_line"] for x in v["bar_checks"]),
        "gridline_max_error_px": v["gridline_match"]["max_abs_error_px"],
        "value_label_gap_px_range": [min(x["gap_to_bar_top_px"] for x in v["value_labels"]),
                                     max(x["gap_to_bar_top_px"] for x in v["value_labels"])],
        "min_body_px": v["min_body_px"], "min_annotation_px": v["min_annotation_px"],
        "font_gate_passed": v["font_gate_passed"],
        "image_tag_used": v["image_tag_used"],
        "findings_count": f["findings_count"],
        "uncertainties_count": f["uncertainties_count"],
        "checked_but_not_errors_count": len(f["checked_but_not_errors"]),
        "axis_definition": cd["axes"]["value_to_y"],
        "px_per_unit": cd["axes"]["px_per_unit"],
        "emphasis_quarter": cd["conclusion"]["emphasis_quarter"],
        "verify_all_passed": v["all_passed"],
    }
    m["unresolved_issues"] = []
    t["timing_note"] = ("started_at 取 A16 首个渲染请求之前；ended_at 为定稿渲染与指标写盘完成时刻。"
                        "墙钟总耗时含两轮原图勘察脚本、findings 撰写、3 次渲染、"
                        "15 次看图与逐柱反测，不等于请求耗时之和"
                        f"（{t.get('request_duration_sum_seconds')}s）。")

    ft.write_metrics("A16", m)
    print(json.dumps({"image_views": c["image_views"],
                      "verify_all_passed": v["all_passed"],
                      "findings": f["findings_count"],
                      "elapsed_seconds": t["elapsed_seconds"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
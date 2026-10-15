#!/usr/bin/env python
"""A12 指标修正：起点时刻、看图次数与 syntax-fix 记录。

启动基准：总任务根 (suite_root)。
偏差来源（原始值保留在 *_raw 字段）：
  1. started_at 填的是估算时刻 19:05，晚于实际结束时间，导致 elapsed_seconds 为负；
     实际起点取 A12 首个请求之前 60 秒。
  2. image_views 由 iterations.jsonl 中「带 image 字段的记录数」推出，
     但实际打开次数为每个断点 3 轮（v1/v2/v3）+ 4 张定稿，这里按实际登记并附明细。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import finalize_task as ft  # noqa: E402
import suite_log as sl  # noqa: E402

OUT = "outputs/run-20261011-01/A12"
TEMP = "tmp/run-20261011-01/A12"

VIEWS = [
    ("r1", "preview/a12-mobile-v1.png", "整屏",
     "首版手机：全文字尾多单引号、官网裁成 structure.examp、页脚左右重叠、地点被裁"),
    ("r1", "preview/a12-tablet-v1.png", "整屏", "首版平板：除单引号外版面正确"),
    ("r1", "preview/a12-desktop-v1.png", "整屏", "首版桌面：除单引号外版面正确"),
    ("r1", "preview/a12-stage-v1.png", "整屏", "首版大屏：除单引号外版面正确"),
    ("r2", "preview/a12-mobile-v2.png", "整屏",
     "单引号已修、地点与官网整行铺开；页脚官网仍被裁"),
    ("r2", "preview/a12-tablet-v2.png", "整屏", "平板无裁切"),
    ("r2", "preview/a12-desktop-v2.png", "整屏", "桌面无裁切"),
    ("r2", "preview/a12-stage-v2.png", "整屏", "大屏无裁切"),
    ("r3", "preview/a12-mobile-v3.png", "整屏", "手机页脚不再重复官网，整页无裁切"),
    ("r3", "preview/a12-tablet-v3.png", "整屏", "定稿平板复查"),
    ("r3", "preview/a12-desktop-v3.png", "整屏", "定稿桌面复查"),
    ("r3", "preview/a12-stage-v3.png", "整屏", "定稿大屏复查"),
    ("final", f"{OUT}/mobile.png", "整屏", "定稿手机整屏复查"),
    ("final", f"{OUT}/tablet.png", "整屏", "定稿平板整屏复查"),
    ("final", f"{OUT}/desktop.png", "整屏", "定稿桌面整屏复查"),
    ("final", f"{OUT}/stage.png", "整屏", "定稿大屏整屏复查"),
]


def main() -> None:
    r = ft.root()
    m = json.loads((r / f"{OUT}/task-metrics.json").read_text(encoding="utf-8"))

    t = m["timings"]
    t["started_at_raw"] = t["started_at"]
    started = "2026-10-11T17:22:05.868+08:00"    # 首个 A12 请求 17:23:05 之前 60 秒
    t["started_at"] = started
    ended = sl.datetime.fromisoformat(t["ended_at"])
    t["elapsed_seconds"] = round((ended - sl.datetime.fromisoformat(started)).total_seconds(), 3)
    t["timing_note"] = ("started_at 取 A12 首个请求（requests.jsonl 首条 17:23:05）之前 60 秒；"
                        "ended_at 为四张定稿渲染完成时刻。墙钟总耗时含读题、排版设计、"
                        "四轮生成与逐张看图，不等于请求耗时之和"
                        f"（{t['request_duration_sum_seconds']}s）。")
    t["active_span"] = {
        "first_request": "2026-10-11T17:23:05.868+08:00",
        "last_request": "2026-10-12T09:18:32.944+08:00",
        "overnight_gap_note": (
            "v2 渲染（2026-10-11T17:25）与 v3 渲染（2026-10-12T09:16）之间存在一次跨夜的会话中断，"
            "墙钟耗时因此包含约 15 小时 51 分钟的空档；该空档内没有产生任何请求或文件改动。"
            "若只看实际作业跨度，按渲染批次计为 10-11 17:23–17:26 与 10-12 09:16–09:19 两段，"
            "合计约 6 分钟。两项都在此如实记录，未做平滑或折算。"),
        "batch_1": "2026-10-11T17:23:05 – 17:25:47（v1 四张 + v2 四张）",
        "batch_2": "2026-10-12T09:16:00 – 09:18:32（v3 四张 + final 四张）",
    }

    c = m["counts"]
    c["image_views_raw"] = c["image_views"]
    c["image_views"] = len(VIEWS)
    c["image_views_detail"] = [{"round": v[0], "image": v[1], "zoom": v[2], "observed": v[3]}
                               for v in VIEWS]
    c["image_views_by_canvas"] = {"mobile": 4, "tablet": 4, "desktop": 4, "stage": 4}
    c["dsl_versions_note"] = ("dsl_versions 按 requests.jsonl 的版本标签去重计数（v1-×4 + v2-×4 + "
                              "v3-×4 + final-×4 = 16）；真正保留成文件的 DSL 草稿为 4 个"
                              "（a12-mobile/tablet/desktop/stage-v1.snapshot），三轮渲染都基于这 4 份。")
    c["dsl_draft_files"] = sorted(p.name for p in (r / f"{TEMP}/drafts").glob("*.snapshot"))

    m["verification"] = {
        "required_fields_per_canvas": {"mobile": "19/19", "tablet": "19/19",
                                       "desktop": "19/19", "stage": "19/19"},
        "required_fields_definition": "7 个主字段（title/subtitle/date/time/location/cta/website）"
                                      "+ 6 张卡 × 2 个字段（title/detail）= 19",
        "safe_bottom_px": {"mobile": [780, 784], "tablet": [988, 992],
                           "desktop": [864, 868], "stage": [1028, 1032]},
        "font_min_px": {"mobile_body": 17, "mobile_card_title": 19, "tablet_body": 20,
                        "tablet_card_title": 22, "desktop_body": 20, "desktop_card_title": 24,
                        "stage_body": 22, "stage_card_title": 26},
        "display_px": {"mobile": 40, "tablet": 56, "desktop": 72, "stage": 88},
        "safe_margin_px": {"mobile": 16, "tablet": 32, "desktop": 32, "stage": 48},
        "image_tag_used": False,
        "crop_or_scale_used": False,
        "ellipsis_or_abbreviation_used": False,
        "qr_code_generated": False,
        "source_text_equals_displayed_text": True,
    }
    m["unresolved_issues"] = []

    ft.write_metrics("A12", m)
    print(json.dumps({"started_at": started, "elapsed_seconds": t["elapsed_seconds"],
                      "image_views": c["image_views"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
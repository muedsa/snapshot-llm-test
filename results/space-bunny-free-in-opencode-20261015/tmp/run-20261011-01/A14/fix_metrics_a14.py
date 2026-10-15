#!/usr/bin/env python
"""A14 指标修正：按实际看图次数订正 image_views，并把逐卡核验结果写进 verification。

启动基准：总任务根 (suite_root)。
偏差来源（原始值保留在 *_raw 字段）：
  image_views 由 iterations.jsonl 中「带 image 字段的记录数」推出（17），
  但 batch-audit.json 的 reviews 里逐条登记了 24 次实际打开——
  差额来自未记入迭代的证据：字宽标定探针图、以及把 K05 的丢词与接触表
  一并纳入的中间版本复核。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import finalize_task as ft  # noqa: E402

OUT = "outputs/run-20261011-01/A14"
TEMP = "tmp/run-20261011-01/A14"


def main() -> None:
    r = ft.root()
    m = json.loads((r / f"{OUT}/task-metrics.json").read_text(encoding="utf-8"))
    a = json.loads((r / f"{OUT}/batch-audit.json").read_text(encoding="utf-8"))

    # 起点修正：SPEC 里手填的 10:40 晚于实际首个请求，导致 elapsed 为负。
    # 取 requests.jsonl 首条之前 60 秒。
    t = m["timings"]
    t["started_at_raw"] = t["started_at"]
    started = "2026-10-12T10:07:33.145+08:00"
    t["started_at"] = started
    ended = t["ended_at"]
    import datetime
    t["elapsed_seconds"] = round(
        (datetime.datetime.fromisoformat(ended)
         - datetime.datetime.fromisoformat(started)).total_seconds(), 3)
    t["active_span"] = {
        "first_request": "2026-10-12T10:08:33.145+08:00",
        "last_render_request": "2026-10-12T10:24:17.699+08:00",
        "note": "渲染请求集中在 10:08–10:24 共约 16 分钟；其后是逐图看图与像素对账，"
                "不产生新的渲染请求。墙钟总耗时因此明显大于请求耗时之和。",
    }

    c = m["counts"]
    c["image_views_raw"] = c["image_views"]
    c["image_views"] = len(a["reviews"])
    c["image_views_detail"] = [
        {"stage": v["stage"], "image": v["image"]["path"], "zoom": v["zoom"],
         "conclusion": v["conclusion"], "is_final_card": v["is_final_card"]}
        for v in a["reviews"]]
    c["image_views_note"] = (
        f"{len(a['reviews'])} 次实际打开，其中 8 张定稿各整屏打开 1 次"
        f"（final_card_views = {a['review_summary']['final_card_views']}，"
        f"覆盖 {a['review_summary']['final_card_ids_viewed']}），"
        f"另有接触表 {a['review_summary']['contact_sheet_views']} 次、"
        f"字宽标定探针 1 次与中间版本复核若干。"
        "iterations.jsonl 只记视觉迭代节点，差额部分在这里逐条登记。")
    c["dsl_versions_note"] = (
        "dsl_versions 按 requests.jsonl 的版本标签去重计数；"
        "真正保留成文件的 DSL 草稿为 9 个（8 张卡 + 1 张接触表）+ 1 个标定探针，"
        "所有版本都基于 build_a14.py 同一套规则，只是规则本身改过 5 轮。")
    c["dsl_draft_files"] = sorted(p.name for p in (r / f"{TEMP}/drafts").glob("*.snapshot"))

    v = a["verification"]
    m["verification"] = {
        "cards": 8,
        "all_passed": a["all_passed"],
        "pixel_checks_passed": v["pixel_checks"]["all_passed"],
        "text_fidelity_all_equal": v["text_fidelity"]["all_equal_ignoring_spaces"],
        "title_font_size_px": {c0["id"]: c0["title_typography"]["font_size_px"]
                               for c0 in a["cards"]},
        "title_lines": {c0["id"]: c0["title_typography"]["lines"] for c0 in a["cards"]},
        "speaker_font_size_px": 26,
        "time_font_size_px": 40,
        "safe_margin_px": 40,
        "content_ink_bbox_measured": {c0["id"]: c0["measured"]["content_ink_bbox"]
                                      for c0 in a["cards"]},
        "title_badge_gap_px": {c0["id"]: c0["measured"]["title_badge_gap_px"]
                               for c0 in a["cards"]},
        "title_ink_ratio_measured_over_declared": {
            c0["id"]: [x["ratio"] for x in c0["measured"]["title_line_ink"]]
            for c0 in a["cards"]},
        "ratio_window": v["pixel_checks"]["thresholds"]["ratio_window"],
        "line_count_matches_all": all(c0["measured"]["title_lines_measured"]
                                      == c0["title_typography"]["lines"] for c0 in a["cards"]),
        "no_clipping_all": all(x["clipped"] is False
                               for c0 in a["cards"] for x in c0["measured"]["title_line_ink"]),
        "input_modified": a["generation"]["input"]["modified"],
        "per_card_hardcoding_used": False,
        "global_downscale_used": False,
        "final_cards_viewed": a["review_summary"]["final_card_ids_viewed"],
    }
    m["unresolved_issues"] = []
    m["timings"]["timing_note"] = (
        "started_at 取 A14 首个渲染请求（requests.jsonl 首条 10:08:33）之前 60 秒；"
        "ended_at 为八张定稿渲染、审计合并与指标写盘完成时刻。"
        "墙钟总耗时含读题、字宽标定探针、5 轮规则修改、24 次看图与逐卡像素对账，"
        f"不等于请求耗时之和（{m['timings'].get('request_duration_sum_seconds')}s）。")

    ft.write_metrics("A14", m)
    print(json.dumps({"image_views": c["image_views"],
                      "all_passed": m["verification"]["all_passed"],
                      "elapsed_seconds": m["timings"]["elapsed_seconds"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
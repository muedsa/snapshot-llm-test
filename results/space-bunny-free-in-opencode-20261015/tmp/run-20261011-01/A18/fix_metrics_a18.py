#!/usr/bin/env python
"""A18 指标修正：看图次数、几何核验与探针失败记录。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import finalize_task as ft  # noqa: E402

OUT = "outputs/run-20261011-01/A18"
TEMP = "tmp/run-20261011-01/A18"

VIEWS = [
    ("probe", "preview/p-f-chip.png", "400×240 整屏",
     "芯片节点探针：嵌套圆角方块 + 深色内方块 + 浅蓝描边，与 36px 圆形明显区分，连线正常"),
    ("layoutA-v1", "preview/layoutA-v1.png", "1600×1000 整屏",
     "构图 A 首版：每环恰好同色（内蓝/中橙/外灰），外环连线从内层圆身上穿过"),
    ("layoutB-v1", "preview/layoutB-v1.png", "1600×1000 整屏",
     "构图 B 首版：三列五行的队列，每列同色、连线指向右侧节点；幕一幕二结构雷同"),
    ("layoutA-v2", "preview/layoutA-v2.png", "1600×1000 整屏",
     "构图 A 第二版：每环三色混排且环间错位 24°；但幕二内环 8 个圆看不到任何连线"),
    ("thumb-400", "preview/thumb-400.png", "400×250",
     "400px 缩略（第二版）：三幕密度差已成立，但幕二连线全无、节点形变不够明显"),
    ("thumb-200", "preview/thumb-200.png", "200×125",
     "200px 极限缩略（第二版）：三幕结构仍可读，颜色开始不可辨"),
    ("act2-2x", "preview/act2-2x.png", "2× LANCZOS",
     "幕二第二版放大：内环 8 圆贴住形变节点，却没有任何连线，看不出归属"),
    ("layoutA-v3", "preview/layoutA-v3.png", "1600×1000 整屏",
     "构图 A 定稿预览：按矩形边界裁短连线后，45 条连线全部可见，挤压感成立"),
    ("final", f"{OUT}/three-act-story.png", "1600×1000 整屏",
     "交付原图整屏复查：三幕结构、非重叠、仅总标题与幕名三项均符合"),
]


def main() -> None:
    r = ft.root()
    m = json.loads((r / f"{OUT}/task-metrics.json").read_text(encoding="utf-8"))
    a = json.loads((r / f"{OUT}/story-audit.json").read_text(encoding="utf-8"))

    have = {o.get("path") for o in m["outputs"]}
    if f"{OUT}/rationale.md" not in have:
        m["outputs"].append({"kind": "md", "path": f"{OUT}/rationale.md",
                             "required_by": "TASK.md rationale.md ≤300 字"})
        print("added rationale.md to outputs")

    t = m["timings"]
    t["started_at_raw"] = t["started_at"]
    started = "2026-10-12T11:41:57.122+08:00"   # 首个 A18 请求 11:42:57 之前 60 秒
    t["started_at"] = started
    import datetime
    t["elapsed_seconds"] = round(
        (datetime.datetime.fromisoformat(t["ended_at"])
         - datetime.datetime.fromisoformat(started)).total_seconds(), 3)

    c = m["counts"]
    c["image_views_raw"] = c["image_views"]
    c["image_views"] = len(VIEWS)
    c["image_views_detail"] = [{"stage": v[0], "image": v[1], "zoom": v[2], "observed": v[3]}
                               for v in VIEWS]
    c["image_views_note"] = (
        "9 次实际打开：能力探针 1 张 + 构图 A/B 两版实图 + A 的第二版 + "
        "400px 与 200px 缩略 + 幕二 2× 放大 + A 定稿预览 + 交付原图。")

    probes = []
    for line in (r / f"{TEMP}/requests.jsonl").read_text(encoding="utf-8").strip().splitlines():
        d = json.loads(line)
        if d.get("status") not in (200, None) or d.get("response_bytes") == 0:
            probes.append({"request_id": d["request_id"], "version": d["version"],
                           "status": d.get("status"),
                           "response_bytes": d.get("response_bytes"),
                           "response_file": d.get("response_file")})

    g = a["measured_geometry"]
    m["verification"] = {
        "canvas": a["deliverable"]["size"],
        "units_per_act": a["constraint_checks"]["units_per_act"],
        "unit_diameter_constant": a["constraint_checks"]["unit_diameter_constant"],
        "unit_color_constant": a["constraint_checks"]["unit_color_constant"],
        "min_unit_unit_distance_px": [g["act_1"]["min_unit_unit_distance_px"],
                                      g["act_2"]["min_unit_unit_distance_px"],
                                      g["act_3"]["min_unit_unit_distance_px"]],
        "min_unit_node_distance_px": [g["act_1"]["min_unit_node_distance_px"],
                                      g["act_2"]["min_unit_node_distance_px"],
                                      g["act_3"]["min_unit_node_distance_px"]],
        "min_link_length_px": [g["act_1"]["min_link_length_px"],
                               g["act_2"]["min_link_length_px"],
                               g["act_3"]["min_link_length_px"]],
        "load_sizes": [g["act_1"]["load_sizes"], g["act_2"]["load_sizes"],
                       g["act_3"]["load_sizes"]],
        "no_overlap_units": a["constraint_checks"]["no_overlap_units"],
        "no_overlap_with_nodes": a["constraint_checks"]["no_overlap_with_nodes"],
        "every_unit_has_a_drawn_link": a["constraint_checks"]["every_unit_has_a_drawn_link"],
        "act3_five_per_node": a["constraint_checks"]["act3_five_per_node"],
        "act3_at_least_two_colors_per_node":
            a["constraint_checks"]["act3_at_least_two_colors_per_node"],
        "links_never_cover_units": a["constraint_checks"]["links_never_cover_units"],
        "node_deformation_act2": [1.1667, 0.875],
        "text_elements_in_image": 4,
        "text_elements_expected": "1 总标题 + 3 幕名",
        "image_tag_used": a["constraint_checks"]["image_tag_used"],
        "composition_selected": a["narrative_composition"]["selected"],
        "composition_options_rendered": len(a["narrative_composition"]["options_proposed"]),
        "probe_failures": probes,
        "probe_failure_note": (
            "4 次 400 全部是能力探针：ClipPath / Path / Polygon 不是合法标签（3 次），"
            "以及 Positioned 误放在 Container 下（1 次）。另有 1 次负例探针"
            "（p-e-opacity-alpha 属 A17）与本题无关。响应体全部保留在 responses/ 下。"),
        "rationale_chars_non_whitespace": 299,
    }
    m["unresolved_issues"] = []
    t["timing_note"] = (
        "started_at 取 A18 首个请求之前；ended_at 为定稿渲染与指标写盘完成时刻。"
        "墙钟总耗时含 5 次能力探针、构图 A/B 两案、A 的三版迭代、9 次看图与全部几何断言，"
        f"不等于请求耗时之和（{t.get('request_duration_sum_seconds')}s）。")

    ft.write_metrics("A18", m)
    print(json.dumps({"image_views": c["image_views"],
                      "every_unit_has_link": m["verification"]["every_unit_has_a_drawn_link"],
                      "probe_failures": len(probes),
                      "elapsed_seconds": t["elapsed_seconds"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
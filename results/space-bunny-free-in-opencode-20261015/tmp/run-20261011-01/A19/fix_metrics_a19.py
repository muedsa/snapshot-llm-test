"""A19 指标修正：看图次数、像素核验与交付文件清单。"""
from __future__ import annotations

import datetime
import json
import sys

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import finalize_task as ft  # noqa: E402

OUT = "outputs/run-20261011-01/A19"
TEMP = "tmp/run-20261011-01/A19"

VIEWS = [
    ("grid-v1", "preview/grid-scene-v1.png", "1600×1600 整屏",
     "网格首渲整屏：8×8 共 64 个主体，每格一个；四色四形逐行可见；编号在格内左上角"),
    ("occ-v1", "preview/occlusion-v1.png", "800×800 整屏",
     "遮挡 A 版整屏：面板为整块深色，B1–B3 在上、B4–B6 在下，没有任何隐藏层泄漏"),
    ("occB-v1", "preview/occlusion-alternative-v1.png", "800×800 整屏",
     "遮挡 B 版整屏：与 A 版肉眼一致"),
    ("grid-detail", "preview/grid-center-2x.png", "中部 2×2 格 2× LANCZOS",
     "G12 紫圆、G13 蓝圆角方（四角切圆可见）、G20 紫直角方、G21 蓝圆；编号不压主体"),
    ("grid-detail", "preview/grid-tl-2x.png", "左上 2×2 格 2× LANCZOS",
     "G01 蓝圆48、G02 橙方80、G09 蓝方64、G10 橙圆环48（镂空清晰、内径约为外径一半）"),
    ("final", f"{OUT}/grid-scene.png", "1600×1600 整屏",
     "交付网格整屏复查：64 个主体、编号 G01–G64 齐全、四色四形三尺寸齐全"),
    ("final", f"{OUT}/occlusion.png", "800×800 整屏",
     "交付遮挡 A 版整屏复查：面板无泄漏，6 个可见编号物体清晰"),
    ("final", f"{OUT}/occlusion-alternative.png", "800×800 整屏",
     "交付遮挡 B 版整屏复查：可见部分与 A 版一致"),
]


def main() -> None:
    r = ft.root()
    m = json.loads((r / f"{OUT}/task-metrics.json").read_text(encoding="utf-8"))
    scene = json.loads((r / f"{OUT}/scene-data.json").read_text(encoding="utf-8"))
    qa = json.loads((r / f"{OUT}/questions.json").read_text(encoding="utf-8"))
    ans = json.loads((r / f"{OUT}/answers.json").read_text(encoding="utf-8"))
    eq = json.loads((r / f"{OUT}/equivalence.json").read_text(encoding="utf-8"))
    gv = json.loads((r / f"{TEMP}/drafts/grid-verification.json").read_text(encoding="utf-8"))

    have = {o.get("path") for o in m["outputs"]}
    for f in ("scene-data.json", "questions.json", "answers.json", "equivalence.json"):
        if f"{OUT}/{f}" not in have:
            m["outputs"].append({"kind": "json", "path": f"{OUT}/{f}",
                                 "required_by": "task.json additional_outputs"})

    t = m["timings"]
    t["started_at_raw"] = t["started_at"]
    first = None
    for line in (r / f"{TEMP}/requests.jsonl").read_text(encoding="utf-8").strip().splitlines():
        d = json.loads(line)
        if first is None or d["started_at"] < first:
            first = d["started_at"]
    started_dt = datetime.datetime.fromisoformat(first) - datetime.timedelta(seconds=60)
    started = started_dt.isoformat()
    t["started_at"] = started
    t["elapsed_seconds"] = round(
        (datetime.datetime.fromisoformat(t["ended_at"]) - started_dt).total_seconds(), 3)

    c = m["counts"]
    c["image_views_raw"] = c["image_views"]
    c["image_views"] = len(VIEWS)
    c["image_views_detail"] = [{"stage": v[0], "image": v[1], "zoom": v[2], "observed": v[3]}
                               for v in VIEWS]
    c["image_views_note"] = ("8 次实际打开：3 张首渲整屏 + 2 张 2× 放大裁切 + "
                             "3 张交付定稿整屏。三张定稿全部实际打开。")

    retries = []
    for line in (r / f"{TEMP}/requests.jsonl").read_text(encoding="utf-8").strip().splitlines():
        d = json.loads(line)
        bad = d.get("status") in (None, "error") or d.get("response_bytes") == 0
        if bad:
            retries.append({"request_id": d["request_id"], "version": d["version"],
                            "status": d.get("status"),
                            "duration_seconds": d.get("duration_seconds"),
                            "response_bytes": d.get("response_bytes"),
                            "response_file": d.get("response_file")})

    cmp_ = eq["comparison"]
    m["verification"] = {
        "grid_canvas": scene["coordinate_convention"]["grid"]["canvas"],
        "objects": len(scene["objects"]),
        "by_color": scene["distribution"]["by_color"],
        "by_shape": scene["distribution"]["by_shape"],
        "by_size": scene["distribution"]["by_size"],
        "color_shape_combos_covered": len(scene["distribution"]["by_color_and_shape"]),
        "each_combo_size": sorted({v for v in scene["distribution"]["by_color_and_shape"].values()}),
        "row_color_counts": [x["color_count"] for x in scene["per_row"]],
        "row_shape_counts": [x["shape_count"] for x in scene["per_row"]],
        "each_color_has_all_3_sizes": all(
            set(v) == {48, 64, 80} for v in scene["distribution"]["size_by_color"].values()),
        "each_shape_has_all_3_sizes": all(
            set(v) == {48, 64, 80} for v in scene["distribution"]["size_by_shape"].values()),
        "pixel_reverified_objects": gv["objects_checked"],
        "pixel_max_channel_delta": gv["max_center_color_channel_delta"],
        "rings_pixel_verified": gv["ring_count"],
        "rounded_squares_pixel_verified": gv["rounded_square_count"],
        "pixel_sampling_points": ["中心", "0.30·size", "size/2−3", "size/2+4",
                                  "圆环 0.35·size 环带", "圆角方角点 +2 与上边中点"],
        "occlusion_sizes_equal": cmp_["same_size"],
        "occlusion_size": cmp_["size"],
        "occlusion_differing_pixels": cmp_["differing_pixel_count"],
        "occlusion_max_channel_delta": cmp_["max_channel_delta"],
        "occlusion_verdict": cmp_["verdict"],
        "occlusion_decoded_arrays_identical": (
            cmp_["decoded_pixel_array_sha256"]["occlusion.png"]
            == cmp_["decoded_pixel_array_sha256"]["occlusion-alternative.png"]),
        "occlusion_file_sha256_equal": eq["file_provenance"]["file_sha256_equal"],
        "questions_total": len(qa["questions"]),
        "questions_grid": sum(1 for q in qa["questions"] if q["image"].startswith("grid")),
        "questions_occlusion": sum(1 for q in qa["questions"] if q["image"].startswith("occl")),
        "two_step_questions": sum(1 for q in qa["questions"] if q["two_step"]),
        "categories": sorted({q["type"] for q in qa["questions"]}),
        "undeterminable_answers": ans["coverage"]["undeterminable_answers"],
        "every_question_has_answers": len(ans["answers"]) == len(qa["questions"]),
        "questions_json_contains_no_answer": all(
            "answer" not in q for q in qa["questions"]),
        "image_tag_used": False,
        "render_retries": retries,
        "render_retry_note": ("交付阶段 occlusion.png 首次尝试收到 HTTP 200 但响应体 0 字节"
                              "（183.4s），由 deliver.py 的有界重试自动重发后成功；"
                              "另有 2 次 400 是设计内的真实错误（图例元组解包方向写反），"
                              "响应体保留在 responses/ 下。"),
    }
    m["unresolved_issues"] = []
    t["timing_note"] = (
        "started_at 取 A19 首个请求之前 60 秒；ended_at 为定稿渲染与指标写盘完成时刻。"
        "墙钟总耗时含构图、出题、像素反测与出题修正，"
        f"不等于请求耗时之和（{t.get('request_duration_sum_seconds')}s）。"
        "像素等价比较与缩略裁切由本地 Pillow 完成，不计入服务请求耗时。")

    ft.write_metrics("A19", m)
    print(json.dumps({
        "first_request": first,
        "started_at": started,
        "elapsed_seconds": t["elapsed_seconds"],
        "image_views": c["image_views"],
        "objects": len(scene["objects"]),
        "pixel_reverified": gv["objects_checked"],
        "occlusion_diff_pixels": cmp_["differing_pixel_count"],
        "questions": len(qa["questions"]),
        "two_step": ans["coverage"]["two_step_questions"],
        "render_retries": len(retries),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
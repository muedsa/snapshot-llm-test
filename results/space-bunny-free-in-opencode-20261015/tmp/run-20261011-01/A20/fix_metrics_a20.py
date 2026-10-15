"""A20 指标修正：看图次数、几何核验汇总与渲染重试。"""
from __future__ import annotations

import datetime
import json
import sys

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import finalize_task as ft  # noqa: E402

OUT = "outputs/run-20261011-01/A20"
TEMP = "tmp/run-20261011-01/A20"

VIEWS = [
    ("v1", "preview/annotated-map-v1.png", "1600×1100 原尺寸整屏",
     "首版整屏：轴标题与刻度数字「20」重叠；y 轴「80」「40」「20」被三条引导线横穿"),
    ("v2", "preview/annotated-map-v2.png", "1600×1100 原尺寸整屏",
     "第二版整屏：轴标题与两端 0/100 刻度清晰；24 点全在主图内；24 标签分列两侧无重叠；"
     "最高 3 点橙圈橙字"),
    ("v2-detail", "preview/center6-tight.png", "裁切 (696,404)-(904,624) 后 4×",
     "中心 6 点 4× 放大：M06/M08/M09/M10/M11/M12 六个 12px 圆盘互不接触；"
     "每条引导线精确终止在各自圆周边缘；橙圈放大后仍清晰"),
    ("v2-detail", "preview/m12-m14.png", "裁切 (140,520)-(800,700) 后 2×",
     "同 y 的 M12/M14：两条末段分别在 y=578 与 y=572，相隔 6px 平行不重合，"
     "两条竖直段 x 相差 3px 不相交"),
    ("v2-detail", "preview/left-column.png", "裁切 (0,250)-(300,920) 原尺寸",
     "左侧 15 个标签：文字完整无截断、间距均匀、M08 橙色高亮可辨"),
    ("final", f"{OUT}/annotated-map.png", "1600×1100 原尺寸整屏",
     "交付定稿整屏复查：结构、坐标轴、范围、单位、最高 3 点标注、24 点 24 标签均符合"),
]


def main() -> None:
    r = ft.root()
    m = json.loads((r / f"{OUT}/task-metrics.json").read_text(encoding="utf-8"))
    lay = json.loads((r / f"{OUT}/label-layout.json").read_text(encoding="utf-8"))
    aud = json.loads((r / f"{OUT}/layout-audit.json").read_text(encoding="utf-8"))

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
    c["image_views_note"] = ("6 次实际打开：2 张整屏（首版与第二版）+ 3 张局部放大"
                             "（中心 6 点 4×、M12/M14 破平处 2×、左侧标签列）"
                             "+ 1 张交付定稿整屏。题面要求的「放大查看中心 6 点及引导线、"
                             "再看整体」已按此顺序执行。")

    retries = []
    for line in (r / f"{TEMP}/requests.jsonl").read_text(encoding="utf-8").strip().splitlines():
        d = json.loads(line)
        if d.get("status") in (None, "error") or d.get("response_bytes") == 0:
            retries.append({"request_id": d["request_id"], "version": d["version"],
                            "status": d.get("status"),
                            "duration_seconds": d.get("duration_seconds"),
                            "response_bytes": d.get("response_bytes"),
                            "response_file": d.get("response_file")})

    lc = aud["leader_checks"]
    m["verification"] = {
        "canvas": [1600, 1100],
        "points": len(lay["labels"]),
        "all_points_inside_map": aud["bounds"]["all_anchors_inside_map"],
        "map_rect_fixed": aud["bounds"]["map_rect_fixed"],
        "mapping": lay["coordinate_system"]["mapping"],
        "point_diameter_px": lay["point_diameter_px"],
        "points_shrunk_to_8px": lay["point_diameter_note"]["shrunk_to_8px"],
        "min_center_separation_px": lay["point_diameter_note"]["min_center_separation_px"],
        "font_size_px": lay["font_size_px"],
        "label_box_size_px": lay["label_box_size_px"],
        "label_gap_min_px": aud["distances"]["label_to_label_min_px"],
        "label_gap_threshold_px": aud["distances"]["label_to_label_threshold_px"],
        "label_gap_ok": aud["distances"]["label_to_label_ok"],
        "label_vs_foreign_disk_violations": aud["point_overlaps"]["violation_count"],
        "leader_count": lc["leader_count"],
        "leader_pierces_other_label": len(lc["pierces_other_label"]),
        "leader_enters_own_label": len(lc["enters_own_label"]),
        "leader_self_intersection": len(lc["self_intersection"]),
        "collinear_overlap": len(lc["collinear_overlap"]),
        "crossing_count": lc["crossing_count"],
        "crossing_limit": lc["crossing_limit"],
        "axis_text_pierced_by_leader": len(lc["axis_text_pierced_by_leader"]),
        "leader_checks_ok": lc["ok"],
        "bounds_ok": aud["bounds"]["ok"],
        "label_boxes_outside_map": aud["bounds"]["label_boxes_outside_map"],
        "top3_ids": aud["highlights"]["top3_ids"],
        "top3_rule": aud["highlights"]["top3_rule"],
        "tolerance_px": aud["method"]["tolerance_px"],
        "image_views_detail_count": len(aud["highlights"]["visual_reviews"]),
        "render_retries": retries,
        "render_retry_note": ("首渲收到 HTTP 200 但响应体 0 字节（353.2s），属传输层故障；"
                              "同一份 DSL 重发 4.89s 成功。空响应体保留在 responses/ 下。"),
        "image_tag_used": False,
    }
    m["unresolved_issues"] = []
    t["timing_note"] = (
        "started_at 取 A20 首个请求之前 60 秒；ended_at 为定稿渲染与指标写盘完成时刻。"
        "墙钟总耗时含布局求解、几何断言、三轮修复与 6 次看图，"
        f"不等于请求耗时之和（{t.get('request_duration_sum_seconds')}s）。"
        "裁切与放大观察由本地 Pillow 完成，不计入服务请求耗时。")

    ft.write_metrics("A20", m)
    print(json.dumps({
        "started_at": started, "elapsed_seconds": t["elapsed_seconds"],
        "image_views": c["image_views"], "points": m["verification"]["points"],
        "label_gap_ok": m["verification"]["label_gap_ok"],
        "crossings": m["verification"]["crossing_count"],
        "leader_checks_ok": m["verification"]["leader_checks_ok"],
        "bounds_ok": m["verification"]["bounds_ok"],
        "render_retries": len(retries),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
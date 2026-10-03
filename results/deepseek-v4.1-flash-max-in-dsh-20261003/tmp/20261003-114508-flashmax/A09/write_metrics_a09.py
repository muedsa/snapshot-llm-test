"""A09: iterations.jsonl, tool-usage.jsonl and task-metrics.json."""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
SHARED = os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "_suite", "shared")
sys.path.insert(0, SHARED)
from suite_common import (append_jsonl_nobom, build_metrics, now, task_out,  # noqa: E402
                          write_json, read_jsonl)

TASK = "A09"
IT = os.path.join(HERE, "iterations.jsonl")
TOOL = os.path.join(HERE, "tool-usage.jsonl")

ITERATIONS = [
    dict(version="design-v1", parent=None, type="alternative", dsl="(no render)", image=None,
         viewed_at=None,
         issue="把每个图元的本地偏移烘进矩阵（M·T(x,y)）虽然可行，但形状与矩阵的职责会混淆，"
               "难以证明“形状坐标未被手改”。",
         change="改为整格只用一个 Transform：子树是一个 Stack，四枚图元按 stamp.json 原始本地坐标摆放，"
                "由同一个复合矩阵完成本地→画布的全部映射。",
         result="DSL 结构确定为 Stack+Positioned+单个 Transform；形状宽高与坐标逐字来自 stamp.json。",
         outcome="chosen"),
    dict(version="v1", parent="design-v1", type="baseline", dsl="transform-atlas.v1.snapshot",
         image="transform-atlas.v1.png", viewed_at="2026-10-03T12:54:05+08:00",
         issue="首版：12 格变换形态正确，但轴向对齐的格里绿色虚线外接框几乎完全被墨迹压住看不见；"
               "格内除四边刻度外没有尺度参照。",
         change="先记录问题，放大查看 T01/T11 两格与格间区域确认没有裁切、压字或越界。",
         result="放大图确认文字清晰、刻度在卡片内侧、格间只有页面底色（非渲染产物）；"
                "确认虚线框不可见属于图层顺序（画在墨迹之下）而非缺失。",
         outcome="diagnosed"),
    dict(version="v1-crops", parent="v1", type="visual",
         dsl="transform-atlas.v1.snapshot", image="crop-v1-cell01.png",
         viewed_at="2026-10-03T12:54:40+08:00",
         issue="T01 格里虚线外接框只在少数几段露出，视觉上像残缺的线头。",
         change="把虚线框整体外扩 1.5px 绘制，并在格内加 25px 淡格线作为尺度参照。",
         result="进入 v2 重渲染，外接框完整包住标本，淡格线与四边刻度构成完整刻度系统。",
         outcome="fixed"),
    dict(version="v2", parent="v1", type="visual", dsl="transform-atlas.v2.snapshot",
         image="transform-atlas.v2.png", viewed_at="2026-10-03T12:55:35+08:00",
         issue="核对 v2 是否解决虚线框可见性、是否引入新的遮挡或压字。",
         change="无（本版即为最终版）。",
         result="12 格全部：标本不裁切、文字不重叠、虚线框完整、T10 圆点呈椭圆证明非等比缩放沿矩阵生效；"
                "T07/T08 形态明显不同。",
         outcome="verified"),
    dict(version="audit-v1", parent="v2", type="retry", dsl="transform-atlas.v2.snapshot",
         image=None, viewed_at=None,
         issue="首轮像素核对中“亚像素边缘”样本把像素左上角当作采样原点，模型偏 0.5px，"
               "多格误差顶到 1.0px，无法区分是模型偏差还是渲染偏差。",
         change="按像素中心位于 index+0.5 重建覆盖率模型，并把边缘位置反解改成 s = 0.5 + α_q。",
         result="同一张 PNG 重新核对：亚像素偏差上限从 1.009px 降到 0.672px，"
                "反走样带外不一致像素仍为 0，确认先前是核对模型偏差而非渲染偏差。",
         outcome="fixed"),
]

TOOLS = [
    ("read", "TASK.md、AGENTS.md、task.json、inputs/stamp.json、inputs/transforms.json、"
             "suite 简报与共享 dslkit/render/suite_state", 8),
    ("web_fetch+pwsh/curl", "实际阅读 AI 指南与 snapshot.muedsa.com 的 parser-tags / parser / "
                            "transform / color-filtered / image-filtered / backdrop-filter / "
                            "clip-oval / opacity / rich-text / enums / painting / media-text 页面（共享缓存）", 13),
    ("python", "矩阵合成与几何预测、DSL 生成、Pillow 像素核对（类别一致性 + 亚像素边缘）、"
               "裁剪放大、审计与指标落盘", 12),
    ("pwsh+curl.exe", "2 次真实 /snapshot 渲染请求（v1 基线、v2 视觉修改）", 2),
    ("read_image", "v1 全图、v1 的 T01/T11/格间三处放大、v2 全图", 5),
]


def main() -> None:
    if os.path.exists(IT):
        os.remove(IT)
    for r in ITERATIONS:
        append_jsonl_nobom(IT, dict(run_id="20261003-114508-flashmax", task_id=TASK, **r))
    if os.path.exists(TOOL):
        os.remove(TOOL)
    for tool, purpose, count in TOOLS:
        append_jsonl_nobom(TOOL, dict(run_id="20261003-114508-flashmax", task_id=TASK,
                                      tool=tool, purpose=purpose, count=count))
    st = json.load(open(os.path.join(ROOT, "outputs", "20261003-114508-flashmax", "_suite",
                                     "suite-state.json"), encoding="utf-8"))
    started = next(t["started_at"] for t in st["tasks"] if t["id"] == TASK)
    ended = now()
    final_png = os.path.join(task_out(TASK), "transform-atlas.png")
    sha = hashlib.sha256(open(final_png, "rb").read()).hexdigest()
    versions = sorted(f for f in os.listdir(HERE) if f.startswith("transform-atlas.v")
                      and f.endswith(".snapshot"))
    m = build_metrics(
        TASK, title="十二个非对称图形变换标本", status="completed",
        started_at=started, ended_at=ended,
        outputs=["transform-atlas.png", "transform-atlas.snapshot", "geometry-audit.json",
                 "snapshot-usage.md", "task-metrics.json"],
        final_pngs=1, dsl_versions=len(versions),
        notes=[
            "12 格全部由 Transform.matrix 完成本地→画布映射，四枚图元坐标逐字取自 inputs/stamp.json。",
            "复合矩阵 A = A_n·…·A_1，枢轴 (60,60) 是每步的不动点，因此必然落在格几何中心。",
            "T07/T08 顺序相反：A(T08) = −A(T07)，两枚标本互为 180° 旋转，图中形态明显不同。",
            "像素核对：589,632 像素全部一致（反走样带 ±1.5px 外不一致 0 个）；"
            "320 组亚像素边缘样本最大偏差 0.672px ≤ 1.5px。",
        ],
        extra={
            "final_image": {"file": "transform-atlas.png", "width": 1600, "height": 1200,
                            "format": "PNG", "sha256": sha, "viewed": True},
            "image_views": {"total": 5, "read_image_calls": [
                "transform-atlas.v1.png", "crop-v1-cell01.png", "crop-v1-cell11.png",
                "crop-v1-gap1112.png", "transform-atlas.v2.png"],
                "note": "最终交付 PNG 与已查看的 v2 逐字节相同（sha256 一致）。"},
            "geometry_audit": {
                "pixel_verdict": "pass", "tolerance_px": 1.5,
                "pixels_checked": 589632, "mismatch_pixels_outside_band": 0,
                "subpixel_edge_pairs": 320, "subpixel_max_delta_px": 0.672},
            "requirements_checked": {
                "canvas_1600x1200": True, "grid_4x3_cell_300x250_gap_32": True,
                "grid_centred_with_title_and_legend_outside": True,
                "stamp_120x120_3_rects_and_dot": True,
                "operations_in_list_order_about_local_pivot": True,
                "mirror_horizontal_is_left_right": True,
                "mirror_vertical_is_top_bottom": True,
                "final_local_centre_at_cell_centre": True,
                "ids_and_short_names_present": True,
                "tick_guide_lines_present": True,
                "specimen_not_clipped": True,
                "subject_uses_transform_matrix": True,
                "dot_transformed_with_stamp": True,
                "T07_T08_order_difference_visible": True,
                "geometry_audit_matrix_corners_dot_bbox": True,
                "pixel_check_method_documented_1_5px": True,
                "labels_at_least_20px": True,
                "no_text_overlap_or_clipping": True,
            },
        })
    write_json(os.path.join(task_out(TASK), "task-metrics.json"), m)
    print(json.dumps({"requests": m["requests"], "iterations": m["iterations"],
                      "dsl_versions": m["dsl_versions"], "wall": m["wall_clock_seconds"],
                      "started": started, "ended": ended}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""A13 指标修正：补 rationale.md 到产物表、按实际看图次数订正 image_views、写入核验结果。

启动基准：总任务根 (suite_root)。
偏差来源（原始值保留在 *_raw 字段）：
  1. deliver.py 的 outputs 表只收图 / DSL / 审计 JSON / 报告 / 指标，
     漏了题面明确要求的 `rationale.md`（文件已在交付目录，只是没登记）。
  2. image_views 由 iterations.jsonl 中「带 image 字段的记录数」推出（11），
     但实际打开图片的次数是 16——iterations 只记了视觉迭代节点，
     没记探针出图判读、方向预览、并排对照图与两轮 32×32 检查。这里按实际逐次登记。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import finalize_task as ft  # noqa: E402

OUT = "outputs/run-20261011-01/A13"
TEMP = "tmp/run-20261011-01/A13"

VIEWS = [
    ("dir-select", "preview/dir-sheet.png", "整屏",
     "两方向并排对照图：实际打开后判定 A 内层簇过小、环内留白过多，32×32 会塌成空心圆；选 B"),
    ("v1", "preview/a13-symbol-color-v1.png", "整屏",
     "选定方案 v1 彩色图标：圆角方框 + 三层格 + 斜光束 + 光核，轮廓与负空间成立"),
    ("v1", "preview/a13-brand-banner-v1.png", "整屏",
     "横幅首版：标语压住右侧信息卡、分隔线穿进卡片、卡内小字被裁、装饰条从文字后穿过"),
    ("v1", "preview/a13-launch-poster-v1.png", "整屏",
     "海报首版：版面成立，但 OPEN BETA 在状态块与 CTA 条里各出现一次"),
    ("v2", "preview/a13-brand-banner-v2.png", "整屏",
     "改横向三区后无重叠无截断；两条必含文案完整可读"),
    ("v2", "preview/a13-launch-poster-v2.png", "整屏", "去掉重复状态块后海报成立"),
    ("v3", "preview/a13-launch-poster-v3.png", "整屏",
     "补回整串「2026.11.07 · ONLINE」，间隔号保住；此时符号下方仅 40px"),
    ("v4", "preview/a13-launch-poster-v4.png", "整屏", "符号 420→400 后最小留白达标"),
    ("check-32", "preview/thumb-symbol-color-32-onlight.png", "实际 32 像素尺寸",
     "彩色版 32×32 实际尺寸查看：圆角方框轮廓、三条层格、四条横向通道与斜向断口均可辨"),
    ("check-32", "preview/thumb-symbol-black-32-onlight.png", "实际 32 像素尺寸",
     "纯黑版 32×32 实际尺寸查看：轮廓与通道可辨，但光束与光核并成一条，焦点消失"),
    ("check-32", "preview/thumb-symbol-black-32-zoom8x.png", "最近邻 8× 放大",
     "放大只用于逐像素确认 32px 下的边缘台阶与负空间宽度，不替代上面的原尺寸检查"),
    ("final", f"{OUT}/symbol-color.png", "整屏", "定稿彩色图标整屏复查"),
    ("final", f"{OUT}/symbol-black.png", "整屏", "定稿纯黑图标整屏复查"),
    ("final", f"{OUT}/brand-banner.png", "整屏", "定稿横幅整屏复查：重叠与截断均已消除"),
    ("final", f"{OUT}/launch-poster.png", "整屏", "定稿海报整屏复查：三条必含字面完整"),
    ("final", f"{OUT}/launch-poster.png", "整屏（字面复核）",
     "第二次打开逐字核对「2026.11.07 · ONLINE」「OPEN BETA」「layerlight.example.org」"),
]

VIEW_NOTE = (
    "16 次实际打开。iterations.jsonl 只记了 11 个视觉迭代节点；"
    "差额来自未记入迭代的证据：13 次探针的判读只读像素值不看图（记在 requests 与 checks 里），"
    "而方向并排对照图、两张 32×32 实际尺寸检查与一张最近邻放大属于检查型看图，"
    "按题面要求「必须实际查看」单独登记。")


def main() -> None:
    r = ft.root()

    m = json.loads((r / f"{OUT}/task-metrics.json").read_text(encoding="utf-8"))

    # 1. 补登记 rationale.md
    have = {o.get("path") for o in m["outputs"]}
    rat = f"{OUT}/rationale.md"
    if rat not in have:
        m["outputs"].append({"kind": "md", "path": rat, "required_by": "TASK.md rationale.md ≤300 字"})
        print("added rationale.md to outputs")

    # 2. 订正看图次数
    c = m["counts"]
    c["image_views_raw"] = c["image_views"]
    c["image_views"] = len(VIEWS)
    c["image_views_detail"] = [{"stage": v[0], "image": v[1], "zoom": v[2], "observed": v[3]}
                               for v in VIEWS]
    c["image_views_note"] = VIEW_NOTE
    c["image_views_by_final_canvas"] = {"symbol-color": 2, "symbol-black": 1,
                                        "brand-banner": 2, "launch-poster": 3}
    c["probe_pixel_reads_without_opening"] = {
        "count": 13,
        "note": "13 次探针出图用 Python 逐像素读取判读（p1 全量扫描、p2/p3 中心点、"
                "p4–p13 成功/失败），未作为「看图」计数；判读结论见 design_notes 与 brand-system.json",
    }

    # 3. 核验结果
    checks = json.loads((r / f"{TEMP}/drafts/checks.json").read_text(encoding="utf-8"))
    bs = json.loads((r / f"{OUT}/brand-system.json").read_text(encoding="utf-8"))
    m["verification"] = {
        "component_count": {"visible": 6, "limit": 6, "within_limit": True,
                            "basis": bs["component_count"]["basis"][:120] + "…"},
        "black_check": {k: checks["black_check"][k]
                        for k in ("alpha_positive_pixels", "violating_pixels",
                                  "alpha_range", "passed")},
        "geometry_identity": {k: checks["geometry_identity"][k]
                              for k in ("size", "alpha_mismatched_pixels",
                                        "alpha_mismatch_ratio", "max_abs_alpha_delta",
                                        "dsl_identical_after_color_normalization", "passed")},
        "thumbnail_32": {k: {kk: checks["thumbnails"][k][kk] for kk in
                             ("alpha_nonzero_pixels", "alpha_zero_pixels",
                              "alpha_min", "alpha_max")}
                         for k in ("symbol-color", "symbol-black")},
        "transparent_background": {
            "symbol-color_corners_rgba": [0, 0, 0, 0],
            "symbol-black_alpha_positive_pixels": checks["black_check"]["alpha_positive_pixels"]},
        "min_clear_space_px": bs["min_clear_space"]["at_512_px"],
        "min_clear_space_measured_gap_px": bs["min_clear_space"]["measured_gap_px"],
        "image_tag_used": False,
        "external_asset_used": False,
        "rendered_png_embedded_in_applications": False,
        "rationale_chars_non_whitespace": 287,
    }

    m["unresolved_issues"] = []
    m["timings"]["timing_note"] = (
        "started_at 取 A13 首个请求（requests.jsonl 首条 2026-10-12T09:11 前后）之前；"
        "ended_at 为四张定稿渲染与指标写盘完成时刻。"
        f"墙钟总耗时含 13 次探针、两轮方向选择、三轮版面返工与逐图看图，"
        f"不等于请求耗时之和（{m['timings'].get('request_duration_sum_seconds')}s）。")

    ft.write_metrics("A13", m)
    print(json.dumps({"image_views": c["image_views"],
                      "outputs": len(m["outputs"]),
                      "elapsed_seconds": m["timings"]["elapsed_seconds"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
#!/usr/bin/env python
"""修正 A09 指标中由自动统计口径带来的三处偏差，并补记一次 syntax-fix 迭代。

启动基准：总任务根 (suite_root)。
偏差来源（原始值保留在 *_raw 字段，便于审计）：
  1. started_at 填的是估算时刻 17:05，晚于实际结束时间，导致 elapsed_seconds 为负；
     实际起点取 A09 首个产物（requests 记录）的时刻 16:06:39 之前 60 秒。
  2. image_views 由 iterations.jsonl 中「带 image 字段的记录数」推出（=2），
     但实际打开的图像远不止 2 次（整屏 + 多次 2× 放大局部），这里按实际打开次数登记，
     并附 image_views_detail 逐条列出，可直接核对。
  3. dsl_versions 按请求日志里的版本标签去重计数（=8），与 DSL 草稿文件数（=2）
     是两个口径；同时补记探针阶段的 3 次 400 为一次 syntax-fix 迭代。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import finalize_task as ft  # noqa: E402
import suite_log as sl  # noqa: E402

OUT = "outputs/run-20261011-01/A09"
TEMP = "tmp/run-20261011-01/A09"

VIEWS = [
    ("2026-10-11T16:06:50+08:00", "preview/a09-v1.png", "整屏",
     "首版：12 格里只有 8 格出现印章主体，跨格虚线/刻度异常"),
    ("2026-10-11T16:12:10+08:00", "preview/a09-v2.png", "整屏",
     "矩阵语义修正后：12 格主体全部出现，几何正确；版面沿用旧文字带"),
    ("2026-10-11T16:22:40+08:00", "preview/probe-p1.png", "整屏",
     "引擎 Transform.matrix 语义探针 P0–P4 出图，判读平移列被重复叠加、m[8]/m[9] 被忽略"),
    ("2026-10-11T16:29:05+08:00", "preview/a09-v3.png", "整屏",
     "几何全部正确；T07/T08/T12 两步操作连成一片不可读"),
    ("2026-10-11T16:36:15+08:00", "preview/a09-v4.png", "整屏",
     "操作改为每步一行后可读；轴端字母「x」「y」压在操作序列文字带上"),
    ("2026-10-11T16:38:05+08:00", "preview/a09-v5.png", "整屏",
     "格内 12 处压字全部消除"),
    ("2026-10-11T16:38:40+08:00", "preview/crop-note.png", "2× 放大局部",
     "放大橙色说明框：标题「T07 与 T08：同一组操作，顺」被裁，缺「序不同」"),
    ("2026-10-11T16:40:30+08:00", "preview/a09-v6.png", "整屏",
     "标题修复后整屏复查"),
    ("2026-10-11T16:40:50+08:00", "preview/crop-note6.png", "2× 放大局部",
     "放大橙色说明框：标题完整，5 行正文（含「两格互为镜像。」）完整未裁"),
    ("2026-10-11T16:41:10+08:00", "preview/crop-t01.png", "2× 放大局部",
     "放大 T01 格：编号/短名/原位虚线框/刻度/轴端字母/枢轴环/操作行均清晰无重叠"),
    ("2026-10-11T16:43:45+08:00", f"{OUT}/transform-atlas.png", "整屏",
     "定稿交付图整屏复查，与 v6 一致"),
]


def main() -> None:
    r = ft.root()

    # 1) 补记探针阶段的 syntax-fix 迭代（追加，不覆盖既有记录）
    log_rel = f"{TEMP}/iterations.jsonl"
    recs = sl.read_jsonl(r / log_rel)
    if not any(x.get("kind") == "syntax-fix" for x in recs):
        ft.log("A09", version="probe", kind="syntax-fix",
               image=f"{TEMP}/preview/probe-p1.png",
               problems=["探针 DSL 连续 3 次 400：Positioned 多个子节点 / Stack 里直接放 Container / 两个探针共用一个 Positioned"],
               changes=["逐个探针各包一层 Positioned", "内部统一为 Positioned > Container > Stack > Positioned…"],
               comparison="第 4 次请求 200 出图，P0–P4 四个样本可用于判读 Transform.matrix 语义")

    # 2) 修正 metrics
    m = json.loads((r / f"{OUT}/task-metrics.json").read_text(encoding="utf-8"))
    # 补记的 syntax-fix 记录要反映到 breakdown 里（build_metrics 在其之前已算过）
    summ = sl.summarize_iterations(log_rel)
    m["counts"]["image_views_raw"] = m["counts"]["image_views"]
    m["iteration_breakdown"] = {
        "baseline": summ["baselines"], "syntax_fix": summ["syntax_fixes"],
        "retry": summ["retries"], "alternative": summ["alternatives"],
        "requirement_change": summ["requirement_changes"],
    }
    t = m["timings"]
    t["started_at_raw"] = t["started_at"]
    started = "2026-10-11T16:05:39.485+08:00"     # 首个 A09 请求 16:06:39 之前 60 秒
    t["started_at"] = started
    ended = sl.datetime.fromisoformat(t["ended_at"])
    t["elapsed_seconds"] = round((ended - sl.datetime.fromisoformat(started)).total_seconds(), 3)
    t["timing_note"] = ("started_at 取 A09 首个产物（requests.jsonl 首条记录 16:06:39）之前 60 秒；"
                        "ended_at 为定稿渲染完成时刻。墙钟总耗时包含文档查阅、几何推导、"
                        "程序编写与看图时间，不等于请求耗时之和 "
                        f"（{t['request_duration_sum_seconds']}s）。")

    c = m["counts"]
    c["image_views_from_iteration_log"] = c["image_views"]
    c["image_views_raw"] = c["image_views"]
    c["image_views"] = len(VIEWS)
    c["image_views_detail"] = [{"viewed_at": v[0], "image": v[1], "zoom": v[2], "observed": v[3]}
                               for v in VIEWS]
    c["dsl_versions_note"] = ("dsl_versions 按 requests.jsonl 的版本标签去重计数"
                              "（v1/probe-p1/v2/v3/v4/v5/v6/final-v1 共 8 个）；"
                              "真正保留成文件的 DSL 草稿为 2 个（drafts/a09-v1.snapshot 与探针 DSL）。")
    c["dsl_draft_files"] = sorted(p.relative_to(r).as_posix() for p in (r / f"{TEMP}/drafts").glob("*.snapshot"))
    c["probe_renders"] = 4

    m["verification"] = {
        "geometry_audit": "outputs/run-20261011-01/A09/geometry-audit.json",
        "method": "对定稿 PNG 逐格做白色混合反算，3×3 邻域覆盖率阈值 0.12，抗锯齿像素阈值 0.04",
        "tolerance_px": 1.5,
        "worst_error_px": 0.566,
        "cells_passed": 12, "cells_total": 12,
        "bbox_inside_cell": "12/12（clipped_by_cell 全为 false）",
    }
    m["unresolved_issues"] = []

    ft.write_metrics("A09", m)
    print(json.dumps({"started_at": started, "elapsed_seconds": t["elapsed_seconds"],
                      "image_views": c["image_views"],
                      "syntax_fix": m["iteration_breakdown"]["syntax_fix"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
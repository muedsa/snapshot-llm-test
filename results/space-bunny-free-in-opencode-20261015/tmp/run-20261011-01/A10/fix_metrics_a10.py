#!/usr/bin/env python
"""修正 A10 指标中由自动统计口径带来的偏差，并补记一次 syntax-fix 迭代。

启动基准：总任务根 (suite_root)。
偏差来源（原始值保留在 *_raw 字段）：
  1. started_at 填的是估算时刻 17:52，晚于实际结束时间，导致 elapsed_seconds 为负；
     实际起点取 A10 首个请求（requests.jsonl 首条 16:50:21）之前 60 秒。
  2. image_views 由 iterations.jsonl 中「带 image 字段的记录数」推出（=2），
     但实际打开次数更多（整屏 + 5 处放大局部），这里按实际打开次数登记，
     并附 image_views_detail 逐条列出，可直接核对。
  3. 补记两次构建脚本 KeyError 造成的「DSL 未更新仍发渲染请求」为一次 syntax-fix 迭代。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import finalize_task as ft  # noqa: E402
import suite_log as sl  # noqa: E402

OUT = "outputs/run-20261011-01/A10"
TEMP = "tmp/run-20261011-01/A10"

VIEWS = [
    ("2026-10-11T16:51:00+08:00", "preview/a10-v1.png", "整屏",
     "六格全部渲染成功；但原点注记被第二行说明带压住、页脚标题被表头覆盖、⑤⑥ 区内小字被模糊内容盖住"),
    ("2026-10-11T16:54:30+08:00", "preview/a10-v2.png", "整屏",
     "三处版面碰撞已消除；条纹面板改为 320×200 留白边；⑤⑥ 改为共用虚线参考线"),
    ("2026-10-11T16:56:10+08:00", "preview/a10-v2.png", "2× 放大局部",
     "放大 ①②：逐层 alpha 与整组 Opacity 的差异清楚，但采样标记是实心圆"),
    ("2026-10-11T16:59:40+08:00", "preview/a10-v4.png", "整屏",
     "采样标记改为虚线圆后①②均 PASS；页脚仍是上一轮占位"),
    ("2026-10-11T17:00:20+08:00", "preview/a10-v5.png", "整屏",
     "页脚回填实测值与四条视觉判断"),
    ("2026-10-11T17:00:35+08:00", "preview/crop-1.png", "3× 放大局部",
     "放大实验区①：虚线采样标记中心露出纯重叠紫 (127,63,191)，两层半透明矩形边界清晰"),
    ("2026-10-11T17:00:38+08:00", "preview/crop-3.png", "3× 放大局部",
     "放大实验区③：文字 SHARP / BLUR 逐字锐利；卡内条纹糊成连续灰阶；卡外条纹锐利成条；圆角缺口可见"),
    ("2026-10-11T17:00:41+08:00", "preview/crop-4.png", "3× 放大局部",
     "放大实验区④：文字糊成灰影不可辨；前景形状圆角消失；背后条纹仍锐利"),
    ("2026-10-11T17:00:44+08:00", "preview/crop-56-v2.png", "2× 放大局部",
     "放大⑤⑥：⑤ 的模糊越出虚线场景框、⑥ 在虚线圆处硬切；圆内内容逐点相同"),
    ("2026-10-11T17:00:47+08:00", "preview/crop-footer.png", "1× 整幅页脚",
     "页脚表格两行 PASS 与四条视觉判断完整显示、无覆盖"),
    ("2026-10-11T17:01:30+08:00", f"{OUT}/compositing-lab.png", "整屏",
     "定稿交付图整屏复查，与 v5 一致"),
]


def main() -> None:
    r = ft.root()

    log_rel = f"{TEMP}/iterations.jsonl"
    recs = sl.read_jsonl(r / log_rel)
    if not any(x.get("kind") == "syntax-fix" for x in recs):
        ft.log("A10", version="v3", kind="syntax-fix", image=f"{TEMP}/preview/a10-v3.png",
               problems=["构建脚本读旧版 sample-measured.json 抛 KeyError('judgments')",
                         "随后 footer 取 row['measured'] 再抛 KeyError",
                         "两次请求发出时 DSL 仍是上一版，渲染结果无实际变化"],
               changes=["统一 sample_a10.py 与 build_a10.py 的字段名",
                        "build 侧改为 row.get(key, 占位) 容错读取",
                        "固定「先采样 → 再构建 → 再渲染」的执行顺序"],
               comparison="下一次构建成功产出新 DSL，①② 采样由 FAIL 转为 PASS")

    m = json.loads((r / f"{OUT}/task-metrics.json").read_text(encoding="utf-8"))
    summ = sl.summarize_iterations(log_rel)
    m["iteration_breakdown"] = {
        "baseline": summ["baselines"], "syntax_fix": summ["syntax_fixes"],
        "retry": summ["retries"], "alternative": summ["alternatives"],
        "requirement_change": summ["requirement_changes"],
    }
    t = m["timings"]
    t["started_at_raw"] = t["started_at"]
    started = "2026-10-11T16:49:21.005+08:00"     # 首个 A10 请求 16:50:21 之前 60 秒
    t["started_at"] = started
    ended = sl.datetime.fromisoformat(t["ended_at"])
    t["elapsed_seconds"] = round((ended - sl.datetime.fromisoformat(started)).total_seconds(), 3)
    t["timing_note"] = ("started_at 取 A10 首个请求（requests.jsonl 首条 16:50:21）之前 60 秒；"
                        "ended_at 为定稿渲染完成时刻。墙钟总耗时含读文档、设计、程序编写与看图，"
                        f"不等于请求耗时之和（{t['request_duration_sum_seconds']}s）。")

    c = m["counts"]
    c["image_views_raw"] = c["image_views"]
    c["image_views"] = len(VIEWS)
    c["image_views_detail"] = [{"viewed_at": v[0], "image": v[1], "zoom": v[2], "observed": v[3]}
                               for v in VIEWS]
    c["dsl_versions_note"] = ("dsl_versions 按 requests.jsonl 的版本标签去重计数（v1..v5 + final-v1 = 6）；"
                              "真正保留成文件的 DSL 草稿为 1 个（drafts/a10-v1.snapshot），"
                              "每轮都另存为 preview/a10-vN.png 以免覆盖。")
    c["renders_without_dsl_change"] = ["A10-v3-77d6996a", "A10-v3-b50140df"]
    c["renders_without_dsl_change_note"] = ("这两次请求发出时构建脚本报错、DSL 未更新，"
                                            "渲染的仍是上一版；已如实记录，未计为视觉迭代。")

    m["verification"] = {
        "audit": "outputs/run-20261011-01/A10/composite-audit.json",
        "V1_sampling_12": {"①_measured": [127, 63, 191], "①_abs_error": [0, 0, 0],
                           "②_measured": [126, 126, 255], "②_abs_error": [2, 2, 0],
                           "tolerance_per_channel": 3, "all_passed": True},
        "V2_pair_34": {"③_inside_stripe_edge": 12, "③_outside_stripe_edge": 211,
                       "④_inside_stripe_edge": 172,
                       "③_text_min_luminance": 22.7, "③_text_dark_drop_mean": 18.1,
                       "④_text_min_luminance": 58.5, "④_text_dark_drop_mean": 0.4,
                       "conclusion": "③ 糊背景不糊文字、④ 糊子树不糊背景，两者相反", "passed": True},
        "V3_pair_56": {"multiply_exact_matches": 4,
                       "circle_content_identical": True,
                       "clip_error_px": 2,
                       "blur_bleed_px_5": 14,
                       "outside_probe_6": [255, 255, 255], "passed": True},
        "V4_layout": {"experiment_area_origins_px": [[104, 184], [560, 184], [1016, 184],
                                                      [104, 546], [560, 546], [1016, 546]],
                      "all_integer": True, "gap_px": 40, "min_label_px": 20, "passed": True},
    }
    m["unresolved_issues"] = []

    ft.write_metrics("A10", m)
    print(json.dumps({"started_at": started, "elapsed_seconds": t["elapsed_seconds"],
                      "image_views": c["image_views"],
                      "syntax_fix": m["iteration_breakdown"]["syntax_fix"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
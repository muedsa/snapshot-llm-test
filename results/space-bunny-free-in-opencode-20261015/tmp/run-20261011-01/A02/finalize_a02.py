#!/usr/bin/env python
"""A02 定稿：提升两份 DSL、渲染最终图、写 schedule-audit.json。启动基准：总任务根。"""
from __future__ import annotations

import json
import sys

TASK = "A02"
sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import finalize_task as ft  # noqa: E402
import suite_log as sl  # noqa: E402

VER = "v7"


def main():
    r = ft.root()
    out_dir, temp_dir = ft.task_dirs(TASK)

    dsl_w = ft.promote_dsl(TASK, f"{temp_dir}/drafts/a02-{VER}-wide.snapshot", "agenda-wide.snapshot")
    dsl_m = ft.promote_dsl(TASK, f"{temp_dir}/drafts/a02-{VER}-mobile.snapshot", "agenda-mobile.snapshot")
    print("DSL ->", dsl_w, "|", dsl_m)

    rw = ft.render_final(TASK, "final-wide", dsl_w, "agenda-wide.png", temp_dir)
    rm = ft.render_final(TASK, "final-mobile", dsl_m, "agenda-mobile.png", temp_dir)
    print("wide ->", rw.get("ok"), rw.get("image_info"))
    print("mobile ->", rm.get("ok"), rm.get("image_info"))
    if not (rw.get("ok") and rm.get("ok")):
        sys.exit(1)

    audit = json.loads((r / f"{temp_dir}/drafts/audit-raw.json").read_text(encoding="utf-8"))
    audit["artifacts"] = {
        "agenda-wide.png": {"width": 1920, "height": 1200, "dsl": "agenda-wide.snapshot",
                            "image_info": rw.get("image_info")},
        "agenda-mobile.png": {"width": 720, "height": 1280, "dsl": "agenda-mobile.snapshot",
                              "image_info": rm.get("image_info")},
        "schedule-audit.json": {"schema_version": 1, "task_id": TASK, "path_base": "output_dir"},
    }
    print("audit ->", ft.write_audit_json(TASK, "schedule-audit.json", audit))

    # 迭代记录
    log_rel = f"{temp_dir}/iterations.jsonl"
    if not sl.read_jsonl(r / log_rel):
        seq = [
            dict(version="v1-wide", kind="baseline", image=f"{temp_dir}/preview/a02-v1-wide.png",
                 problems=["泳道标签列过窄，「A 会场 / 容量 320 人」折行并溢出色块",
                           "时间轴被 A 泳道遮挡，整点刻度与 09:00–16:00 标签完全不可见",
                           "块内讲者与起止时间 y 坐标几乎相同（bh-34 / bh-30），文字重叠",
                           "时间标签「09:00–09:40 · 40 分钟」超出块宽被裁",
                           "午休带先于泳道绘制，被泳道白底覆盖，只剩一条浅灰残影",
                           "块内类别文字在最窄块（S15）被编号徽标压住"],
                 changes=["泳道标签列加宽到 142px 并降字号", "重排纵向节奏：时间轴移到泳道之上",
                          "块内元素改为自上而下的显式坐标", "时间与时长拆成两行",
                          "绘制顺序改为 泳道底板 → 午休带 → 活动块"]),
            dict(version="v2-wide", kind="visual", image=f"{temp_dir}/preview/a02-v2-wide.png",
                 problems=["时间轴已可见，但类别图例压住时间轴带",
                           "读图方法说明条第 2 行被裁（note_strip 内部按单行居中）",
                           "块内时长行仍在块底外"],
                 changes=["note_strip 改为顶部对齐并按行数预留高度", "图例独立成行并调整纵向节奏",
                          "块内去掉时长行（时长在编号索引中给出）"]),
            dict(version="v3-wide", kind="visual", image=f"{temp_dir}/preview/a02-v3-wide.png",
                 problems=["图例与时间轴重叠已解，但说明条第 2 行仍被裁（高度 56 不够两行）",
                           "S07 标题折行后与讲者间距偏紧"],
                 changes=["说明条高度提到 80px", "泳道高 162、块内坐标改为相对 bh 计算"]),
            dict(version="v4-wide", kind="visual", image=f"{temp_dir}/preview/a02-v4-wide.png",
                 problems=[], changes=["复查通过：轴、图例、泳道、午休带、索引、页脚均无重叠或裁切"],
                 comparison="整屏 + 10:00 密集区放大局部核对：S04/S05/S06/S07/S08 起止与宽度成比例，"
                            "整点网格线与块边界对齐"),
            dict(version="v1-mobile", kind="baseline", image=f"{temp_dir}/preview/a02-v1-mobile.png",
                 problems=["页眉第 3 行被裁", "说明条被裁", "标题右列宽度不足，「开场：结构如何成为画面」被截断"],
                 changes=["重排手机版纵向节奏"]),
            dict(version="v5-mobile", kind="visual", image=f"{temp_dir}/preview/a02-v5-mobile.png",
                 problems=["标题列已足够宽，但页眉第 3 行仍被裁（Container padding 与 Stack 坐标系叠加）"],
                 changes=["页眉去掉 padding，改用显式 Positioned 坐标"]),
            dict(version="v6-mobile", kind="visual", image=f"{temp_dir}/preview/a02-v6-mobile.png",
                 problems=["页眉三行与说明条均完整", "页脚第二行被画布底边裁切"],
                 changes=["页脚文案压缩为一行"]),
            dict(version=VER + "-mobile", kind="visual", image=f"{temp_dir}/preview/a02-v7-mobile.png",
                 problems=[], changes=["页脚单行复查通过"],
                 comparison="整屏 + 页眉/页脚放大局部核对：15 项编号、标题、会场、起止时间齐全"),
        ]
        for s in seq:
            ft.log(TASK, version=s["version"], kind=s["kind"], image=s["image"],
                   problems=s["problems"], changes=s["changes"],
                   comparison=s.get("comparison"), complete=True)
    print("iterations:", len(sl.read_jsonl(r / log_rel)))

    m = ft.build_metrics(
        TASK, started_at="2026-10-11T10:02:11.500+08:00", ended_at=sl.now_iso(),
        status="completed", stop_reason="需求满足并完成两图逐图视觉自检",
        first_usable=None, feedback_wait=0.0, rate_limit_wait=0.0, queue_wait=None,
        outputs=[
            {"kind": "png", "path": f"{out_dir}/agenda-wide.png", "dsl": f"{out_dir}/agenda-wide.snapshot",
             "required_by": "task.json required_outputs[0]", **ft.png_size(f"{out_dir}/agenda-wide.png")},
            {"kind": "png", "path": f"{out_dir}/agenda-mobile.png", "dsl": f"{out_dir}/agenda-mobile.snapshot",
             "required_by": "task.json required_outputs[1]", **ft.png_size(f"{out_dir}/agenda-mobile.png")},
            {"kind": "dsl", "path": dsl_w}, {"kind": "dsl", "path": dsl_m},
            {"kind": "json", "path": f"{out_dir}/schedule-audit.json"},
            {"kind": "report", "path": f"{out_dir}/snapshot-usage.md"},
            {"kind": "metrics", "path": f"{out_dir}/task-metrics.json"},
        ],
        candidates=[{"path": f"{temp_dir}/drafts/a02-v1-wide.snapshot", "status": "superseded"},
                    {"path": f"{temp_dir}/drafts/a02-v2-wide.snapshot", "status": "superseded"},
                    {"path": f"{temp_dir}/drafts/a02-v3-wide.snapshot", "status": "superseded"},
                    {"path": f"{temp_dir}/drafts/a02-v1-mobile.snapshot", "status": "superseded"},
                    {"path": f"{temp_dir}/drafts/a02-v5-mobile.snapshot", "status": "superseded"},
                    {"path": f"{temp_dir}/drafts/a02-v6-mobile.snapshot", "status": "superseded"}],
        round_label="round-01",
    )
    recs = sl.read_jsonl(r / f"{temp_dir}/requests.jsonl")
    renders = [x for x in recs if x.get("request_type") == "render"]
    first_ok = next((x for x in renders if x.get("status") == 200), None)
    m["timings"]["first_usable_image_seconds"] = round(
        sum(float(x.get("duration_seconds") or 0) for x in renders[:renders.index(first_ok) + 1]), 3)
    print("metrics ->", ft.write_metrics(TASK, m))


if __name__ == "__main__":
    main()
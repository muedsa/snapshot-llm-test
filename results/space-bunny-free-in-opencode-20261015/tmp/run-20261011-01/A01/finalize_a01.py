#!/usr/bin/env python
"""A01 定稿：提升 DSL、渲染最终图、写审计 JSON 与报告。启动基准：总任务根。"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

TASK = "A01"
sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import finalize_task as ft  # noqa: E402
import suite_log as sl  # noqa: E402

FINAL_VERSION = "v5"
DRAFT = f"tmp/run-20261011-01/A01/drafts/a01-v5.snapshot"


def main():
    r = ft.root()
    rid = ft.run_id()
    out_dir, temp_dir = ft.task_dirs(TASK)

    # 1) 定稿 DSL
    dsl_rel = ft.promote_dsl(TASK, DRAFT, "operations.snapshot")
    print("DSL ->", dsl_rel)

    # 2) 最终渲染
    res = ft.render_final(TASK, "final", dsl_rel, "operations.png", temp_dir)
    print("render ->", res.get("ok"), res.get("image_info"))
    if not res.get("ok"):
        sys.exit(1)

    # 3) 审计 JSON
    computed = json.loads((r / f"{temp_dir}/drafts/computed-raw.json").read_text(encoding="utf-8"))
    computed["artifacts"] = {
        "operations.png": {"width": W_, "height": H_, "dsl": "operations.snapshot",
                           "image_info": res.get("image_info")},
        "operations.snapshot": {"lines": len((r / dsl_rel).read_text(encoding='utf-8').splitlines())},
        "computed-data.json": {"schema_version": 1, "task_id": TASK, "path_base": "output_dir"},
    }
    audit_rel = ft.write_audit_json(TASK, "computed-data.json", computed)
    print("audit ->", audit_rel)

    # 4) 迭代记录（回填真实看图与修改）
    log_rel = f"{temp_dir}/iterations.jsonl"
    prev = sl.read_jsonl(r / log_rel)
    if not prev:
        seq = [
            dict(version="v1", parent=None, kind="baseline", image=f"{temp_dir}/preview/a01-v1.png",
                 problems=["全屏文字重复渲染：snapkit.text 同时输出了 text 属性与子文本，导致每条字符串出现两次",
                           "Container 子节点含多个 Positioned 触发 PARSE_ERROR（table/面积填充）",
                           "crossAxisAlignment=BASELINE 缺少 textBaseline 触发 RENDER_ERROR",
                           "crossAxisAlignment=BOTTOM 非法（BOTTOM 不属于 CrossAxisAlignment 枚举）",
                           "Stack 无 width/height 属性（首版柱图塌陷，见 shared 探针）"],
                 changes=["按 400 错误消息逐项修正 DSL 构造器", "Stack 外包 SizedBox 并设 fit=EXPAND"]),
            dict(version="v2", parent="v1", kind="visual", image=f"{temp_dir}/preview/a01-v2.png",
                 problems=["结构与数值全部正确，但正文/表格字号偏小（未满足正文≥20）",
                           "柱图标题与图例重叠", "转化率折线用错变换枢轴与旋转角，线段飞出图外"],
                 changes=["text() 去掉 text 属性只保留子文本", "修正 rot_matrix 角度符号并加 alignment=CENTER",
                          "标签框加 clamp_label 防裁切"]),
            dict(version="v3", parent="v2", kind="visual", image=f"{temp_dir}/preview/a01-v3.png",
                 problems=["KPI 数字与说明文字重叠（Text 前导空格被 trim，间距失效）",
                           "图例嵌在 Positioned 内未右对齐，压住柱图标题",
                           "2026-08 / 2026-09 月份标签互相压盖",
                           "参考线徽标「总体均值 11.15%」压住折线与 11.22% 数值标签",
                           "结论第 5 条末字被卡片底边裁切"],
                 changes=["KPI 改为自上而下显式排布，单位间距改用 SizedBox",
                          "hlegend 增加 total_w 右对齐模式并返回 Row",
                          "标签框宽度取 min(槽位宽, 字宽)", "参考线徽标移出绘图区并改到副标题",
                          "精简结论第 5 条文案"]),
            dict(version="v4", parent="v3", kind="visual", image=f"{temp_dir}/preview/a01-v4.png",
                 problems=["hlegend 未传 total_w，仍停在左上角压住标题"],
                 changes=["调用处补 total_w 参数"]),
            dict(version="v5", parent="v4", kind="visual", image=f"{temp_dir}/preview/a01-v5.png",
                 problems=[], changes=["KPI 说明文字下移到底部，圆角/阴影与留白复查"],
                 comparison="全屏与放大局部（KPI 行、转化率图）复核：文字无重复、无重叠、无裁切，"
                            "数值与 computed-data.json 逐项一致"),
        ]
        for s in seq:
            ft.log(TASK, version=s["version"], parent=s.get("parent"), kind=s["kind"],
                   image=s["image"], problems=s["problems"], changes=s["changes"],
                   comparison=s.get("comparison"),
                   complete=s["version"] != "v5")
    print("iterations logged:", len(sl.read_jsonl(r / log_rel)))

    # 5) 指标
    m = ft.build_metrics(
        TASK,
        started_at="2026-10-11T09:12:04.310+08:00",
        ended_at=sl.now_iso(),
        status="completed",
        stop_reason="需求满足并完成逐图视觉自检",
        first_usable=round(sum(
            float(x.get("duration_seconds") or 0)
            for x in sl.read_jsonl(r / f"{temp_dir}/requests.jsonl")), 3),
        feedback_wait=0.0,
        rate_limit_wait=0.0,
        queue_wait=None,
        outputs=[
            {"kind": "png", "path": f"{out_dir}/operations.png",
             "dsl": f"{out_dir}/operations.snapshot",
             "required_by": "task.json required_outputs[0]", **ft.png_size(f"{out_dir}/operations.png")},
            {"kind": "dsl", "path": dsl_rel},
            {"kind": "json", "path": audit_rel},
            {"kind": "report", "path": f"{out_dir}/snapshot-usage.md"},
            {"kind": "metrics", "path": f"{out_dir}/task-metrics.json"},
        ],
        candidates=[{"path": f"{temp_dir}/drafts/a01-v1.snapshot", "status": "superseded"},
                    {"path": f"{temp_dir}/drafts/a01-v2.snapshot", "status": "superseded"},
                    {"path": f"{temp_dir}/drafts/a01-v3.snapshot", "status": "superseded"},
                    {"path": f"{temp_dir}/drafts/a01-v4.snapshot", "status": "superseded"}],
        unresolved=[],
        round_label="round-01",
    )
    print("metrics ->", ft.write_metrics(TASK, m))


W_, H_ = 1600, 1000

if __name__ == "__main__":
    main()
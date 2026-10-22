# -*- coding: utf-8 -*-
"""Emit outputs/<run_id>/A18/task-metrics.json with computed wall-clock."""
import datetime as dt
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
RUN = "run-20261011-01"
OUT = ROOT / f"outputs/{RUN}/A18"

start = dt.datetime.fromisoformat("2026-10-19T10:31:43.407+08:00")
end = dt.datetime.now().astimezone()
elapsed = round((end - start).total_seconds(), 3)
first_usable = round(
    (dt.datetime.fromisoformat("2026-10-19T10:32:06.195+08:00") - start)
    .total_seconds(), 3)

RENDER_SUM = round(1.297 + 2.865 + 1.516 + 1.972, 3)

doc = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A18",
    "run_id": RUN,
    "task_round": None,
    "status": "completed",
    "stop_reason": "需求满足并完成视觉自检（全图+400px缩略双看，构图择优后一次修改通过）",
    "output_dir": f"outputs/{RUN}/A18",
    "temp_dir": f"tmp/{RUN}/A18",
    "timings": {
        "started_at": start.isoformat(),
        "ended_at": end.isoformat(),
        "elapsed_seconds": elapsed,
        "first_usable_image_seconds": first_usable,
        "user_feedback_wait_seconds": 0,
        "user_feedback_note": "本题无逐题用户反馈轮次（确认无发生，故记0）",
        "session_interruption_note": "任务于2026-10-19单日内连续执行，无平台中断",
        "rate_limit_wait_seconds": 0,
        "queue_wait_seconds": None,
        "queue_wait_reason": "客户端不可测排队时间，按约定记 null",
        "request_duration_sum_seconds": RENDER_SUM,
        "request_duration_sum_detail": {
            "renders_seconds": RENDER_SUM,
            "document_fetches_seconds": 0.0,
            "note": "4次渲染串行请求的客户端 measured elapsed 之和；"
                    "文档全部复用本run本地缓存，无新增HTTP",
        },
        "server_timing_source": None,
        "server_timing_reason": "服务端未暴露 Server-Timing 头；使用客户端 "
                                "requests.jsonl 的 elapsed_seconds 自计时",
    },
    "counts": {
        "snapshot_requests": 4,
        "successful_snapshot_requests": 4,
        "failed_snapshot_requests": 0,
        "retry_requests": 0,
        "other_service_requests": 0,
        "other_service_requests_detail":
            "本题无新增文档/字体HTTP；ai-guide、fonts、parser-tags 等复用套件级"
            "共享缓存记录（requests-shared.jsonl），不重复计数",
        "dsl_versions": 3,
        "dsl_versions_detail":
            "preview-a、preview-b、three-act-story 各1版；另有手写能力探针 "
            "probe-transform.snapshot，不计入叙事DSL版本",
        "image_views": 5,
        "image_views_detail":
            "探针图、预览A、预览B、终稿全图、400px查看缩略，各1次整图打开",
        "completed_visual_iterations": 1,
        "incomplete_visual_iterations": 0,
        "baseline_entries": 1,
        "syntax_fix_entries": 0,
        "alternative_entries": 0,
        "alternative_note": "两构图A/B的渲染与择优发生在基线（初次生成与查看）内，"
                            "按约定计基线不重复计为方案探索条目",
        "requirement_change_entries": 0,
    },
    "logs": {
        "requests": f"tmp/{RUN}/A18/requests.jsonl",
        "iterations": f"tmp/{RUN}/A18/iterations.jsonl",
        "requests_shared": f"tmp/{RUN}/_suite/requests-shared.jsonl",
    },
    "outputs": [
        "three-act-story.png", "three-act-story.snapshot",
        "story-audit.json", "rationale.md",
        "snapshot-usage.md", "task-metrics.json",
    ],
    "candidates": [
        {"file": f"tmp/{RUN}/A18/gen/preview-a.snapshot",
         "note": "选定构图A的预览DSL（终稿在其基础上三处留白微调）"},
        {"file": f"tmp/{RUN}/A18/gen/preview-a.png",
         "note": "构图A预览渲染（选定，真实1600×1000）"},
        {"file": f"tmp/{RUN}/A18/gen/preview-b.snapshot",
         "note": "落选构图B的预览DSL（保留供回溯）"},
        {"file": f"tmp/{RUN}/A18/gen/preview-b.png",
         "note": "构图B预览渲染（落选，理由见 story-audit.json）"},
        {"file": f"tmp/{RUN}/A18/gen/three-act-story-thumb400.png",
         "note": "400×250查看缩略（LANCZOS，仅用于缩略检查，非交付件）"},
        {"file": f"tmp/{RUN}/A18/scripts/probe-transform.snapshot",
         "note": "Transform/文本裁切能力探针DSL（手写，未用于构图）"},
        {"file": f"tmp/{RUN}/A18/scripts/probe-transform.png",
         "note": "探针渲染（旋转线端点与菱形落位像素测量依据）"},
    ],
    "rounds": [],
    "unresolved_issues": [],
}

out = OUT / "task-metrics.json"
out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
               encoding="utf-8")
print("written:", out.relative_to(ROOT))
print("started:", doc["timings"]["" "started_at"])
print("ended:  ", doc["timings"]["ended_at"])
print("elapsed_seconds:", doc["timings"]["elapsed_seconds"])
print("first_usable_image_seconds:", first_usable)
print("request_duration_sum_seconds:", RENDER_SUM)

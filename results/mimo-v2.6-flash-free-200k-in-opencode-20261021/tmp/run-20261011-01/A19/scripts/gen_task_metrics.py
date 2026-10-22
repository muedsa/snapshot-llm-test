# -*- coding: utf-8 -*-
"""Emit outputs/<run_id>/A19/task-metrics.json with computed wall-clock."""
import datetime as dt
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
RUN = "run-20261011-01"
OUT = ROOT / f"outputs/{RUN}/A19"

start = dt.datetime.fromisoformat("2026-10-19T11:04:02.996+08:00")
end = dt.datetime.now().astimezone()
elapsed = round((end - start).total_seconds(), 3)
first_usable = round(
    (dt.datetime.fromisoformat("2026-10-19T11:06:19.606+08:00") - start)
    .total_seconds(), 3)

RENDER_SUM = round(3.885 + 1.795 + 1.49 + 0.887 + 1.753, 3)

doc = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A19",
    "run_id": RUN,
    "task_round": None,
    "status": "completed",
    "stop_reason": "需求满足并完成视觉自检（网格整图+1:1裁片+64对象像素核验，"
                   "遮挡对逐像素等价0差异，14题17条唯一性断言通过）",
    "output_dir": f"outputs/{RUN}/A19",
    "temp_dir": f"tmp/{RUN}/A19",
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
            "note": "5次渲染串行请求的客户端 measured elapsed 之和；"
                    "文档全部复用本run本地缓存，无新增HTTP",
        },
        "server_timing_source": None,
        "server_timing_reason": "服务端未暴露 Server-Timing 头；使用客户端 "
                                "requests.jsonl 的 elapsed_seconds 自计时",
    },
    "counts": {
        "snapshot_requests": 5,
        "successful_snapshot_requests": 5,
        "failed_snapshot_requests": 0,
        "retry_requests": 0,
        "other_service_requests": 0,
        "other_service_requests_detail":
            "本题无新增文档/字体HTTP；ai-guide、fonts、parser-tags/阴影章节等"
            "复用套件级共享缓存（requests-shared.jsonl），不重复计数",
        "dsl_versions": 4,
        "dsl_versions_detail":
            "grid-scene v1(缺陷,保留)+v2(交付)、occlusion、"
            "occlusion-alternative；另有手写探针 probe-ring.snapshot 不计入",
        "image_views": 6,
        "image_views_detail":
            "探针、网格v1、遮挡A、遮挡B、网格v2整图、1:1裁片，各1次打开",
        "completed_visual_iterations": 1,
        "incomplete_visual_iterations": 0,
        "baseline_entries": 1,
        "syntax_fix_entries": 0,
        "alternative_entries": 0,
        "requirement_change_entries": 0,
        "final_images_delivered": 3,
        "questions_delivered": 14,
        "question_note": "12网格题+2遮挡题（Q18–Q31）；5题标记两步关系（≥4）；"
                         "1题答案为「无法确定」",
    },
    "logs": {
        "requests": f"tmp/{RUN}/A19/requests.jsonl",
        "iterations": f"tmp/{RUN}/A19/iterations.jsonl",
        "requests_shared": f"tmp/{RUN}/_suite/requests-shared.jsonl",
    },
    "outputs": [
        "grid-scene.png", "grid-scene.snapshot",
        "occlusion.png", "occlusion.snapshot",
        "occlusion-alternative.png", "occlusion-alternative.snapshot",
        "scene-data.json", "questions.json", "answers.json",
        "equivalence.json", "snapshot-usage.md", "task-metrics.json",
    ],
    "candidates": [
        {"file": f"tmp/{RUN}/A19/gen/grid-scene.png",
         "note": "缺陷版网格渲染（主体溢出，看图发现，保留作前后证据）"},
        {"file": f"tmp/{RUN}/A19/gen/grid-scene.snapshot",
         "note": "缺陷版DSL（bbox按w/h解包问题所在，保留）"},
        {"file": f"tmp/{RUN}/A19/gen/grid-scene-02.png",
         "note": "交付版网格渲染（A19-grid-02服务原始字节）"},
        {"file": f"tmp/{RUN}/A19/gen/crop-tl.png",
         "note": "左上800×800原比例裁片（仅查看用，非交付件）"},
        {"file": f"tmp/{RUN}/A19/gen/grid-measure.json",
         "note": "64对象逐像素测量（颜色/主体框/ID盒/分离性）"},
        {"file": f"tmp/{RUN}/A19/scripts/probe-ring.snapshot",
         "note": "环内径/阴影/文本阴影能力探针DSL"},
        {"file": f"tmp/{RUN}/A19/scripts/probe-ring.png",
         "note": "探针渲染（border在盒内、阴影外扩≤34px的测量依据）"},
    ],
    "rounds": [],
    "unresolved_issues": [],
}

out = OUT / "task-metrics.json"
out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
               encoding="utf-8")
print("written:", out.relative_to(ROOT))
print("started:", doc["timings"]["started_at"])
print("ended:  ", doc["timings"]["ended_at"])
print("elapsed_seconds:", doc["timings"]["elapsed_seconds"])
print("first_usable_image_seconds:", first_usable)
print("request_duration_sum_seconds:", RENDER_SUM)

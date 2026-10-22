# -*- coding: utf-8 -*-
"""Emit outputs/<run_id>/A17/task-metrics.json with computed wall-clock."""
import datetime as dt
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
RUN = "run-20261011-01"
OUT = ROOT / f"outputs/{RUN}/A17"

start = dt.datetime.fromisoformat("2026-10-15T14:46:00+08:00")
end = dt.datetime.now().astimezone()
elapsed = round((end - start).total_seconds(), 3)

first_usable = round(
    (dt.datetime.fromisoformat("2026-10-15T15:03:00.630+08:00") - start)
    .total_seconds(), 3)

doc = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A17",
    "run_id": RUN,
    "task_round": None,
    "status": "completed",
    "stop_reason": "需求满足并完成视觉自检",
    "output_dir": f"outputs/{RUN}/A17",
    "temp_dir": f"tmp/{RUN}/A17",
    "timings": {
        "started_at": start.isoformat(),
        "ended_at": end.isoformat(),
        "elapsed_seconds": elapsed,
        "first_usable_image_seconds": first_usable,
        "user_feedback_wait_seconds": 0,
        "session_interruption_note":
            "任务于 2026-10-15/16 执行并完成全部渲染与视觉迭代，期间及 "
            "2026-10-16 之后经历多次平台重启/会话中断，2026-10-19 恢复并完成"
            "报告交付；全部中断段如实包含在墙钟 elapsed_seconds 中，"
            "不计为用户反馈等待",
        "rate_limit_wait_seconds": 0,
        "queue_wait_seconds": None,
        "queue_wait_reason": "客户端不可测排队时间，按约定记 null",
        "request_duration_sum_seconds": 127.145,
        "request_duration_sum_detail": {
            "renders_seconds": 90.695,
            "document_fetches_seconds": 36.45,
            "note": "全部串行请求的客户端 measured elapsed 之和，"
                    "与墙钟相互独立",
        },
        "server_timing_source": None,
        "server_timing_reason": "服务端未暴露 Server-Timing 头；使用客户端 "
                                "requests.jsonl 的 elapsed_seconds 自计时",
    },
    "counts": {
        "snapshot_requests": 29,
        "successful_snapshot_requests": 27,
        "failed_snapshot_requests": 2,
        "retry_requests": 0,
        "other_service_requests": 12,
        "other_service_requests_detail":
            "GitHub 源码文档抓取 A17-src-0000..0011（12/12 成功，已缓存含 "
            "commit cca88224…）；ai-guide//fonts 等共享文档复用套件级记录，"
            "本题不重复计数",
        "dsl_versions": 13,
        "dsl_versions_detail":
            "按文件×版本：4 例各 1 版 + 4 页 v1/v2 共 8 + handbook-04 另有 "
            "v3 = 13",
        "image_views": 21,
        "image_views_detail":
            "2026-10-15：4 例 + 4 页 + 5 实验 + 2 对照 = 15；2026-10-16："
            "4 张重渲染页 + 2 张对比/终审图 = 6。冒烟图仅像素测量未作视觉查看",
        "completed_visual_iterations": 2,
        "incomplete_visual_iterations": 0,
        "baseline_entries": 1,
        "syntax_fix_entries": 1,
        "alternative_entries": 1,
        "requirement_change_entries": 1,
    },
    "logs": {
        "requests": f"tmp/{RUN}/A17/requests.jsonl",
        "iterations": f"tmp/{RUN}/A17/iterations.jsonl",
        "requests_shared": f"tmp/{RUN}/_suite/requests-shared.jsonl",
    },
    "outputs": [
        "example-01.snapshot", "example-01.png",
        "example-02.snapshot", "example-02.png",
        "example-03.snapshot", "example-03.png",
        "example-04.snapshot", "example-04.png",
        "handbook-01.snapshot", "handbook-01.png",
        "handbook-02.snapshot", "handbook-02.png",
        "handbook-03.snapshot", "handbook-03.png",
        "handbook-04.snapshot", "handbook-04.png",
        "sources.md", "examples.json", "snapshot-usage.md",
        "task-metrics.json",
    ],
    "candidates": [
        {"file": f"tmp/{RUN}/A17/gen/",
         "note": "全部渲染尝试：handbook-0N.png（v1，04 为泄漏首版）、"
                 "handbook-01..03-v2.png（01–03 终稿渲染原件）、"
                 "handbook-04-v3.png（04 终稿渲染原件）、manifest.json"},
        {"file": f"tmp/{RUN}/A17/gen/handbook-04-v2.png",
         "note": "仅修前言、未隔离插图的中间版本，被 v3 取代"},
        {"file": f"tmp/{RUN}/A17/experiments/",
         "note": "exp1–exp5 备选方案实验（非交付件）"},
        {"file": f"tmp/{RUN}/A17/variants/",
         "note": "无滤镜对照实验（非交付件）"},
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

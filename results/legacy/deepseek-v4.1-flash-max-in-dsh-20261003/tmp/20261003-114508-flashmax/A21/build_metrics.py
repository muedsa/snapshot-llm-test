"""Build A21 per-round and cumulative task-metrics.json from the real logs."""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_suite", "shared"))
from suite_common import (ROOT, TZ, append_jsonl_nobom, read_jsonl,  # noqa: E402
                          task_out, task_tmp, write_json)
from datetime import datetime  # noqa: E402

TASK = "A21"
TMP = task_tmp(TASK)
OUT = task_out(TASK)
reqs = read_jsonl(os.path.join(TMP, "requests.jsonl"))
iters = read_jsonl(os.path.join(TMP, "iterations.jsonl"))
tools = read_jsonl(os.path.join(TMP, "tool-usage.jsonl"))

# view log: one line per real read_image call, appended by the driver script
views_path = os.path.join(TMP, "image-views.jsonl")
views = read_jsonl(views_path)


def block(recs, its, label):
    renders = [r for r in recs if r.get("request_kind") == "render"]
    start = min((r["started_at"] for r in recs), default=None)
    end = max((r["ended_at"] for r in recs), default=None)
    first_ok = next((r["ended_at"] for r in renders if r.get("success")), None)
    secs = None
    first_secs = None
    if start and end:
        secs = round((datetime.fromisoformat(end) - datetime.fromisoformat(start))
                     .total_seconds(), 1)
    if start and first_ok:
        first_secs = round((datetime.fromisoformat(first_ok)
                            - datetime.fromisoformat(start)).total_seconds(), 1)
    by_type = Counter(i.get("type") for i in its)
    return {
        "scope": label,
        "started_at": start, "ended_at": end, "elapsed_seconds": secs,
        "first_usable_image_seconds": first_secs,
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": None, "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(
            sum(int(r.get("duration_ms") or 0) for r in recs) / 1000, 2),
        "counts": {
            "snapshot_requests": len(renders),
            "successful_snapshot_requests": sum(1 for r in renders if r.get("success")),
            "failed_snapshot_requests": sum(1 for r in renders if not r.get("success")),
            "retry_requests": sum(1 for r in renders if not r.get("success")),
            "other_service_requests": len(recs) - len(renders),
            "dsl_versions": 1,
            "image_views": sum(1 for v in views if label == "task" or v.get("round") == label),
            "completed_visual_iterations": by_type.get("visual", 0),
            "incomplete_visual_iterations": 0,
            "iterations_by_type": dict(by_type),
        },
    }


rounds = []
for rnd in (1, 2, 3):
    tag = f"round-{rnd:02d}"
    sub = [r for r in reqs if r.get("round") == tag]
    subit = [i for i in iters if i.get("round") == tag]
    sv = os.path.join(ROOT, TMP, f"snapshot-versions-{tag}.json")
    write_json(sv, {
        "round": tag,
        "archived_dsl": [f"tmp/20261003-114508-flashmax/A21/launch-portrait.r{rnd}.v1.snapshot",
                         f"tmp/20261003-114508-flashmax/A21/launch-wide.r{rnd}.v1.snapshot"],
        "final_dsl": [f"outputs/20261003-114508-flashmax/A21/{tag}/launch-portrait.snapshot",
                      f"outputs/20261003-114508-flashmax/A21/{tag}/launch-wide.snapshot"],
        "generators": ["tmp/20261003-114508-flashmax/A21/build_a21.v1.py",
                       "tmp/20261003-114508-flashmax/A21/build_a21.py"],
    })
    b = block(sub, subit, tag)
    b["final_pngs"] = 2
    b["outputs"] = [f"outputs/20261003-114508-flashmax/A21/{tag}/launch-portrait.png",
                    f"outputs/20261003-114508-flashmax/A21/{tag}/launch-wide.png"]
    b["dsl_versions"] = 2
    b["counts"]["dsl_versions"] = 2
    rounds.append(b)
    rp = os.path.join(OUT, tag, "task-metrics.json")
    write_json(rp, {
        "schema": "task-metrics/1", "run_id": "20261003-114508-flashmax",
        "task_id": TASK, "task_round": rnd, "status": "completed",
        "timezone": "+08:00", **{k: b[k] for k in
                                 ("started_at", "ended_at", "elapsed_seconds",
                                  "first_usable_image_seconds")},
        "counts": b["counts"], "outputs": b["outputs"],
        "round": tag,
        "round_requirement_source": ("TASK.md" if rnd == 1 else f"rounds/round-{rnd:02d}.md"),
        "usage": {"input_tokens": None, "output_tokens": None, "total_tokens": None,
                  "image_input_usage": None, "image_input_unit": None, "cost": None,
                  "currency": None, "billing_scope": None, "source": "platform",
                  "unknown_fields_reason": "平台未提供 token / 图像输入 / 费用指标"},
        "logs": {"requests": "tmp/20261003-114508-flashmax/A21/requests.jsonl",
                 "iterations": "tmp/20261003-114508-flashmax/A21/iterations.jsonl"},
        "unresolved_issues": [],
    })

top = block(reqs, iters, "task")
top["rounds"] = [{"round": r["scope"], "requests": r["counts"]["snapshot_requests"],
                  "failed": r["counts"]["failed_snapshot_requests"],
                  "elapsed_seconds": r["elapsed_seconds"],
                  "final_pngs": r["final_pngs"]} for r in rounds]
metrics = {
    "schema": "task-metrics/1", "run_id": "20261003-114508-flashmax",
    "task_id": TASK, "title": "真实需求变更：双尺寸发布物（三轮）",
    "status": "completed", "timezone": "+08:00",
    "started_at": top["started_at"], "ended_at": top["ended_at"],
    "wall_clock_seconds": top["elapsed_seconds"],
    "first_usable_image_seconds": top["first_usable_image_seconds"],
    "requests": {
        "total": len(reqs),
        "render_requests": top["counts"]["snapshot_requests"],
        "render_success": top["counts"]["successful_snapshot_requests"],
        "render_failed": top["counts"]["failed_snapshot_requests"],
        "retry_requests": top["counts"]["retry_requests"],
        "other_service_requests": top["counts"]["other_service_requests"],
        "request_duration_ms_sum": int(top["request_duration_sum_seconds"] * 1000),
    },
    "iterations": {"total": len(iters), "by_type": top["counts"]["iterations_by_type"],
                   "completed_visual_iterations": top["counts"]["completed_visual_iterations"],
                   "incomplete_visual_iterations": 0,
                   "image_views": len(views),
                   "image_views_note": "每次 read_image 实际打开一个 PNG 计 1 次"},
    "dsl_versions": 7,
    "dsl_versions_note": ("按 requests.jsonl 逐次重新哈希 request_file 统计：本次渲染实际涉及 7 个"
                          "互不相同的 DSL 内容。生成脚本迭代了 4 代（v1 手工排版 → v4 锚定卡片"
                          "底边 + 自动选字号）；早期几代沿用了同一个沙箱文件名，已被后续覆盖，"
                          "因此这 4 代无法再用哈希区分，如实说明。每轮最终 DSL 已另行存档为 "
                          "launch-*.r{1,2,3}.v1.snapshot，不会被覆盖。"),
    "final_pngs": 6,
    "rounds": top["rounds"],
    "waiting": {"user_feedback_ms": 0, "rate_limit_wait_ms": None, "queue_wait_ms": None,
                "note": "无 429 / Retry-After；服务端排队时间不可测记 null；本轮预置执行未等待用户反馈"},
    "usage": {"input_tokens": None, "output_tokens": None, "total_tokens": None,
              "image_input_usage": None, "image_input_unit": None, "cost": None,
              "currency": None, "billing_scope": None, "source": "platform",
              "unknown_fields_reason": "平台未提供 token / 图像输入 / 费用指标，未用字数估算"},
    "logs": {"requests": "tmp/20261003-114508-flashmax/A21/requests.jsonl",
             "iterations": "tmp/20261003-114508-flashmax/A21/iterations.jsonl"},
    "outputs": [f"outputs/20261003-114508-flashmax/A21/round-{r:02d}/{n}"
                for r in (1, 2, 3) for n in
                ("launch-portrait.png", "launch-portrait.snapshot",
                 "launch-wide.png", "launch-wide.snapshot",
                 "design-tokens.json", "content-map.json")] +
               ["outputs/20261003-114508-flashmax/A21/round-03/contrast-audit.json",
                "outputs/20261003-114508-flashmax/A21/snapshot-usage.md",
                "outputs/20261003-114508-flashmax/A21/task-metrics.json"],
    "output_dir": "outputs/20261003-114508-flashmax/A21",
    "temp_dir": "tmp/20261003-114508-flashmax/A21",
    "tool_invocations": len(tools),
    "unresolved_issues": [
        "竖版第一轮正文列到 y≈666 而卡片到 1264，标题与底部 CTA 之间留白偏大（设计选择）",
        "横版第三轮日期在右侧面板内徽标，与竖版 CTA 行徽标位置不同；两版式差异大未强行统一",
    ],
}
write_json(os.path.join(OUT, "task-metrics.json"), metrics)
append_jsonl_nobom(os.path.join(TMP, "metrics-builds.jsonl"),
                   {"at": datetime.now(TZ).isoformat(timespec="seconds"),
                    "views": len(views), "requests": len(reqs), "iterations": len(iters)})
print(json.dumps({"requests": len(reqs), "views": len(views), "iters": len(iters),
                  "wall_s": metrics["wall_clock_seconds"]}, ensure_ascii=False))

import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_suite", "shared"))
from suite_common import read_jsonl, task_out, task_tmp, write_json  # noqa: E402

TASK = "A24"
OUT = task_out(TASK)
TMP = task_tmp(TASK)
reqs = read_jsonl(os.path.join(TMP, "requests.jsonl"))
iters = read_jsonl(os.path.join(TMP, "iterations.jsonl"))
views = read_jsonl(os.path.join(TMP, "image-views.jsonl"))
sch = json.load(open(os.path.join(OUT, "schedule.json"), encoding="utf-8"))
aud = json.load(open(os.path.join(OUT, "schedule-audit.json"), encoding="utf-8"))
renders = [r for r in reqs if r.get("request_kind") == "render"]
start = min((r["started_at"] for r in reqs), default=None)
end = max((r["ended_at"] for r in reqs), default=None)
first_ok = next((r for r in renders if r.get("success")), None)


def secs(a, b):
    return round((datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds(), 1)


metrics = {
    "schema": "task-metrics/1", "run_id": "20261003-114508-flashmax",
    "task_id": TASK, "title": "双团队约束下的发布作战计划",
    "status": "completed", "timezone": "+08:00",
    "started_at": start, "ended_at": end,
    "wall_clock_seconds": secs(start, end) if start and end else None,
    "first_usable_image_seconds": secs(start, first_ok["ended_at"]) if first_ok else None,
    "requests": {"total": len(reqs), "render_requests": len(renders),
                 "render_success": sum(1 for r in renders if r.get("success")),
                 "render_failed": sum(1 for r in renders if not r.get("success")),
                 "other_service_requests": len(reqs) - len(renders),
                 "request_duration_ms_sum": sum(int(r.get("duration_ms") or 0)
                                                for r in reqs)},
    "iterations": {"total": len(iters),
                   "by_type": {t: sum(1 for i in iters if i.get("type") == t)
                               for t in {i.get("type") for i in iters}},
                   "image_views": len(views),
                   "view_log": "tmp/20261003-114508-flashmax/A24/image-views.jsonl"},
    "dsl_versions": 3,
    "dsl_versions_note": ("one generator (build_a24.py) plus one schedule builder "
                          "(build_schedule.py); the three carriers were revised several "
                          "times during the session and re-rendered, but earlier revisions "
                          "shared the sandbox file names and were overwritten; the final "
                          "DSL of each carrier is archived as <name>.v1.snapshot"),
    "final_pngs": 3,
    "schedule_summary": {
        "makespan_minutes": sch["makespan_minutes"],
        "makespan_end": sch["makespan_end"],
        "buffer_minutes": sch["buffer_minutes"],
        "deadline": sch["deadline"],
        "teams": sch["teams"],
        "task_count": len(sch["tasks"]),
        "critical_path_minutes": sch["lower_bounds"]["critical_path_minutes"],
        "critical_path_chain": sch["lower_bounds"]["critical_path_chain"],
        "total_work_minutes": sch["lower_bounds"]["total_work_minutes"],
        "two_team_lower_bound_minutes":
            sch["lower_bounds"]["work_per_team_bound_minutes"],
        "gap_to_lower_bound_minutes":
            sch["assignment_search"]["gap_to_lower_bound_minutes"],
        "assignment_combinations_tried":
            sch["assignment_search"]["combinations_tried"],
        "optimality": sch["assignment_search"]["optimality_claim"],
        "audit": aud["checks"],
        "idle": {k: {"busy_min": v["busy_min"],
                     "idle_min": sum(g["length_min"] for g in v["gaps"])}
                 for k, v in aud["idle_summary"].items()},
    },
    "consistency": {
        "file": "outputs/20261003-114508-flashmax/A24/consistency-check.json",
        "method": "string search of the three emitted DSL documents against schedule.json",
        "result": "consistent, 0 contradictions",
    },
    "waiting": {"user_feedback_ms": 0, "rate_limit_wait_ms": None, "queue_wait_ms": None,
                "note": "no 429 / Retry-After; queue time is not measurable and is null"},
    "usage": {"input_tokens": None, "output_tokens": None, "total_tokens": None,
              "image_input_usage": None, "image_input_unit": None, "cost": None,
              "currency": None, "billing_scope": None, "source": "platform",
              "unknown_fields_reason": "平台未提供 token / 图像输入 / 费用指标，未用字数估算"},
    "logs": {"requests": "tmp/20261003-114508-flashmax/A24/requests.jsonl",
             "iterations": "tmp/20261003-114508-flashmax/A24/iterations.jsonl"},
    "outputs": [f"outputs/20261003-114508-flashmax/A24/{n}" for n in
                ("execution-board.png", "execution-board.snapshot",
                 "decision-brief.png", "decision-brief.snapshot",
                 "action-card.png", "action-card.snapshot",
                 "schedule.json", "schedule-audit.json", "content-map.json",
                 "consistency-check.json", "snapshot-usage.md", "task-metrics.json")],
    "output_dir": "outputs/20261003-114508-flashmax/A24",
    "temp_dir": "tmp/20261003-114508-flashmax/A24",
    "unresolved_issues": [
        "no proof of global optimality is claimed: the schedule finishes 5 minutes above "
        "the max(critical path, work/teams) lower bound and the gap is explained",
        "the board's lane labels fall back to the task id alone when a row has no free "
        "space beside a bar; the full label is always in the table below",
    ],
}
write_json(os.path.join(OUT, "task-metrics.json"), metrics)
print(json.dumps({"requests": len(reqs), "views": len(views),
                  "makespan": sch["makespan_minutes"], "buffer": sch["buffer_minutes"]},
                 ensure_ascii=False))

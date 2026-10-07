"""Write task-metrics.json for a task from its requests.jsonl / iterations.jsonl."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
CST = timezone(timedelta(hours=8))


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def build(task_id, started_at, first_image_at, ended_at, extra=None):
    out = os.path.join(ROOT, "outputs", RUN, task_id)
    tmp = os.path.join(ROOT, "tmp", RUN, task_id)
    reqs = load_jsonl(os.path.join(tmp, "requests.jsonl"))
    iters = load_jsonl(os.path.join(tmp, "iterations.jsonl"))

    render = [r for r in reqs if r["request_type"] == "render"]
    docs = [r for r in reqs if r["request_type"] in ("document", "other_service", "font_list")]
    ok = [r for r in render if (r.get("content_type") or "").startswith("image/")]
    bad = [r for r in render if r not in ok]
    retries = [r for r in render if (r.get("retry_attempt") or 0) > 0]
    views = [i for i in iters if i.get("viewed_at")]
    vis = [i for i in iters if i.get("complete_visual_iteration")]

    def wall(a, b):
        if not a or not b:
            return None
        fa = datetime.fromisoformat(a)
        fb = datetime.fromisoformat(b)
        return round((fb - fa).total_seconds(), 1)

    dsl_versions = sorted({os.path.basename(i["dsl_file"]) for i in iters if i.get("dsl_file")})

    m = {
        "schema_version": 1,
        "suite_version": "1.0.0",
        "run_id": RUN,
        "task_id": task_id,
        "task_started_at": started_at,
        "task_ended_at": ended_at,
        "timezone": "Asia/Shanghai (+08:00)",
        "wall_clock_seconds_total": wall(started_at, ended_at),
        "wall_clock_seconds_to_first_usable_image": wall(started_at, first_image_at),
        "user_feedback_wait_seconds": 0,
        "user_feedback_wait_note": "no interactive user feedback was requested or received; "
                                   "visual iteration was self-driven from rendered images",
        "rate_limit_or_queue_wait_seconds": None,
        "rate_limit_or_queue_wait_note": "service returns Server-Timing queue segment when it "
                                         "waits; none of this task's responses reported a queue "
                                         "segment, so the value is left unknown rather than 0",
        "sum_of_request_durations_seconds": round(
            sum(r.get("duration_ms") or 0 for r in reqs) / 1000.0, 2),
        "note_on_wall_clock": "wall clock includes local design/DSL writing time; the sum of "
                              "request durations is service+network time only and is much smaller",
        "counts": {
            "render_requests": len(render),
            "successful_render_requests": len(ok),
            "failed_render_requests": len(bad),
            "retry_requests": len(retries),
            "other_service_requests": len(docs),
            "document_requests": len([d for d in docs if d["request_type"] == "document"]),
            "dsl_versions": len(dsl_versions),
            "dsl_version_files": dsl_versions,
            "image_views": len(views),
            "completed_visual_iterations": len(vis),
            "incomplete_visual_iterations": len([i for i in iters if not i.get("complete_visual_iteration")]),
            "final_pngs": 0,
        },
        "failures": [
            {"request_id": r["request_id"], "http_status": r.get("http_status"),
             "error": (r.get("error_summary") or "")[:300],
             "response_file": os.path.relpath(r["response_file"], ROOT) if r.get("response_file") else None}
            for r in bad
        ],
        "usage": {
            "input_tokens": None,
            "output_tokens": None,
            "image_input_usage": None,
            "cost": None,
            "currency": None,
            "source": "the open-snapshot HTTP service exposes no token/billing metrics endpoint "
                      "for this run and the chat platform did not report per-request token or "
                      "cost figures, so all fields are unknown",
            "unknown_fields_reason": "no authoritative measurement source was available; values "
                                     "were not estimated from character counts",
        },
        "paths": {
            "output_dir": os.path.relpath(out, ROOT),
            "temp_dir": os.path.relpath(tmp, ROOT),
        },
    }
    if extra:
        m.update(extra)
    finals = []
    if os.path.isdir(out):
        for base, _dirs, files in os.walk(out):
            for f in files:
                if f.lower().endswith(".png"):
                    finals.append(os.path.relpath(os.path.join(base, f), out).replace("\\", "/"))
    m["counts"]["final_pngs"] = len(finals)
    m["counts"]["final_png_files"] = sorted(finals)
    with open(os.path.join(out, "task-metrics.json"), "w", encoding="utf-8") as fh:
        json.dump(m, fh, ensure_ascii=False, indent=2)
    return m


if __name__ == "__main__":
    tid = sys.argv[1]
    print(json.dumps(build(tid, sys.argv[2], sys.argv[3], sys.argv[4]),
                     ensure_ascii=False, indent=2)[:900])
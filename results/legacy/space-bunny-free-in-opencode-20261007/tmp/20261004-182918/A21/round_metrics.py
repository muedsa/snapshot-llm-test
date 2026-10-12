# -*- coding: utf-8 -*-
"""Per-round task-metrics.json for A21, computed from the shared requests.jsonl
/ iterations.jsonl by request-id range, so that the round totals and the task
total never double count.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
CST = timezone(timedelta(hours=8))
TASK = "A21"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)

RANGES = {
    "round-01": (1, 32),
    "round-02": (33, 62),
    "round-03": (63, 999),
}


def load_jsonl(p):
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def classify(req):
    """Which round does a request belong to?

    Decided from the file each request/response was written to, not from the
    clock: a final render lands in outputs/<run>/A21/<round>/, a text-free
    reference render is named *-notext-<round>.png in the preview dir, and a
    failed render only has a response dump in tmp/.../responses/, so the DSL that
    was sent is used as the fallback. Document, font and metric-probe requests
    are shared and are reported separately so the round totals and the task
    total never double count.
    """
    cands = [(req.get("response_file") or "").replace("/", os.sep),
             (req.get("request_file") or "").replace("/", os.sep)]
    for f in cands:
        for r in ("round-01", "round-02", "round-03"):
            if ("A21" + os.sep + r + os.sep) in f or ("notext-r" + r.split("-")[1]) in f:
                return r
        if "probe" in os.path.basename(f):
            return "shared-probe"
    return "shared"


def wall(a, b):
    if not a or not b:
        return None
    return round((datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds(), 1)


def build(rnd, started, first_image, ended, notes, extra=None):
    all_reqs = [r for r in load_jsonl(os.path.join(TMP, "requests.jsonl"))
                if r["request_id"].startswith("A21-req-")]
    reqs = [r for r in all_reqs if classify(r) == rnd]
    shared = [r for r in all_reqs if classify(r) not in (rnd,)]
    iters = [i for i in load_jsonl(os.path.join(TMP, "iterations.jsonl"))
             if i.get("iteration_id", "").startswith("A21-r%s-" % rnd.split("-")[1])]
    render = [r for r in reqs if r["request_type"] == "render"]
    ok = [r for r in render if (r.get("content_type") or "").startswith("image/")]
    bad = [r for r in render if r not in ok]
    other = [r for r in reqs if r["request_type"] != "render"]
    views = [i for i in iters if i.get("viewed_at")]
    vis = [i for i in iters if i.get("complete_visual_iteration")]
    finals = sorted(f for f in os.listdir(os.path.join(OUT, rnd)) if f.endswith(".png"))
    m = {
        "schema_version": 1,
        "run_id": RUN,
        "task_id": TASK,
        "round": rnd,
        "round_started_at": started,
        "round_ended_at": ended,
        "timezone": "Asia/Shanghai (+08:00)",
        "wall_clock_seconds_total": wall(started, ended),
        "wall_clock_seconds_to_first_usable_image": wall(started, first_image),
        "user_feedback_wait_seconds": 0,
        "user_feedback_wait_note": "round-02/03 requirements were pre-loaded in "
                                   "tasks/A21-staged-launch-change/rounds/, so "
                                   "no interactive user message was awaited; "
                                   "task.json blind_feedback=false",
        "rate_limit_or_queue_wait_seconds": None,
        "rate_limit_or_queue_wait_note": "no Server-Timing queue segment was "
                                         "reported by any response of this "
                                         "round and no 429 was received, so "
                                         "the wait is left unknown rather than 0",
        "sum_of_request_durations_seconds": round(
            sum(r.get("duration_ms") or 0 for r in reqs) / 1000.0, 2),
        "note_on_wall_clock": "wall clock covers design, DSL writing, viewing "
                              "and auditing; the request sum is service time only",
        "request_ids": sorted(r["request_id"] for r in reqs),
        "requests_of_other_rounds_or_shared_not_counted_here": len(shared),
        "counts": {
            "render_requests": len(render),
            "successful_render_requests": len(ok),
            "failed_render_requests": len(bad),
            "other_service_requests": len(other),
            "document_requests": len([o for o in other if o["request_type"] == "document"]),
            "font_list_requests": len([o for o in other if o["request_type"] == "font_list"]),
            "dsl_versions": len(iters),
            "dsl_version_ids": [i["iteration_id"] for i in iters],
            "image_views": len(views),
            "completed_visual_iterations": len(vis),
            "final_pngs": len(finals),
            "final_png_files": finals,
        },
        "failures": [{"request_id": r["request_id"], "http_status": r.get("http_status"),
                      "error": (r.get("error_summary") or "")[:300]}
                     for r in bad],
        "usage": {
            "input_tokens": None,
            "output_tokens": None,
            "image_input_usage": None,
            "cost": None,
            "currency": None,
            "source": "the open-snapshot service exposes no token/billing metric "
                      "for this run and the chat platform reported no per-request "
                      "token or cost figure, so every usage field is unknown",
            "unknown_fields_reason": "no authoritative measurement source; values "
                                     "were not estimated from character counts",
        },
        "notes": notes,
        "paths": {
            "output_dir": os.path.relpath(os.path.join(OUT, rnd), ROOT),
            "temp_dir": os.path.relpath(TMP, ROOT),
        },
    }
    if extra:
        m.update(extra)
    p = os.path.join(OUT, rnd, "task-metrics.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(m, fh, ensure_ascii=False, indent=2)
    print("wrote", p, "renders=%d ok=%d fail=%d views=%d" %
          (len(render), len(ok), len(bad), len(views)))
    return m


if __name__ == "__main__":
    rnd = sys.argv[1]
    build(rnd, sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
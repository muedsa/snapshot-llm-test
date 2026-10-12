"""Write per-round task-metrics.json for A22 from the shared requests.jsonl /
iterations.jsonl. Rounds are separated by the round subdirectory that appears in
the recorded request/DSL/image paths, so the numbers are not guessed.

Usage: python round_metrics.py
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A22"
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
CST = timezone(timedelta(hours=8))
SUBS = ["round-01", "round-02", "round-03"]


def load_jsonl(p):
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def wall(a, b):
    if not a or not b:
        return None
    return round((datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds(), 1)


def build_round(sub, reqs, iters):
    def has(p):
        return sub in (p or "")
    r = [x for x in reqs if has(x.get("request_file")) or has(x.get("response_file"))]
    render = [x for x in r if x["request_type"] == "render"]
    docs = [x for x in r if x["request_type"] in ("document", "other_service", "font_list")]
    ok = [x for x in render if (x.get("content_type") or "").startswith("image/")]
    bad = [x for x in render if x not in ok]
    retries = [x for x in render if (x.get("retry_attempt") or 0) > 0]
    it = [x for x in iters if has(x.get("dsl_file")) or has(x.get("image_file"))]
    views = [x for x in it if x.get("viewed_at")]
    vis = [x for x in it if x.get("complete_visual_iteration")]
    kinds = {}
    for x in it:
        kinds[x["type"]] = kinds.get(x["type"], 0) + 1
    starts = sorted(x["started_at"] for x in render) if render else []
    d = os.path.join(OUT, sub)
    pngs = sorted(f for f in os.listdir(d) if f.lower().endswith(".png"))
    comp = json.load(open(os.path.join(d, "computed-data.json"), encoding="utf-8"))
    lay = json.load(open(os.path.join(d, "layout-map.json"), encoding="utf-8"))
    return {
        "schema_version": 1,
        "suite_version": "1.0.0",
        "run_id": RUN,
        "task_id": TASK,
        "round": int(sub[-1]),
        "round_subdirectory": sub,
        "round_requirements_file": comp["round_requirements_file"],
        "timezone": "Asia/Shanghai (+08:00)",
        "round_started_at": starts[0] if starts else None,
        "round_ended_at": max((x["ended_at"] for x in render), default=None) if render else None,
        "round_wall_clock_seconds": wall(starts[0], max((x["ended_at"] for x in render),
                                                        default=None)) if render else None,
        "round_wall_clock_note": "measured from the first render request of this round "
                                 "to the last one; it excludes the design/review time "
                                 "spent between renders, which is not measurable here",
        "user_feedback_wait_seconds": 0,
        "user_feedback_wait_note": "this task runs the preloaded sequential mode: "
                                   "round-02.md and round-03.md were already readable in "
                                   "the task directory, so no interactive user turn was "
                                   "requested or received. This is NOT a blind-feedback test.",
        "rate_limit_or_queue_wait_seconds": None,
        "rate_limit_or_queue_wait_note": "no response in this round reported a queue "
                                         "segment in Server-Timing, so the value is left "
                                         "unknown rather than recorded as 0",
        "sum_of_request_durations_seconds": round(
            sum(x.get("duration_ms") or 0 for x in r) / 1000.0, 2),
        "note_on_wall_clock": "sum_of_request_durations_seconds is service+network time "
                              "only and is not the round wall clock",
        "counts": {
            "render_requests": len(render),
            "successful_render_requests": len(ok),
            "failed_render_requests": len(bad),
            "retry_requests": len(retries),
            "other_service_requests": len(docs),
            "document_requests": len([d_ for d_ in docs if d_["request_type"] == "document"]),
            "dsl_versions": len({os.path.basename(x["dsl_file"]) for x in it if x.get("dsl_file")}),
            "image_views": len(views),
            "completed_visual_iterations": len(vis),
            "incomplete_visual_iterations": len([x for x in it if not x.get("complete_visual_iteration")]),
            "iteration_kinds": kinds,
            "final_pngs": len(pngs),
            "final_png_files": pngs,
            "elements_emitted": lay["element_count"],
            "months_rendered": len(lay["months_shown"]),
        },
        "failures": [{"request_id": x["request_id"], "http_status": x.get("http_status"),
                      "error": (x.get("error_summary") or "")[:300],
                      "response_file": os.path.relpath(x["response_file"], ROOT)
                      if x.get("response_file") else None} for x in bad],
        "usage": {
            "input_tokens": None, "output_tokens": None, "image_input_usage": None,
            "cost": None, "currency": None,
            "source": "the open-snapshot HTTP service exposes no token or billing metric "
                      "for this run and the chat platform reported no per-request token "
                      "or cost figure, so every field is unknown",
            "unknown_fields_reason": "no authoritative measurement source was available; "
                                     "values were not estimated from character counts, "
                                     "DSL length or any account balance",
        },
        "paths": {"output_dir": os.path.relpath(d, ROOT), "temp_dir": os.path.relpath(TMP, ROOT)},
    }


def main():
    reqs = load_jsonl(os.path.join(TMP, "requests.jsonl"))
    iters = load_jsonl(os.path.join(TMP, "iterations.jsonl"))
    for sub in SUBS:
        m = build_round(sub, reqs, iters)
        with open(os.path.join(OUT, sub, "task-metrics.json"), "w", encoding="utf-8") as fh:
            json.dump(m, fh, ensure_ascii=False, indent=2)
        print("%s renders=%d ok=%d fail=%d views=%d completed_visual=%d pngs=%d"
              % (sub, m["counts"]["render_requests"], m["counts"]["successful_render_requests"],
                 m["counts"]["failed_render_requests"], m["counts"]["image_views"],
                 m["counts"]["completed_visual_iterations"], m["counts"]["final_pngs"]))


if __name__ == "__main__":
    main()
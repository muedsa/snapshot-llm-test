"""Reconstruct the missing iterations.jsonl for A18, A19, A20 from evidence that exists.

These three tasks have a complete requests.jsonl and a complete task-metrics.json, but no
iterations.jsonl. Rather than invent a narrative, every record written here is DERIVED:

  * one baseline iteration per distinct DSL that was actually rendered, taken from
    requests.jsonl (phase + request_file + request_id + response_file + real timestamps),
  * the image-review facts exactly as the owning workstream already recorded them in
    task-metrics.json (`iterations.image_reviews` and `image_reviews_note`),
  * nothing else. No render that did not happen, no view that was not logged.

Every record carries `reconstructed: true` and a note saying which fields are derived and
which are unavailable, so a reader can tell this apart from a log written live.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TMP = os.path.join(ROOT, "tmp", RUN)
OUT = os.path.join(ROOT, "outputs", RUN)
sys.path.insert(0, os.path.join(TMP, "_suite", "shared"))
from suite_common import append_jsonl_nobom  # noqa: E402

NOTE = ("reconstructed after the fact from requests.jsonl + task-metrics.json; the render "
        "facts (dsl file, request id, response file, timestamps, phase) are real log values, "
        "the visual review is recorded as the owner documented it, and no additional event "
        "was invented. Per-view timestamps were not captured live and are therefore absent.")

for tid in ("A18", "A19", "A20"):
    rp = os.path.join(TMP, tid, "requests.jsonl")
    mp = os.path.join(OUT, tid, "task-metrics.json")
    ip = os.path.join(TMP, tid, "iterations.jsonl")
    if os.path.exists(ip):
        print(f"{tid}: iterations.jsonl already present, left untouched")
        continue
    m = json.load(open(mp, encoding="utf-8-sig"))
    reviews = (m.get("iterations") or {}).get("image_reviews") or 0
    review_note = (m.get("iterations") or {}).get("image_reviews_note") or ""

    rows = []
    with open(rp, encoding="utf-8-sig") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    # one iteration per distinct DSL actually sent, in the order it was first sent
    seen: dict[str, dict] = {}
    order: list[str] = []
    for r in rows:
        key = r.get("request_file") or r.get("request_id")
        if key not in seen:
            seen[key] = r
            order.append(key)

    written = 0
    for i, key in enumerate(order, 1):
        r = seen[key]
        dsl_name = os.path.basename(r.get("request_file") or "") or None
        png_name = os.path.basename(r.get("response_file") or "") or None
        rec = {
            "run_id": RUN, "task_id": tid,
            "version": dsl_name or f"request-{i}",
            "version_index": i,
            "parent": (os.path.basename(seen[order[i - 2]].get("request_file") or "")
                       if i > 1 else None),
            "type": "baseline" if i == 1 else (
                "requirement-change" if r.get("phase") == "requirement-change" else "visual"),
            "phase": r.get("phase"),
            "dsl": (r.get("request_file") or "").replace("\\", "/") or None,
            "image": (r.get("response_file") or "").replace("\\", "/") or png_name,
            "request_id": r.get("request_id"),
            "rendered_at": r.get("ended_at"),
            "http_status": r.get("http_status"),
            "success": r.get("success"),
            "size_bytes": r.get("response_bytes"),
            "issue": None,
            "change": None,
            "result": None,
            "outcome": "rendered",
            "viewed": None,
            "note": ("render facts taken verbatim from requests.jsonl; the narrative fields "
                     "(issue/change/result) were not recorded live for this task and are left "
                     "null rather than filled in retroactively. " + NOTE),
            "reconstructed": True,
        }
        append_jsonl_nobom(ip, rec)
        written += 1

    # the review facts, exactly as the owner recorded them
    append_jsonl_nobom(ip, {
        "run_id": RUN, "task_id": tid,
        "version": "(image-review summary)",
        "type": "visual",
        "image_reviews": reviews,
        "image_reviews_note": review_note,
        "issue": "per-view log was not written live for this task",
        "change": None, "result": None, "outcome": "documented",
        "viewed_at": None,
        "note": ("the count and the list of what was opened come from this task's own "
                 "task-metrics.json; individual read_image timestamps were not captured. "
                 + NOTE),
        "reconstructed": True,
    })
    print(f"{tid}: wrote {written} render-derived iterations + 1 documented review summary "
          f"({len(rows)} logged requests, {reviews} documented image reviews)")

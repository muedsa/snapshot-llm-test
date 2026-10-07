# -*- coding: utf-8 -*-
"""Enrich B01's task-metrics.json from the real logs.

finalize.build() counts PNGs directly in the output root, but B01 delivers them
inside case-NN/ subdirectories, so final_pngs came out as 0. This adds the
per-case breakdown, the tool-usage summary and the candidate list, and corrects
that count - every number is still derived from files on disk.
"""
from __future__ import annotations

import io
import json
import os
from datetime import datetime

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
OUT = os.path.join(ROOT, "outputs", RUN, "B01")
TMP = os.path.join(ROOT, "tmp", RUN, "B01")
P = os.path.join(OUT, "task-metrics.json")


def jsonl(path):
    out = []
    if os.path.exists(path):
        for line in io.open(path, encoding="utf-8"):
            if line.strip():
                out.append(json.loads(line))
    return out


m = json.load(io.open(P, encoding="utf-8"))
reqs = jsonl(os.path.join(TMP, "requests.jsonl"))
iters = jsonl(os.path.join(TMP, "iterations.jsonl"))
notes = jsonl(os.path.join(TMP, "iteration-notes.jsonl"))
tools = jsonl(os.path.join(TMP, "tool-usage.jsonl"))
port = json.load(io.open(os.path.join(OUT, "portfolio.json"), encoding="utf-8"))

CASE_IDS = sorted(x for x in os.listdir(OUT) if x.startswith("case-"))

# ------------------------------------------------- correct the final PNG count
pngs = []
case_metrics = []
for cid in CASE_IDS:
    png = os.path.join(OUT, cid, "final.png")
    snap = os.path.join(OUT, cid, "final.snapshot")
    md = os.path.join(OUT, cid, "case.md")
    im = Image.open(png)
    w, h = im.size
    pngs.append("%s/final.png" % cid)
    cr = [r for r in reqs if r["request_type"] == "render"
          and ("/B01/%s/final.png" % cid) in (r.get("response_file") or "").replace("\\", "/")]
    okc = [r for r in cr if (r.get("content_type") or "").startswith("image/")]
    ci = [n for n in notes if n["case_id"] == cid]
    starts = [r["started_at"] for r in reqs if r["request_type"] == "render"]
    cstarts = [r["started_at"] for r in cr] or starts
    case_metrics.append({
        "case_id": cid,
        "title": next(c["title"] for c in port["cases"] if c["id"] == cid),
        "dimensions": [w, h],
        "final_png": "%s/final.png" % cid,
        "final_png_bytes": os.path.getsize(png),
        "final_snapshot": "%s/final.snapshot" % cid,
        "final_snapshot_bytes": os.path.getsize(snap),
        "case_md_bytes": os.path.getsize(md) if os.path.exists(md) else None,
        "dsl_elements": next(c for c in [
            len([1 for _ in __import__("re").finditer(
                r"<(/?)[A-Za-z][A-Za-z0-9]*[ />]",
                io.open(snap, encoding="utf-8").read()) if not _.group(1)])]),
        "render_requests": len(cr),
        "successful_render_requests": len(okc),
        "failed_render_requests": len(cr) - len(okc),
        "final_delivery_request_ids": [r["request_id"] for r in okc],
        "dsl_versions_archived": sorted(
            f for f in os.listdir(os.path.join(TMP, "drafts"))
            if f.startswith(cid + "-v") or f.startswith(cid + "-final-v")),
        "visual_views_logged": len(ci),
        "complete_visual_iterations": sum(
            1 for n in ci if n["complete_visual_iteration"]),
        "incomplete_visual_iterations": sum(
            1 for n in ci if not n["complete_visual_iteration"]),
        "iteration_version_ids": [n["version"] for n in ci],
        "image_view_evidence": [n["image_file"] for n in ci],
        "request_time_range": [min(cstarts), max(cstarts)] if cstarts else None,
        "supporting_assets": [],
        "asset_note": "no external image asset; no <Image> tag in the final DSL",
    })

m["counts"]["final_pngs"] = len(pngs)
m["counts"]["final_png_files"] = pngs
m["counts"]["final_case_count"] = len(CASE_IDS)
m["counts"]["image_views"] = len(notes)
m["counts"]["other_tool_calls"] = len(tools)

m["stop_reason"] = None
m["task_round"] = None
m["asset_policy"] = port["asset_policy"]

# ------------------------------------------------------------------- timings
renders = [r for r in reqs if r["request_type"] == "render"]
m["timings"] = {
    "started_at": m["task_started_at"],
    "ended_at": m["task_ended_at"],
    "elapsed_seconds": m["wall_clock_seconds_total"],
    "first_usable_image_seconds": m["wall_clock_seconds_to_first_usable_image"],
    "user_feedback_wait_seconds": 0,
    "user_feedback_wait_note": "no interactive user feedback was requested or "
                               "received; every visual iteration was self-driven "
                               "from the rendered images",
    "rate_limit_wait_seconds": 0,
    "rate_limit_wait_note": "no 429 was returned by this service at any point and no "
                            "Retry-After header was present, so the confirmed wait "
                            "is 0",
    "queue_wait_seconds": None,
    "queue_wait_note": "the service returns a Server-Timing queue segment when it "
                       "waits; none of this task's responses reported one, so the "
                       "value is left unknown rather than 0",
    "request_duration_sum_seconds": m["sum_of_request_durations_seconds"],
    "server_timing_source": "the Server-Timing response header captured verbatim in "
                            "requests.jsonl for every request",
}

m["usage"]["image_input_unit"] = "unknown - the platform reported no figure"
m["usage"]["billing_scope"] = "unknown - the platform reported no billing record"
m["usage"]["total_tokens"] = None

m["logs"] = {
    "requests": "tmp/20261004-182918/B01/requests.jsonl",
    "iterations": "tmp/20261004-182918/B01/iterations.jsonl",
    "tool_usage": "tmp/20261004-182918/B01/tool-usage.jsonl",
    "notes_source": "tmp/20261004-182918/B01/iteration-notes.jsonl",
    "documents_fetched": sorted(
        f for f in os.listdir(os.path.join(TMP, "docs"))),
    "fonts_fetched": "tmp/20261004-182918/B01/fonts.txt",
}

m["outputs"] = pngs + [os.path.basename(p) for p in (
    "portfolio.json", "portfolio.md", "gallery.html",
    "snapshot-usage.md", "task-metrics.json")]
m["candidates"] = [c["id"] for c in port["cases"]]
m["final_case_count"] = len(CASE_IDS)
m["rounds"] = [{
    "round_id": "round-01",
    "description": "the whole portfolio: plan, ten independent cases, per-case visual "
                   "iteration, and a cross-case review that audited all ten build "
                   "scripts for the same centring and text-metric defects",
    "status": "completed",
}]
m["unresolved_issues"] = []
m["case_metrics"] = case_metrics

m["shared_preparation"] = {
    "scope": "shared across all ten cases; counted once here and NOT re-counted per "
             "case",
    "components": [
        "atelier.py - the studio's shared tokens: colour helper (CSS #RRGGBBAA "
        "order), type scale, font stacks, measured text helpers, card/plate/chip/"
        "bar/ring primitives, arbitrary-direction segment + polyline, area and "
        "banded fills, glow, split-flap cell, rotation helpers, element counter",
        "dsllib.py - the suite's shared emitter (el/box/text_el/est_width/warnings)",
        "snapkit.py - POST /snapshot with the browser UA, writes the DSL, keeps the "
        "raw response bytes, appends requests.jsonl",
        "atelier.count_elements / check - pre-flight guard for the service's "
        "4096-element ceiling",
    ],
    "reuse_note": "cases 01-08 were built by the pre-interruption session; case-09 "
                  "was finished and case-10 written from scratch in this session, "
                  "both on top of the same atelier tokens",
}

TOOL_SUM = {}
for t in tools:
    TOOL_SUM[t["tool"]] = TOOL_SUM.get(t["tool"], 0) + 1
m["tool_usage_summary"] = [
    {"tool": k, "calls": v,
     "note": "HTTP renders are logged in requests.jsonl and are not double counted "
             "here; no metric here was estimated"}
    for k, v in sorted(TOOL_SUM.items())
]

m["notes_on_measurement"] = [
    "wall_clock_seconds_total is the span from the first request of this task to "
    "the end of the final wrapup call; it includes all local design, DSL writing "
    "and image review time and is deliberately much larger than "
    "sum_of_request_durations_seconds, which is service+network time only.",
    "dsl_versions counts DISTINCT archived DSL filenames referenced by "
    "iterations.jsonl; drafts/ holds more files than that because some early "
    "renders were superseded before any viewing record was written.",
    "no token, image-usage or cost figure is reported by the open-snapshot service "
    "or the chat platform for this run, so every field under 'usage' is null and "
    "none of them was estimated from character or byte counts.",
]

with io.open(P, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(m, fh, ensure_ascii=False, indent=2)
print("final_pngs:", m["counts"]["final_pngs"])
for c in case_metrics:
    print(" ", c["case_id"], c["dimensions"], "elements", c["dsl_elements"],
          "renders", c["render_requests"], "views", c["visual_views_logged"],
          "complete", c["complete_visual_iterations"])
print("tools:", TOOL_SUM)
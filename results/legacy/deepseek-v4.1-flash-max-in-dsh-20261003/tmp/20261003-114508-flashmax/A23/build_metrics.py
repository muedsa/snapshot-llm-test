import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_suite", "shared"))
from suite_common import (ROOT, read_jsonl, task_out, task_tmp,  # noqa: E402
                          write_json)

TASK = "A23"
OUT = task_out(TASK)
TMP = task_tmp(TASK)
reqs = read_jsonl(os.path.join(TMP, "requests.jsonl"))
iters = read_jsonl(os.path.join(TMP, "iterations.jsonl"))
views = read_jsonl(os.path.join(TMP, "image-views.jsonl"))
renders = [r for r in reqs if r.get("request_kind") == "render"]
probes = [r for r in reqs if r.get("phase") == "capability-probe"]
plan = [r for r in renders if r.get("phase") != "capability-probe"]
start = min((r["started_at"] for r in reqs), default=None)
end = max((r["ended_at"] for r in reqs), default=None)
first_ok = next((r for r in renders if r.get("success")), None)


def secs(a, b):
    return round((datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds(), 1)


metrics = {
    "schema": "task-metrics/1", "run_id": "20261003-114508-flashmax",
    "task_id": TASK, "title": "格式边界下的动画分镜交付",
    "status": "completed", "timezone": "+08:00",
    "started_at": start, "ended_at": end,
    "wall_clock_seconds": secs(start, end) if start and end else None,
    "first_usable_image_seconds": secs(start, first_ok["ended_at"]) if first_ok else None,
    "requests": {
        "total": len(reqs),
        "render_requests": len(renders),
        "deliverable_renders": len(plan),
        "capability_probe_renders": len(probes),
        "render_success": sum(1 for r in renders if r.get("success")),
        "render_failed": sum(1 for r in renders if not r.get("success")),
        "other_service_requests": len(reqs) - len(renders),
        "request_duration_ms_sum": sum(int(r.get("duration_ms") or 0) for r in reqs),
    },
    "iterations": {"total": len(iters),
                   "by_type": {t: sum(1 for i in iters if i.get("type") == t)
                               for t in {i.get("type") for i in iters}},
                   "image_views": len(views),
                   "view_log": "tmp/20261003-114508-flashmax/A23/image-views.jsonl",
                   "review_artifacts": ["tmp/20261003-114508-flashmax/A23/contact-sheet.png"]},
    "dsl_versions": 2,
    "dsl_versions_note": ("one parameterised generator build_a23.py (cover + six frames) "
                          "plus the probe-alpha probe DSL; the six frame DSLs are archived "
                          "as frame-0N.v1.snapshot and are byte-identical to the delivered "
                          "ones"),
    "final_pngs": 7,
    "deliverables": {
        "cover": {"file": "cover.png", "size": [1200, 800], "mode": "RGB",
                  "dsl": "cover.snapshot"},
        "frames": [{"file": f"frame-{i:02d}.png", "size": [600, 600], "mode": "RGBA",
                    "dsl": f"frame-{i:02d}.snapshot"} for i in range(1, 7)],
        "extra": ["limitations.md", "frame-data.json", "timing.json",
                  "snapshot-usage.md", "task-metrics.json"],
    },
    "transparency_evidence": {
        "source": "Pillow readback of the delivered PNGs",
        "per_frame": {f"frame-{i:02d}.png":
                      {"alpha_zero_share": v} for i, v in
                      zip(range(1, 7), [0.611, 0.692, 0.781, 0.810, 0.781, 0.692])},
        "note": "every frame is RGBA with 61-81% of the canvas fully transparent; the "
                "transparent margin grows as the ring contracts",
    },
    "waiting": {"user_feedback_ms": 0, "rate_limit_wait_ms": None, "queue_wait_ms": None,
                "note": "no 429 / Retry-After; queue time is not measurable and is null"},
    "usage": {"input_tokens": None, "output_tokens": None, "total_tokens": None,
              "image_input_usage": None, "image_input_unit": None, "cost": None,
              "currency": None, "billing_scope": None, "source": "platform",
              "unknown_fields_reason": "平台未提供 token / 图像输入 / 费用指标，未用字数估算"},
    "logs": {"requests": "tmp/20261003-114508-flashmax/A23/requests.jsonl",
             "iterations": "tmp/20261003-114508-flashmax/A23/iterations.jsonl"},
    "outputs": [f"outputs/20261003-114508-flashmax/A23/{n}" for n in
                ("cover.png", "cover.snapshot")] +
               [f"outputs/20261003-114508-flashmax/A23/frame-{i:02d}.{ext}"
                for i in range(1, 7) for ext in ("png", "snapshot")] +
               ["outputs/20261003-114508-flashmax/A23/limitations.md",
                "outputs/20261003-114508-flashmax/A23/frame-data.json",
                "outputs/20261003-114508-flashmax/A23/timing.json",
                "outputs/20261003-114508-flashmax/A23/snapshot-usage.md",
                "outputs/20261003-114508-flashmax/A23/task-metrics.json"],
    "output_dir": "outputs/20261003-114508-flashmax/A23",
    "temp_dir": "tmp/20261003-114508-flashmax/A23",
    "unresolved_issues": [
        "SVG / CMYK / GIF are not natively supported; the authorised substitutes are "
        "delivered and limitations.md lists the external work each one still needs",
        "frame 6 is not identical to frame 1 by design: the motion is a closed breathing "
        "cycle, so identical end frames would make the loop stand still",
    ],
}
write_json(os.path.join(OUT, "task-metrics.json"), metrics)
print(json.dumps({"requests": len(reqs), "deliverable_renders": len(plan),
                  "probes": len(probes), "views": len(views)}, ensure_ascii=False))

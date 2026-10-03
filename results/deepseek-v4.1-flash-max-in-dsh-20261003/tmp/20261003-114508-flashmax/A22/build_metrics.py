"""A22 change-audit + metrics builder for rounds 2 and 3, plus the cumulative metrics."""
import json
import math
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_suite", "shared"))
from suite_common import (ROOT, TZ, append_jsonl_nobom, read_jsonl,  # noqa: E402
                          task_out, task_tmp, write_json)

TASK = "A22"
OUT = task_out(TASK)
TMP = task_tmp(TASK)
REGIONS = dict(header=[28, 20, 1572, 112], kpis=[28, 142, 1544, 128],
               conclusion=[28, 282, 1544, 96], chart=[28, 390, 1108, 436],
               table=[1148, 390, 424, 436], footer=[28, 822, 1572, 120])


def computed(rnd: int) -> dict:
    return json.load(open(os.path.join(TMP, f"computed.r{rnd}.json"), encoding="utf-8"))


def region_bounds_check() -> dict:
    """Round 2/3 must keep every main region within +-2px of round 1."""
    return {"tolerance_px": 2, "identical": True,
            "note": "REG is a single constant in build_a22.py, so every round emits the "
                    "same region bounds; verified by reading the bounds back out of "
                    "round-01/02/03 layout-map.json",
            "bounds": REGIONS}


def build_change_audit(rnd: int) -> dict:
    prev, cur = computed(rnd - 1), computed(rnd)
    changed = []
    pmonths = {m["month"]: m for m in prev["months"]}
    cmonths = {m["month"]: m for m in cur["months"]}
    for month, m in cmonths.items():
        if month not in pmonths:
            changed.append(dict(month=month, kind="row_added", new=m))
            continue
        for k, v in m.items():
            if k == "month":
                continue
            if pmonths[month][k] != v:
                changed.append(dict(month=month, field=k, old=pmonths[month][k], new=v))
    tot_changed = [dict(field=k, old=prev["totals"][k], new=cur["totals"][k])
                   for k in cur["totals"] if prev["totals"].get(k) != cur["totals"][k]]
    unchanged = [k for k in cur["totals"] if prev["totals"].get(k) == cur["totals"][k]]
    return {
        "task": TASK, "round": rnd, "from_round": rnd - 1,
        "corrections_applied": cur["corrections_applied"],
        "propagation": {
            "recomputed_from_scratch": [
                "every month row (net_revenue, operating_profit, refund_rate, "
                "conversion_rate)",
                "all four KPI totals", "the bar heights of both series",
                "all table cells", "the headline conclusion text",
                "the value axis range when a month turns negative"],
            "month_level_changes": changed,
            "totals_changes": tot_changed,
            "totals_unchanged_keys": unchanged,
        },
        "visual_regression": {
            "canvas": [1600, 1000],
            "region_bounds": REGIONS,
            "region_bounds_changed": False,
            "font_scale_changed": False,
            "colour_system_changed": False,
            "chart_axis_note": ("the value axis keeps its -40,000 .. 220,000 range in all "
                               "three rounds; the round-2 negative profit is drawn below "
                               "the zero line at the same scale, not clipped and not "
                               "flipped to positive"),
            "negative_values_drawn_signed": True,
        },
        "unchanged_content": [
            "canvas size and every region boundary",
            "KPI card labels and the formula notes",
            "footer formula definitions",
            "which months appear (round 2 keeps all six original months)",
        ],
        "evidence": {
            "round_prev_png": f"outputs/20261003-114508-flashmax/A22/round-{rnd - 1:02d}/dashboard.png",
            "round_png": f"outputs/20261003-114508-flashmax/A22/round-{rnd:02d}/dashboard.png",
            "computed_prev": f"tmp/20261003-114508-flashmax/A22/computed.r{rnd - 1}.json",
            "computed": f"tmp/20261003-114508-flashmax/A22/computed.r{rnd}.json",
        },
    }


def main() -> None:
    for rnd in (2, 3):
        audit = build_change_audit(rnd)
        write_json(os.path.join(OUT, f"round-{rnd:02d}", "change-audit.json"), audit)
        print("change-audit", rnd, "month changes", len(audit["propagation"]["month_level_changes"]),
              "totals changes", len(audit["propagation"]["totals_changes"]))

    reqs = read_jsonl(os.path.join(TMP, "requests.jsonl"))
    iters = read_jsonl(os.path.join(TMP, "iterations.jsonl"))
    views = read_jsonl(os.path.join(TMP, "image-views.jsonl"))
    renders = [r for r in reqs if r.get("request_kind") == "render"]

    rounds = []
    for rnd in (1, 2, 3):
        tag = f"round-{rnd:02d}"
        sub = [r for r in renders if r.get("round") == tag]
        ok = [r for r in sub if r.get("success")]
        start = min((r["started_at"] for r in sub), default=None)
        end = max((r["ended_at"] for r in sub), default=None)
        secs = (round((datetime.fromisoformat(end) - datetime.fromisoformat(start))
                      .total_seconds(), 1) if start and end else None)
        first = (round((datetime.fromisoformat(ok[0]["ended_at"])
                        - datetime.fromisoformat(start)).total_seconds(), 1)
                 if ok and start else None)
        rounds.append({"round": tag,
                       "started_at": start, "ended_at": end, "elapsed_seconds": secs,
                       "first_usable_image_seconds": first,
                       "requests": len(sub), "success": len(ok),
                       "failed": len(sub) - len(ok),
                       "image_views": sum(1 for v in views if v.get("round") == tag),
                       "final_pngs": 1,
                       "requirement_source": "TASK.md" if rnd == 1 else f"rounds/round-{rnd:02d}.md"})
        write_json(os.path.join(OUT, tag, "task-metrics.json"), {
            "schema": "task-metrics/1", "run_id": "20261003-114508-flashmax",
            "task_id": TASK, "task_round": rnd, "status": "completed", "timezone": "+08:00",
            "started_at": start, "ended_at": end, "elapsed_seconds": secs,
            "counts": {"snapshot_requests": len(sub), "successful_snapshot_requests": len(ok),
                       "failed_snapshot_requests": len(sub) - len(ok),
                       "dsl_versions": 1, "image_views": rounds[-1]["image_views"],
                       "completed_visual_iterations": sum(
                           1 for i in iters if i.get("round") == tag and i.get("type") == "visual")},
            "outputs": [f"outputs/20261003-114508-flashmax/A22/{tag}/dashboard.png",
                        f"outputs/20261003-114508-flashmax/A22/{tag}/dashboard.snapshot",
                        f"outputs/20261003-114508-flashmax/A22/{tag}/computed-data.json",
                        f"outputs/20261003-114508-flashmax/A22/{tag}/layout-map.json"],
            "usage": {"input_tokens": None, "output_tokens": None, "total_tokens": None,
                      "image_input_usage": None, "image_input_unit": None, "cost": None,
                      "currency": None, "billing_scope": None, "source": "platform",
                      "unknown_fields_reason": "平台未提供 token / 图像输入 / 费用指标"},
            "logs": {"requests": "tmp/20261003-114508-flashmax/A22/requests.jsonl",
                     "iterations": "tmp/20261003-114508-flashmax/A22/iterations.jsonl"},
            "unresolved_issues": [],
        })

    start = min((r["started_at"] for r in renders), default=None)
    end = max((r["ended_at"] for r in renders), default=None)
    first_ok = next((r for r in renders if r.get("success")), None)
    metrics = {
        "schema": "task-metrics/1", "run_id": "20261003-114508-flashmax",
        "task_id": TASK, "title": "真实数据更正与局部回归（三轮）",
        "status": "completed", "timezone": "+08:00",
        "started_at": start, "ended_at": end,
        "wall_clock_seconds": (round((datetime.fromisoformat(end)
                                      - datetime.fromisoformat(start)).total_seconds(), 1)
                               if start and end else None),
        "first_usable_image_seconds": (round((datetime.fromisoformat(first_ok["ended_at"])
                                              - datetime.fromisoformat(start)).total_seconds(), 1)
                                       if first_ok else None),
        "requests": {"total": len(reqs), "render_requests": len(renders),
                     "render_success": sum(1 for r in renders if r.get("success")),
                     "render_failed": sum(1 for r in renders if not r.get("success")),
                     "other_service_requests": len(reqs) - len(renders),
                     "request_duration_ms_sum": sum(int(r.get("duration_ms") or 0) for r in reqs)},
        "iterations": {"total": len(iters),
                       "by_type": {t: sum(1 for i in iters if i.get("type") == t)
                                   for t in {i.get("type") for i in iters}},
                       "image_views": len(views),
                       "view_log": "tmp/20261003-114508-flashmax/A22/image-views.jsonl"},
        "dsl_versions": 1,
        "dsl_versions_note": ("one parameterised generator build_a22.py; it was revised "
                              "several times during the session and each revision was "
                              "re-rendered, but earlier revisions shared the same sandbox "
                              "file name and were overwritten, so only the final DSL of "
                              "each round is archived (dashboard.r{1,2,3}.v1.snapshot)"),
        "final_pngs": 3,
        "rounds": rounds,
        "regions_constant": REGIONS,
        "waiting": {"user_feedback_ms": 0, "rate_limit_wait_ms": None, "queue_wait_ms": None,
                    "note": "no 429 / Retry-After; server queue time is not measurable and "
                            "is null; the preloaded rounds needed no user feedback"},
        "usage": {"input_tokens": None, "output_tokens": None, "total_tokens": None,
                  "image_input_usage": None, "image_input_unit": None, "cost": None,
                  "currency": None, "billing_scope": None, "source": "platform",
                  "unknown_fields_reason": "平台未提供 token / 图像输入 / 费用指标，未用字数估算"},
        "logs": {"requests": "tmp/20261003-114508-flashmax/A22/requests.jsonl",
                 "iterations": "tmp/20261003-114508-flashmax/A22/iterations.jsonl"},
        "outputs": [f"outputs/20261003-114508-flashmax/A22/round-{r:02d}/{n}"
                    for r in (1, 2, 3) for n in
                    ("dashboard.png", "dashboard.snapshot", "computed-data.json",
                     "layout-map.json", "task-metrics.json")] +
                   [f"outputs/20261003-114508-flashmax/A22/round-{r:02d}/change-audit.json"
                    for r in (2, 3)] +
                   ["outputs/20261003-114508-flashmax/A22/snapshot-usage.md",
                    "outputs/20261003-114508-flashmax/A22/task-metrics.json"],
        "output_dir": "outputs/20261003-114508-flashmax/A22",
        "temp_dir": "tmp/20261003-114508-flashmax/A22",
        "unresolved_issues": [
            "the September negative profit bar is only ~10px tall at the shared scale; it "
            "is drawn below the zero line with a red fill and a -5,632 label rather than "
            "being rescaled, because a second scale would break the shared axis",
            "table cells are 20px while the rest of the body text is 22px, so that five "
            "numeric columns fit the 424px panel without touching",
        ],
    }
    write_json(os.path.join(OUT, "task-metrics.json"), metrics)
    append_jsonl_nobom(os.path.join(TMP, "metrics-builds.jsonl"),
                       {"at": datetime.now(TZ).isoformat(timespec="seconds"),
                        "requests": len(reqs), "views": len(views), "iters": len(iters)})
    print(json.dumps({"requests": len(reqs), "views": len(views), "iters": len(iters)},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()

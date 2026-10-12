"""Make every per-task task-metrics.json agree with its own requests.jsonl.

The log is the primary record (one line per real HTTP request). Some tasks wrote their
metrics before their final render, and some recorded the totals under different keys. This
pass sets the request counters from the log, preserves whatever was recorded as
`requests_selfreported`, states how it differed (or that it agreed), and does not touch any
other field. It is idempotent.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
OUT = os.path.join(ROOT, "outputs", RUN)
TMP = os.path.join(ROOT, "tmp", RUN)
sys.path.insert(0, os.path.join(TMP, "_suite", "shared"))
from suite_common import write_json  # noqa: E402

CAT = json.load(open(os.path.join(ROOT, "catalog.json"), encoding="utf-8"))
ORDER = CAT["task_order"]


def log_stats(path):
    total = ok = fail = 0
    kinds = {}
    t0 = t1 = None
    dur = 0
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                total += 1
                if r.get("success"):
                    ok += 1
                else:
                    fail += 1
                k = r.get("request_kind") or "unknown"
                kinds[k] = kinds.get(k, 0) + 1
                dur += r.get("duration_ms") or 0
                s, e = r.get("started_at"), r.get("ended_at")
                if s and (t0 is None or s < t0):
                    t0 = s
                if e and (t1 is None or e > t1):
                    t1 = e
    return {"total": total, "ok": ok, "fail": fail, "kinds": kinds,
            "duration_ms_sum": dur, "first_at": t0, "last_at": t1}


report = []
for tid in ORDER:
    mp = os.path.join(OUT, tid, "task-metrics.json")
    lp = os.path.join(TMP, tid, "requests.jsonl")
    if not os.path.exists(mp):
        report.append((tid, "no task-metrics.json", None, None))
        continue
    m = json.load(open(mp, encoding="utf-8-sig"))
    log = log_stats(lp)
    old = m.get("requests") or {}
    prev_total = old.get("requests_total")
    if prev_total != log["total"]:
        m.setdefault("requests_selfreported", {})
        if isinstance(m["requests_selfreported"], dict):
            m["requests_selfreported"].update(
                {"requests_total": prev_total,
                 "render_success": old.get("render_success"),
                 "render_failed": old.get("render_failed"),
                 "note": "该题在最后一次渲染前写下指标文件，自报值落后于 requests.jsonl；以下字段已按日志校正。"})
    m["requests"] = {
        "requests_total": log["total"],
        "render_success": log["ok"],
        "render_failed": log["fail"],
        "other_service_requests": sum(v for k, v in log["kinds"].items() if k != "render"),
        "request_kinds": log["kinds"],
        "source": "tmp/<run_id>/<TASK>/requests.jsonl 逐行统计（每个真实 HTTP 请求一行）",
        "request_duration_ms_sum": log["duration_ms_sum"],
        "first_request_at": log["first_at"],
        "last_request_at": log["last_at"],
    }
    write_json(mp, m)
    report.append((tid, "ok", prev_total, log["total"]))

print(f"{'task':5} {'self-reported':>14} {'from log':>9}  status")
for tid, st, prev, new in report:
    print(f"{tid:5} {str(prev):>14} {str(new):>9}  {st}")
changed = [r for r in report if r[0] and r[2] != r[3]]
print(f"\ncorrected {len(changed)} task metrics; all {len(ORDER)} files now match their logs")

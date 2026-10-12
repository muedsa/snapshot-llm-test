"""Shared suite bookkeeping helpers.

Writes per-task iterations.jsonl, tool-usage.jsonl and task-metrics.json, and keeps
the suite state / checkpoint files current. Import from per-task scripts.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TZ = timezone(timedelta(hours=8))
OUT_ROOT = os.path.join(ROOT, "outputs", RUN_ID)
TMP_ROOT = os.path.join(ROOT, "tmp", RUN_ID)
SUITE_OUT = os.path.join(OUT_ROOT, "_suite")
SUITE_TMP = os.path.join(TMP_ROOT, "_suite")


def now() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def task_out(task: str) -> str:
    p = os.path.join(OUT_ROOT, task)
    os.makedirs(p, exist_ok=True)
    return p


def task_tmp(task: str) -> str:
    p = os.path.join(TMP_ROOT, task)
    os.makedirs(p, exist_ok=True)
    return p


def append_jsonl(path: str, record: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def append_jsonl_nobom(path: str, record: dict) -> None:
    """Append without a BOM even if the file was created by PowerShell Set-Content."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        with open(path, "rb") as fh:
            head = fh.read(3)
        if head == b"\xef\xbb\xbf":
            with open(path, "rb") as fh:
                body = fh.read()
            with open(path, "wb") as fh:
                fh.write(body[3:])
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)


def read_jsonl(path: str) -> list:
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8-sig") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def count_requests(task: str) -> dict:
    """Aggregate tmp/<run>/<task>/requests.jsonl into the counter block used by metrics."""
    recs = read_jsonl(os.path.join(task_tmp(task), "requests.jsonl"))
    renders = [r for r in recs if r.get("request_kind") == "render"]
    return {
        "requests_total": len(recs),
        "render_requests": len(renders),
        "render_success": sum(1 for r in renders if r.get("success")),
        "render_failed": sum(1 for r in renders if not r.get("success")),
        "other_service_requests": len(recs) - len(renders),
        "request_duration_ms_sum": sum(int(r.get("duration_ms") or 0) for r in recs),
        "first_success_at": next((r["ended_at"] for r in renders if r.get("success")), None),
        "last_success_at": next((r["ended_at"] for r in reversed(renders) if r.get("success")), None),
    }


def count_iterations(task: str) -> dict:
    recs = read_jsonl(os.path.join(task_tmp(task), "iterations.jsonl"))
    by_type: dict = {}
    for r in recs:
        by_type[r.get("type", "unknown")] = by_type.get(r.get("type", "unknown"), 0) + 1
    return {
        "iterations_total": len(recs),
        "iterations_by_type": by_type,
        "visual_iterations": by_type.get("visual", 0),
        "image_reviews": sum(1 for r in recs if r.get("viewed_at")),
    }


def build_metrics(task: str, *, title: str, status: str, started_at: str, ended_at: str,
                  outputs: list, rounds: list | None = None, cases: list | None = None,
                  final_pngs: int = 0, notes: list | None = None,
                  dsl_versions: int = 0, extra: dict | None = None) -> dict:
    req = count_requests(task)
    it = count_iterations(task)
    tool_path = os.path.join(task_tmp(task), "tool-usage.jsonl")
    tools = read_jsonl(tool_path)
    t0 = datetime.fromisoformat(started_at)
    t1 = datetime.fromisoformat(ended_at)
    m = {
        "schema": "task-metrics/1",
        "run_id": RUN_ID,
        "task_id": task,
        "title": title,
        "status": status,
        "timezone": "+08:00",
        "started_at": started_at,
        "ended_at": ended_at,
        "wall_clock_seconds": round((t1 - t0).total_seconds(), 1),
        "requests": req,
        "iterations": it,
        "dsl_versions": dsl_versions,
        "final_pngs": final_pngs,
        "rounds": rounds or [],
        "cases": cases or [],
        "tool_invocations": len(tools),
        "tool_usage_file": os.path.relpath(tool_path, ROOT) if os.path.exists(tool_path) else None,
        "outputs": outputs,
        "output_dir": os.path.relpath(task_out(task), ROOT),
        "temp_dir": os.path.relpath(task_tmp(task), ROOT),
        "waiting": {
            "user_feedback_ms": 0,
            "rate_limit_wait_ms": None,
            "queue_wait_ms": None,
            "note": "429/Retry-After 未发生；服务端排队时间不可测，记 null；未等待用户反馈。",
        },
        "cost": {
            "tokens": None,
            "image_inputs": None,
            "money": None,
            "currency": None,
            "source": "平台未提供 token/图像/费用指标，按 AGENTS.md 记 null，不用字数估算。",
        },
        "notes": notes or [],
    }
    if extra:
        m.update(extra)
    return m

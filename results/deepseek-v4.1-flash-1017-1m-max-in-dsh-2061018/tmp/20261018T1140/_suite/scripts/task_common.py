"""Task bookkeeping helpers: logs, metrics, reports and final copies.

Run from the suite root with SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID set. Every
path written into a report is relative to the suite root (or output dir for
portfolio-style references); no machine-specific path is stored.
"""
from __future__ import annotations

import json
import os
import shutil
import time
from pathlib import Path


def root() -> Path:
    return Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()


def rid() -> str:
    value = os.environ.get("SNAPSHOT_RUN_ID")
    if not value:
        raise SystemExit("SNAPSHOT_RUN_ID is required")
    return value


def paths(task: str):
    r = root()
    return {
        "suite": r / "outputs" / rid() / "_suite",
        "out": r / "outputs" / rid() / task,
        "tmp": r / "tmp" / rid() / task,
    }


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def load(task: str):
    p = paths(task)
    return {
        "requests": _read_jsonl(p["tmp"] / "requests.jsonl"),
        "views": _read_jsonl(p["tmp"] / "views.jsonl"),
        "iterations": _read_jsonl(p["tmp"] / "iterations.jsonl"),
        "tool_usage": _read_jsonl(p["tmp"] / "tool-usage.jsonl"),
    }


def append(task: str, name: str, rec: dict) -> None:
    p = paths(task)
    p["tmp"].mkdir(parents=True, exist_ok=True)
    with (p["tmp"] / name).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def rel(path: Path) -> str:
    return path.resolve().relative_to(root()).as_posix()


def copy_final(task: str, src: Path, dst_name: str) -> Path:
    p = paths(task)
    p["out"].mkdir(parents=True, exist_ok=True)
    dst = p["out"] / dst_name
    dst.write_bytes(src.read_bytes())
    return dst


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def compute_metrics(task: str, started_at: str, ended_at: str, status: str = "completed",
                    dsl_versions: int | None = None, unfinished_notes: list[str] | None = None,
                    extra: dict | None = None) -> dict:
    p = paths(task)
    data = load(task)
    reqs = data["requests"]
    views = data["views"]
    iters = data["iterations"]
    ok = [r for r in reqs if r.get("http_status") == 200 and (r.get("content_type") or "").startswith("image/")]
    failed = [r for r in reqs if r not in ok]
    retries = [r for r in reqs if r.get("kind") == "retry"]
    first_ok = min((r["ts"] for r in ok), default=None)

    from datetime import datetime

    def parse(ts):
        return datetime.fromisoformat(ts)

    start = parse(started_at)
    end = parse(ended_at)
    first_seconds = None
    if first_ok:
        first_seconds = round((parse(first_ok) - start).total_seconds(), 1)
    dsl_names = {r.get("version") for r in reqs if r.get("version")}
    visual_done = [i for i in iters if i.get("type") == "visual" and i.get("completed")]
    visual_open = [i for i in iters if i.get("type") == "visual" and not i.get("completed")]

    metrics = {
        "schema_version": 1,
        "path_base": "suite_root",
        "task_id": task,
        "run_id": rid(),
        "task_round": None,
        "status": status,
        "stop_reason": None,
        "output_dir": f"outputs/{rid()}/{task}",
        "temp_dir": f"tmp/{rid()}/{task}",
        "timings": {
            "started_at": started_at,
            "ended_at": ended_at,
            "elapsed_seconds": round((end - start).total_seconds(), 1),
            "first_usable_image_seconds": first_seconds,
            "user_feedback_wait_seconds": 0,
            "rate_limit_wait_seconds": None,
            "queue_wait_seconds": None,
            "request_duration_sum_seconds": round(sum((r.get("duration_ms") or 0) for r in reqs) / 1000, 3),
            "server_timing_source": "X-Request-Id captured; Server-Timing header not present in recorded responses",
        },
        "counts": {
            "snapshot_requests": len(reqs),
            "successful_snapshot_requests": len(ok),
            "failed_snapshot_requests": len(failed),
            "retry_requests": len(retries),
            "other_service_requests": 0,
            "dsl_versions": dsl_versions if dsl_versions is not None else len(dsl_names),
            "image_views": len(views),
            "completed_visual_iterations": len(visual_done),
            "incomplete_visual_iterations": len(visual_open),
        },
        "logs": {
            "requests": f"tmp/{rid()}/{task}/requests.jsonl",
            "iterations": f"tmp/{rid()}/{task}/iterations.jsonl",
            "views": f"tmp/{rid()}/{task}/views.jsonl",
        },
        "outputs": [],
        "candidates": [],
        "rounds": [],
        "unresolved_issues": unfinished_notes or [],
    }
    if extra:
        metrics.update(extra)
    write_json(p["out"] / "task-metrics.json", metrics)
    return metrics


def fmt_ts(ts: str) -> str:
    from datetime import datetime
    return datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M:%S %z")


def request_rows(task: str) -> list[str]:
    rows = []
    for r in load(task)["requests"]:
        rows.append("| {id} | `{req}` | {ts} · {dur}s | {status} · `{ct}` | `{resp}` | {note} |".format(
            id=r.get("id"), req=r.get("request_file"), ts=fmt_ts(r["ts"]),
            dur=round((r.get("duration_ms") or 0) / 1000, 2), status=r.get("http_status"),
            ct=r.get("content_type"), resp=r.get("response_file"),
            note=("已查看" if r.get("http_status") == 200 else (r.get("error") or "失败")),
        ))
    return rows

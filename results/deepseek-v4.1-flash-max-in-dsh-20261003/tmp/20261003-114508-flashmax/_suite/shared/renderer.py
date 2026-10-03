"""Render helper used by the A21-A24 generators.

Talks to the live open-snapshot service directly (stdlib only) and appends one JSON
record per HTTP request to tmp/<run>/<task>/requests.jsonl, matching the schema that
render.ps1 used for A01-A08 so suite_common.count_requests keeps working.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from suite_common import ROOT, append_jsonl_nobom, task_tmp  # noqa: E402

BASE = "https://open-snapshot.muedea.com"  # placeholder, replaced below
BASE = "https://open-snapshot.muedsa.com"
TZ = timezone(timedelta(hours=8))


def _next_req_id(prefix: str) -> str:
    seq_file = os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "_suite", "shared",
                            f"reqseq-{prefix}.txt")
    n = 0
    if os.path.exists(seq_file):
        txt = open(seq_file, encoding="utf-8").read().strip()
        if txt.isdigit():
            n = int(txt)
    n += 1
    os.makedirs(os.path.dirname(seq_file), exist_ok=True)
    with open(seq_file, "w", encoding="utf-8") as fh:
        fh.write(str(n))
    return f"{prefix}-{n:04d}"


def render(jobs: list, task: str, manifest_name: str = "jobs") -> list:
    """jobs: list of dicts {dsl, out, task, prefix, round, case, phase} (paths vs ROOT)."""
    tmp = task_tmp(task)
    n = 1
    while os.path.exists(os.path.join(tmp, f"{manifest_name}-{n:03d}.json")):
        n += 1
    mpath = os.path.join(tmp, f"{manifest_name}-{n:03d}.json")
    with open(mpath, "w", encoding="utf-8") as fh:
        json.dump(jobs, fh, ensure_ascii=False, indent=2)

    log_path = os.path.join(tmp, "requests.jsonl")
    results = []
    for j in jobs:
        dsl_path = os.path.join(ROOT, j["dsl"])
        out_path = os.path.join(ROOT, j["out"])
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        data = open(dsl_path, "rb").read()
        req_id = _next_req_id(j.get("prefix", "REQ"))
        t0 = datetime.now(TZ)
        url = BASE + "/snapshot"
        if j.get("query"):
            url += "?" + j["query"]
        req = urllib.request.Request(url, data=data, method="POST",
                                     headers={"Content-Type": "text/plain; charset=utf-8",
                                              "User-Agent": "curl/8.4.0",
                                              "Accept": "*/*"})
        status = None
        ctype = None
        body = b""
        err = None
        ok = False
        sreq = None
        stim = None
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                status = resp.status
                ctype = resp.headers.get("Content-Type")
                sreq = resp.headers.get("X-Request-Id")
                stim = resp.headers.get("Server-Timing")
                body = resp.read()
            ok = status == 200 and len(body) > 0 and (ctype or "").startswith("image/")
        except urllib.error.HTTPError as e:
            status = e.code
            ctype = e.headers.get("Content-Type")
            sreq = e.headers.get("X-Request-Id")
            stim = e.headers.get("Server-Timing")
            body = e.read()
            err = body.decode("utf-8", "replace")[:2000]
        except Exception as e:  # network level failure
            err = f"{type(e).__name__}: {e}"
        t1 = datetime.now(TZ)
        out_full = None
        if ok:
            with open(out_path, "wb") as fh:
                fh.write(body)
            out_full = out_path
        else:
            with open(out_path + ".failed.txt", "wb") as fh:
                fh.write(body if body else (err or "").encode("utf-8"))
        append_jsonl_nobom(log_path, {
            "request_id": req_id, "run_id": "20261003-114508-flashmax", "task_id": task,
            "round": j.get("round"), "case_id": j.get("case"),
            "phase": j.get("phase", "render"), "request_kind": "render",
            "method": "POST", "url": "/snapshot", "query": j.get("query"),
            "started_at": t0.isoformat(timespec="milliseconds"),
            "ended_at": t1.isoformat(timespec="milliseconds"), "tz": "+08:00",
            "duration_ms": int((t1 - t0).total_seconds() * 1000),
            "http_status": status, "content_type": ctype,
            "request_file": dsl_path.replace("\\", "/"),
            "request_bytes": len(data),
            "response_file": (out_full or "").replace("\\", "/") if out_full else None,
            "response_bytes": len(body),
            "service_request_id": sreq, "server_timing": stim,
            "success": ok, "error": err,
        })
        results.append({"request_id": req_id, "dsl": j["dsl"], "out": j["out"],
                        "ok": ok, "status": status, "bytes": len(body),
                        "ms": int((t1 - t0).total_seconds() * 1000), "error": err})
    return results


def log_iteration(task: str, rec: dict) -> None:
    append_jsonl_nobom(os.path.join(task_tmp(task), "iterations.jsonl"), rec)


def log_tool(task: str, rec: dict) -> None:
    append_jsonl_nobom(os.path.join(task_tmp(task), "tool-usage.jsonl"), rec)

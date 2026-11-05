#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Equivalent /snapshot render client with a short connect/TLS timeout.

Workaround for intermittent `ssl handshake operation timed out` stalls in this
environment: the shared render.py uses urlopen(timeout=180), so one stalled
handshake costs 180s per attempt. This client uses a 30s timeout and retries
quickly. It writes the SAME requests.jsonl schema (so suite.summarize_requests
works), saves raw request/response bytes, and only accepts 200 + image/* as
success. All successful PNGs are genuine open-snapshot responses.
"""
import argparse
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = os.environ.get("SNAPSHOT_BASE_URL", "https://open-snapshot.muedsa.com").rstrip("/")


def now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def rel(path, root):
    try:
        return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return os.path.basename(str(path))


def post(dsl_bytes, req_id, timeout):
    req = urllib.request.Request(
        BASE_URL + "/snapshot", data=dsl_bytes,
        headers={"Content-Type": "text/plain; charset=utf-8", "X-Request-Id": req_id},
        method="POST")
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"status": resp.status, "headers": dict(resp.headers.items()),
                    "body": resp.read(),
                    "duration_ms": round((time.monotonic() - t0) * 1000, 1),
                    "started_at": now(), "ended_at": now()}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "headers": dict(e.headers.items()) if e.headers else {},
                "body": e.read(), "duration_ms": round((time.monotonic() - t0) * 1000, 1),
                "started_at": now(), "ended_at": now()}
    except Exception as e:
        return {"status": 0, "headers": {}, "body": str(e).encode("utf-8"),
                "duration_ms": round((time.monotonic() - t0) * 1000, 1),
                "started_at": now(), "ended_at": now(), "transport_error": repr(e)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsl", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--task", required=True)
    ap.add_argument("--label", default="final")
    ap.add_argument("--logdir", required=True)
    ap.add_argument("--suite-root", default=os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--timeout", type=float, default=30.0)
    args = ap.parse_args()

    root = str(Path(args.suite_root).resolve())
    logdir = Path(args.logdir).resolve()
    (logdir / "requests").mkdir(parents=True, exist_ok=True)
    (logdir / "responses").mkdir(parents=True, exist_ok=True)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    dsl_bytes = Path(args.dsl).read_bytes()

    rec = {"task_id": args.task, "label": args.label,
           "request_type": "snapshot_render", "path_base": "suite_root",
           "dsl_file": rel(args.dsl, root), "out_file": rel(args.out, root),
           "dsl_bytes": len(dsl_bytes)}
    attempts = []
    for attempt in range(args.retries + 1):
        rid = "%s-%s-%03d-%d-fast" % (args.task, args.label.replace("/", "-"),
                                      int(time.time() * 1000) % 100000, attempt)
        res = post(dsl_bytes, rid, args.timeout)
        (logdir / "requests" / (rid + ".snapshot")).write_bytes(dsl_bytes)
        (logdir / "responses" / (rid + ".bin")).write_bytes(res["body"])
        ct = res["headers"].get("Content-Type", res["headers"].get("content-type", ""))
        a = {
            "request_id": rid, "attempt": attempt,
            "started_at": res["started_at"], "ended_at": res["ended_at"],
            "duration_ms": res["duration_ms"], "http_status": res["status"],
            "content_type": ct,
            "request_file": rel(str(logdir / "requests" / (rid + ".snapshot")), root),
            "response_file": rel(str(logdir / "responses" / (rid + ".bin")), root),
            "x_request_id": res["headers"].get("X-Request-Id") or res["headers"].get("x-request-id"),
            "server_timing": res["headers"].get("Server-Timing") or res["headers"].get("server-timing"),
            "retry_after": res["headers"].get("Retry-After") or res["headers"].get("retry-after"),
            "transport_error": res.get("transport_error"),
        }
        ok = res["status"] == 200 and ct.lower().startswith("image/")
        a["success"] = ok
        if not ok:
            a["error_summary"] = res["body"][:600].decode("utf-8", "replace")
        attempts.append(a)
        if ok:
            Path(args.out).write_bytes(res["body"])
            break
        time.sleep(1.0)
    rec["attempts"] = attempts
    rec["final_success"] = bool(attempts and attempts[-1]["success"])
    rec["total_request_ms"] = round(sum(a["duration_ms"] for a in attempts), 1)
    rec["log_time"] = now()
    rec["client"] = "fast_render.py (short TLS timeout workaround)"
    with (logdir / "requests.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    shared = Path(root) / "tmp" / os.environ.get("SNAPSHOT_RUN_ID", "") / "_suite" / "requests.jsonl"
    if shared.parent.exists():
        with shared.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(json.dumps({"label": args.label, "ok": rec["final_success"],
                      "attempts": len(attempts),
                      "bytes": len(Path(args.out).read_bytes()) if rec["final_success"] else 0,
                      "request_id": attempts[-1]["request_id"],
                      "error": None if rec["final_success"] else attempts[-1].get("error_summary")},
                     ensure_ascii=False))
    sys.exit(0 if rec["final_success"] else 2)


if __name__ == "__main__":
    main()

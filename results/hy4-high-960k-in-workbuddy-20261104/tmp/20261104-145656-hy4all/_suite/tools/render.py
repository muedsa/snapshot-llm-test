#!/usr/bin/env python3
"""Shared Open Snapshot render client.

Paths are resolved from SNAPSHOT_TASK_ROOT (default: current working directory)
and SNAPSHOT_RUN_ID; no machine-specific absolute path is stored in any record.
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


def rel(path, suite_root):
    try:
        return Path(path).resolve().relative_to(Path(suite_root).resolve()).as_posix()
    except ValueError:
        return os.path.basename(str(path))


def post_once(dsl_bytes, req_id):
    req = urllib.request.Request(
        BASE_URL + "/snapshot",
        data=dsl_bytes,
        headers={
            "Content-Type": "text/plain; charset=utf-8",
            "X-Request-Id": req_id,
        },
        method="POST",
    )
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            body = resp.read()
            return {
                "status": resp.status,
                "headers": dict(resp.headers.items()),
                "body": body,
                "duration_ms": round((time.monotonic() - t0) * 1000, 1),
                "started_at": now(),
                "ended_at": now(),
            }
    except urllib.error.HTTPError as e:
        return {
            "status": e.code,
            "headers": dict(e.headers.items()) if e.headers else {},
            "body": e.read(),
            "duration_ms": round((time.monotonic() - t0) * 1000, 1),
            "started_at": now(),
            "ended_at": now(),
        }
    except Exception as e:
        return {
            "status": 0,
            "headers": {},
            "body": str(e).encode("utf-8"),
            "duration_ms": round((time.monotonic() - t0) * 1000, 1),
            "started_at": now(),
            "ended_at": now(),
            "transport_error": repr(e),
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsl", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--task", required=True)
    ap.add_argument("--label", default="render")
    ap.add_argument("--logdir", required=True)
    ap.add_argument("--suite-root", default=os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    ap.add_argument("--retries", type=int, default=1)
    args = ap.parse_args()

    suite_root = str(Path(args.suite_root).resolve())
    logdir = Path(args.logdir).resolve()
    logdir.mkdir(parents=True, exist_ok=True)
    (logdir / "requests").mkdir(exist_ok=True)
    (logdir / "responses").mkdir(exist_ok=True)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    dsl_bytes = Path(args.dsl).read_bytes()
    rec = {
        "task_id": args.task,
        "label": args.label,
        "request_type": "snapshot_render",
        "path_base": "suite_root",
        "dsl_file": rel(args.dsl, suite_root),
        "out_file": rel(args.out, suite_root),
        "dsl_bytes": len(dsl_bytes),
    }
    attempts = []
    for attempt in range(args.retries + 1):
        rid = "%s-%s-%03d-%d" % (
            args.task,
            args.label.replace("/", "-"),
            int(time.time() * 1000) % 100000,
            attempt,
        )
        res = post_once(dsl_bytes, rid)
        req_copy = logdir / "requests" / (rid + ".snapshot")
        req_copy.write_bytes(dsl_bytes)
        resp_copy = logdir / "responses" / (rid + ".bin")
        resp_copy.write_bytes(res["body"])
        ct = res["headers"].get("Content-Type", res["headers"].get("content-type", ""))
        a = {
            "request_id": rid,
            "attempt": attempt,
            "started_at": res["started_at"],
            "ended_at": res["ended_at"],
            "duration_ms": res["duration_ms"],
            "http_status": res["status"],
            "content_type": ct,
            "request_file": rel(str(req_copy), suite_root),
            "response_file": rel(str(resp_copy), suite_root),
            "x_request_id": res["headers"].get("X-Request-Id") or res["headers"].get("x-request-id"),
            "server_timing": res["headers"].get("Server-Timing") or res["headers"].get("server-timing"),
            "retry_after": res["headers"].get("Retry-After") or res["headers"].get("retry-after"),
            "transport_error": res.get("transport_error"),
        }
        ok = res["status"] == 200 and ct.lower().startswith("image/")
        a["success"] = ok
        if not ok:
            try:
                a["error_summary"] = res["body"][:1200].decode("utf-8", "replace")
            except Exception:
                a["error_summary"] = repr(res["body"][:200])
        attempts.append(a)
        if ok:
            Path(args.out).write_bytes(res["body"])
            break
        if res["status"] in (429, 503, 0) and attempt < args.retries:
            try:
                delay = min(float(a["retry_after"] or 2), 30)
            except ValueError:
                delay = 2
            time.sleep(max(delay, 1))
        else:
            break

    rec["attempts"] = attempts
    rec["final_success"] = bool(attempts and attempts[-1]["success"])
    rec["total_request_ms"] = round(sum(a["duration_ms"] for a in attempts), 1)
    rec["log_time"] = now()
    with (logdir / "requests.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    # shared aggregate log
    shared = Path(suite_root) / "tmp" / os.environ.get("SNAPSHOT_RUN_ID", "") / "_suite" / "requests.jsonl"
    if shared.parent.exists():
        with shared.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(json.dumps({
        "label": args.label,
        "ok": rec["final_success"],
        "status": attempts[-1]["http_status"] if attempts else None,
        "content_type": attempts[-1]["content_type"] if attempts else None,
        "bytes": len(Path(args.out).read_bytes()) if rec["final_success"] else 0,
        "request_id": attempts[-1]["request_id"] if attempts else None,
        "error": None if rec["final_success"] else attempts[-1].get("error_summary"),
    }, ensure_ascii=False))
    sys.exit(0 if rec["final_success"] else 2)


if __name__ == "__main__":
    main()

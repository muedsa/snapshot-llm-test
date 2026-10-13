"""GET a documentation/service resource, save the raw response, log the request.

Run from the suite task root (or set SNAPSHOT_TASK_ROOT).

  python tmp/<run_id>/_suite/scripts/fetch.py \
      --url https://snapshot.muedsa.com/guides/layout/ \
      --save tmp/<run_id>/_suite/docs/guides_layout.html \
      --log tmp/<run_id>/_suite/requests.jsonl \
      --req-id SHARED-doc-010 --task SHARED --kind document
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()


def rel(p: Path) -> str:
    try:
        return Path(p).resolve().relative_to(ROOT).as_posix()
    except (ValueError, OSError):
        return Path(p).as_posix()


def abs_path(p: str) -> Path:
    q = Path(p)
    return q if q.is_absolute() else ROOT / q


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="milliseconds")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--save", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--req-id", required=True)
    ap.add_argument("--task", required=True)
    ap.add_argument("--kind", default="document")
    ap.add_argument("--timeout", type=float, default=60.0)
    a = ap.parse_args()

    parts = urlsplit(a.url)
    safe_url = urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))

    req = urllib.request.Request(safe_url, method="GET")
    req.add_header("User-Agent", os.environ.get("SNAPSHOT_USER_AGENT", "curl/8.7.1"))
    key = os.environ.get("SNAPSHOT_API_KEY")
    if key:
        req.add_header("X-API-Key", key)

    started_iso, started = now_iso(), time.monotonic()
    status = ctype = None
    headers: dict[str, str] = {}
    body = b""
    err = None
    try:
        with urllib.request.urlopen(req, timeout=a.timeout) as resp:
            status = resp.status
            headers = {k.lower(): v for k, v in resp.getheaders()}
            ctype = headers.get("content-type")
            body = resp.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        headers = {k.lower(): v for k, v in (exc.headers.items() if exc.headers else [])}
        ctype = headers.get("content-type")
        body = exc.read()
        err = body[:300].decode("utf-8", "replace")
    except Exception as exc:
        err = f"{type(exc).__name__}: {exc}"
    elapsed = round(time.monotonic() - started, 3)

    dst = abs_path(a.save)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if body:
        dst.write_bytes(body)

    rec = {
        "request_id": a.req_id,
        "task_id": a.task,
        "kind": a.kind,
        "request_type": "document" if a.kind == "document" else "service_get",
        "method": "GET",
        "url": safe_url,
        "started_at": started_iso,
        "ended_at": now_iso(),
        "timezone": datetime.now(timezone.utc).astimezone().tzname(),
        "duration_seconds": elapsed,
        "http_status": status,
        "response_content_type": ctype,
        "response_file": rel(dst) if body else None,
        "response_bytes": len(body),
        "x_request_id": headers.get("x-request-id"),
        "server_timing": headers.get("server-timing"),
        "ratelimit_remaining": headers.get("x-ratelimit-remaining"),
        "error_summary": err,
        "path_base": "suite_root",
    }
    logf = abs_path(a.log)
    logf.parent.mkdir(parents=True, exist_ok=True)
    with logf.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(json.dumps({k: rec[k] for k in ("request_id", "http_status", "response_bytes", "response_file")}, ensure_ascii=False))
    return 0 if status and status < 400 else 1


if __name__ == "__main__":
    sys.exit(main())

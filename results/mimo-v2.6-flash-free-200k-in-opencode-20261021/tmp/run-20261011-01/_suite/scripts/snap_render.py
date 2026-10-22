#!/usr/bin/env python3
"""Snapshot render helper.

Launch base: suite root (the directory that contains run-config.json).
All stored paths are relative to the suite root (path_base=suite_root).

Usage:
  python tmp/<run_id>/_suite/scripts/snap_render.py \
      --dsl outputs/<run_id>/A01/x.snapshot \
      --out outputs/<run_id>/A01/x.png \
      --log tmp/<run_id>/A01/requests.jsonl \
      --rid A01-req-0001

The service base URL comes from run-config.json (suite root), or SNAPSHOT_URL.
No API key is written into any file.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

SUITE_ROOT = pathlib.Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()


def load_base_url() -> str:
    env = os.environ.get("SNAPSHOT_URL")
    if env:
        return env.rstrip("/")
    cfg = SUITE_ROOT / "run-config.json"
    with cfg.open("r", encoding="utf-8") as fh:
        return json.load(fh)["service_base_url"].rstrip("/")


def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).astimezone().isoformat(timespec="milliseconds")


def rel(path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(SUITE_ROOT).as_posix()
    except Exception:
        return path.as_posix()


def post(base: str, dsl_bytes: bytes, api_key: str | None):
    req = urllib.request.Request(
        base + "/snapshot",
        data=dsl_bytes,
        method="POST",
        headers={
            "Content-Type": "text/plain; charset=utf-8",
            "User-Agent": os.environ.get(
                "SNAPSHOT_UA", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            ),
            "Accept": "image/png,image/*;q=0.8,*/*;q=0.5",
        },
    )
    if api_key:
        req.add_header("X-API-Key", api_key)
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            body = resp.read()
            elapsed = time.perf_counter() - started
            return resp.status, dict(resp.headers), body, elapsed, None
    except urllib.error.HTTPError as exc:
        body = exc.read()
        elapsed = time.perf_counter() - started
        return exc.code, dict(exc.headers or {}), body, elapsed, str(exc)
    except Exception as exc:  # noqa: BLE001 - recorded as evidence
        elapsed = time.perf_counter() - started
        return 0, {}, b"", elapsed, repr(exc)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsl", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--log", required=True, help="requests.jsonl for this task")
    ap.add_argument("--rid", required=True, help="unique request id, e.g. A01-req-0001")
    ap.add_argument("--err-out", default=None, help="where to save a failed response body")
    ap.add_argument("--max-attempts", type=int, default=4)
    args = ap.parse_args()

    dsl_path = pathlib.Path(args.dsl)
    out_path = pathlib.Path(args.out)
    log_path = pathlib.Path(args.log)
    base = load_base_url()
    api_key = os.environ.get("SNAPSHOT_API_KEY")

    dsl_bytes = dsl_path.read_bytes()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    attempt = 0
    status, headers, body, elapsed, err = (0, {}, b"", 0.0, None)
    while attempt < args.max_attempts:
        attempt += 1
        status, headers, body, elapsed, err = post(base, dsl_bytes, api_key)
        if status == 200:
            break
        if status in (429, 503) and attempt < args.max_attempts:
            retry_after = headers.get("Retry-After") or headers.get("retry-after")
            try:
                delay = float(retry_after)
            except (TypeError, ValueError):
                delay = 2.0 * attempt
            delay = min(max(delay, 1.0), 60.0)
            time.sleep(delay)
            continue
        break

    ok = status == 200
    ctype = headers.get("Content-Type") or headers.get("content-type") or ""
    saved = False
    if ok and body:
        out_path.write_bytes(body)
        saved = True
    else:
        err_path = pathlib.Path(args.err_out) if args.err_out else out_path.with_suffix(out_path.suffix + ".error.json")
        err_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            err_path.write_bytes(body)
        except Exception:
            pass

    record = {
        "id": args.rid,
        "ts": now_iso(),
        "method": "POST",
        "url": base + "/snapshot",
        "dsl_path": rel(dsl_path),
        "dsl_bytes": len(dsl_bytes),
        "out_path": rel(out_path) if saved else None,
        "response_bytes": len(body),
        "content_type": ctype,
        "status": status,
        "ok": ok,
        "attempts": attempt,
        "elapsed_seconds": round(elapsed, 3),
        "retry_after_used": attempt > 1,
        "error": err if not ok else None,
    }
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    if not ok:
        sys.stderr.write(json.dumps(record, ensure_ascii=False) + "\n")
        try:
            sys.stderr.write(body.decode("utf-8", "replace") + "\n")
        except Exception:
            pass
        return 1
    print(json.dumps(record, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

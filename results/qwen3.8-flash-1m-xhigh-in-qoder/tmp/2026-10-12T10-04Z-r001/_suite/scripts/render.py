"""Render a Snapshot DSL file through the open-snapshot service and log the request.

Run from the suite task root (or set SNAPSHOT_TASK_ROOT to it).

    python tmp/<run_id>/_suite/scripts/render.py \
        --dsl tmp/<run_id>/A01/v001.snapshot \
        --out outputs/<run_id>/A01/operations.png \
        --log tmp/<run_id>/A01/requests.jsonl \
        --req-id A01-render-001 --task A01 --kind render

Paths in arguments and in the written log are relative to the suite task root.
The service base URL comes from SNAPSHOT_SERVICE_URL, else run-config.json.
Credentials, if any, are read from SNAPSHOT_API_KEY and never written to disk.
"""
from __future__ import annotations

import argparse
import json
import os
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def suite_root() -> Path:
    return Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()


ROOT = suite_root()


def rel(p: Path | None) -> str | None:
    """Convert a runtime path back to the declared suite_root base for records."""
    if p is None:
        return None
    try:
        return Path(p).resolve().relative_to(ROOT).as_posix()
    except (ValueError, OSError):
        return Path(p).as_posix()


def abs_path(p: str) -> Path:
    q = Path(p)
    return q if q.is_absolute() else ROOT / q


def service_base() -> str:
    url = os.environ.get("SNAPSHOT_SERVICE_URL")
    if url:
        return url.rstrip("/")
    cfg = json.loads((ROOT / "run-config.json").read_text(encoding="utf-8"))
    return cfg["service_base_url"].rstrip("/")


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="milliseconds")


def png_size(data: bytes) -> tuple[int | None, int | None, str]:
    if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) >= 24:
        w, h = struct.unpack(">II", data[16:24])
        return w, h, "png"
    if data[:3] == b"\xff\xd8\xff":
        return None, None, "jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return None, None, "webp"
    return None, None, "unknown"


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def post_via_curl(dsl_file: Path, url: str, hdr_file: Path, body_file: Path,
                  timeout: float) -> tuple[int | None, dict[str, str], bytes, str | None]:
    """Transfer via curl: the edge intermittently returns 200 headers for a urllib
    POST and then never streams the body, while curl completes the same DSL in ~2s."""
    cmd = ["curl", "-sS", "--fail-with-body", "--http1.1", "-D", str(hdr_file),
           "-X", "POST", url,
           "-H", "Content-Type: text/plain; charset=utf-8",
           "--max-time", str(int(max(timeout, 10))),
           "--retry", "2", "--retry-delay", "3",
           "--data-binary", f"@{dsl_file}", "-o", str(body_file)]
    key = os.environ.get("SNAPSHOT_API_KEY")
    if key:
        cmd[4:4] = ["-H", f"X-API-Key: {key}"]
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 15)
    except subprocess.TimeoutExpired:
        return None, {}, b"", "curl: timed out"
    err = (cp.stderr or "").strip() or None
    headers: dict[str, str] = {}
    status: int | None = None
    if hdr_file.exists():
        for line in hdr_file.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.upper().startswith("HTTP/"):
                parts = line.split()
                if len(parts) > 1 and parts[1].isdigit():
                    status = int(parts[1])
            elif ": " in line:
                k, _, v = line.partition(":")
                headers[k.strip().lower()] = v.strip()
    body = body_file.read_bytes() if body_file.exists() else b""
    if cp.returncode != 0 and not body:
        err = f"curl exit {cp.returncode}: {err}" if err else f"curl exit {cp.returncode}"
    return status, headers, body, err


def render(args) -> int:
    dsl_file = abs_path(args.dsl)
    out_file = abs_path(args.out)
    log_file = abs_path(args.log)
    dsl_bytes = dsl_file.read_bytes()

    url = f"{service_base()}{args.endpoint}"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    tmpdir = out_file.parent
    hdr_file = tmpdir / f"{args.req_id}.hdr"

    started = time.monotonic()
    started_iso = now_iso()
    status, headers, body, network_error = post_via_curl(
        dsl_file, url, hdr_file, out_file, args.timeout)
    ctype = headers.get("content-type")
    err_summary: str | None = None
    if status and status != 200 and body:
        try:
            err_summary = json.loads(body.decode("utf-8", "replace")).get("message")
        except Exception:
            err_summary = body[:400].decode("utf-8", "replace").strip() or None
    if network_error and not err_summary:
        err_summary = network_error

    elapsed = round(time.monotonic() - started, 3)
    ended_iso = now_iso()

    w, h, fmt = png_size(body)
    is_image = status == 200 and fmt != "unknown"

    out_file.parent.mkdir(parents=True, exist_ok=True)

    if is_image:
        # curl already wrote the service's raw response bytes to out_file untouched.
        resp_saved = rel(out_file)
    elif body:
        raw = abs_path(args.raw_error_dir) if args.raw_error_dir else log_file.parent
        err_file = raw / f"{args.req_id}.resp"
        err_file.parent.mkdir(parents=True, exist_ok=True)
        err_file.write_bytes(body)
        resp_saved = rel(err_file)
        # never leave a JSON error body sitting at a .png path
        if out_file.exists():
            out_file.unlink()
    else:
        resp_saved = None
        if out_file.exists():
            out_file.unlink()

    timing = headers.get("server-timing")
    record = {
        "request_id": args.req_id,
        "task_id": args.task,
        "case_id": args.case,
        "round": args.round,
        "kind": args.kind,
        "request_type": "render",
        "method": "POST",
        "url_path": args.endpoint,
        "service_base": service_base(),
        "started_at": started_iso,
        "ended_at": ended_iso,
        "timezone": datetime.now(timezone.utc).astimezone().tzname(),
        "duration_seconds": elapsed,
        "http_status": status,
        "response_content_type": ctype,
        "request_file": rel(dsl_file),
        "request_bytes": len(dsl_bytes),
        "response_file": resp_saved,
        "response_bytes": len(body) if body else 0,
        "image_format": fmt if body else None,
        "image_width": w,
        "image_height": h,
        "x_request_id": headers.get("x-request-id"),
        "server_timing": timing,
        "x_snapshot_cache": headers.get("x-snapshot-cache"),
        "x_snapshot_image_count": headers.get("x-snapshot-image-count"),
        "retry_after": headers.get("retry-after"),
        "error_code": None,
        "error_summary": err_summary or network_error,
        "path_base": "suite_root",
    }
    if status and status != 200:
        try:
            record["error_code"] = json.loads(body.decode("utf-8", "replace")).get("code")
        except Exception:
            record["error_code"] = None

    append_jsonl(log_file, record)

    summary = {
        "request_id": args.req_id,
        "http_status": status,
        "ok": is_image,
        "format": fmt,
        "width": w,
        "height": h,
        "bytes": len(body),
        "duration_seconds": elapsed,
        "cache": record["x_snapshot_cache"],
        "server_timing": timing,
        "x_request_id": record["x_request_id"],
        "error_code": record["error_code"],
        "error_summary": record["error_summary"],
        "response_file": resp_saved,
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if is_image else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsl", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--req-id", required=True)
    ap.add_argument("--task", required=True)
    ap.add_argument("--case", default=None)
    ap.add_argument("--round", default=None)
    ap.add_argument("--kind", default="render")
    ap.add_argument("--endpoint", default="/snapshot")
    ap.add_argument("--raw-error-dir", default=None)
    ap.add_argument("--timeout", type=float, default=90.0)
    return render(ap.parse_args())


if __name__ == "__main__":
    sys.exit(main())

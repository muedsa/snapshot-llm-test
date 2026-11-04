# -*- coding: utf-8 -*-
"""Shared Snapshot service client used by every task in this suite.

Script base: suite_root (directory containing run-config.json).
Placement: tmp/<run_id>/_suite/scripts/snapshot_api.py  (shared, not a task artifact)

Records requests.jsonl inside the *task temp dir*:
    <TEMP_DIR>/requests.jsonl

All persisted paths are relative to the suite root (`path_base: "suite_root"`).
The service URL is read from SNAPSHOT_SERVICE_URL or the suite run-config.
"""
from __future__ import annotations

import json
import os
import time
import hashlib
import datetime
import urllib.error
import urllib.request
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")


def iso_now() -> str:
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def load_service_url() -> str:
    env = os.environ.get("SNAPSHOT_SERVICE_URL")
    if env:
        return env.rstrip("/")
    cfg = json.loads((SUITE_ROOT / "run-config.json").read_text(encoding="utf-8"))
    return str(cfg["service_base_url"]).rstrip("/")


SERVICE_URL = load_service_url()


def rel(path: Path) -> str:
    """Path relative to the suite root, POSIX separators."""
    try:
        return path.resolve().relative_to(SUITE_ROOT).as_posix()
    except ValueError:
        return path.name


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _curl_call(method: str, url: str, body: bytes | None, out_path: Path,
               headers: dict, timeout: int) -> tuple[int | None, dict, bytes, str | None]:
    """One HTTP call through curl.exe.

    curl is used instead of urllib because the deployment's chunked responses
    stalled urllib's reader on larger images; curl streams them reliably.
    """
    import subprocess
    import tempfile

    out_path.parent.mkdir(parents=True, exist_ok=True)
    hdr_file = out_path.with_suffix(out_path.suffix + ".headers.txt")
    body_file = None
    cmd = ["curl.exe", "-sS", "-X", method, url, "-o", str(out_path),
           "-D", str(hdr_file), "--max-time", str(timeout),
           "-w", "%{http_code} %{content_type} %{size_download}"]
    for k, v in headers.items():
        cmd += ["-H", f"{k}: {v}"]
    if body is not None:
        fd, tmp_name = tempfile.mkstemp(suffix=".body", dir=str(out_path.parent))
        os.close(fd)
        body_file = Path(tmp_name)
        body_file.write_bytes(body)
        cmd += ["--data-binary", f"@{body_file}"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 30)
        meta = (proc.stdout or "").strip().split(" ")
        status = int(meta[0]) if meta and meta[0].isdigit() else None
        ctype = meta[1] if len(meta) > 1 else ""
        hdrs: dict[str, str] = {}
        if hdr_file.exists():
            for line in hdr_file.read_text(encoding="utf-8", errors="replace").splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    hdrs[k.strip().lower()] = v.strip()
        if ctype and "content-type" not in hdrs:
            hdrs["content-type"] = ctype
        raw = out_path.read_bytes() if out_path.exists() else b""
        err = None
        if proc.returncode != 0:
            err = f"curl exit {proc.returncode}: {(proc.stderr or '').strip()[:200]}"
        elif status is None:
            err = f"no status: {(proc.stderr or '').strip()[:200]}"
        return status, hdrs, raw, err
    except Exception as exc:  # noqa: BLE001
        return None, {}, b"", f"{type(exc).__name__}: {exc}"
    finally:
        if body_file and body_file.exists():
            body_file.unlink()
        if hdr_file.exists():
            hdr_file.unlink()


def http_call(
    method: str,
    url: str,
    body: bytes | None,
    out_path: Path,
    headers: dict | None = None,
    timeout: int = 180,
    retries: int = 6,
) -> dict:
    """Perform one HTTP call. Returns dict with status/headers/body/path.

    On 429 / 503 with Retry-After the call is retried, and each attempt is a
    distinct record so the request log keeps the true attempt count.
    """
    attempts = []
    delay = 0.0
    last = None
    for attempt in range(1, retries + 1):
        if delay:
            time.sleep(delay)
            delay = 0.0
        started = time.time()
        req_headers = {
            "User-Agent": "snapshot-suite-runner/1.0",
            "Accept": "*/*",
        }
        if headers:
            req_headers.update(headers)
        status, hdrs, raw, err = _curl_call(method, url, body, out_path, req_headers, timeout)
        elapsed = round(time.time() - started, 3)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(raw)
        record = {
            "attempt": attempt,
            "status": status,
            "content_type": hdrs.get("content-type"),
            "bytes": len(raw),
            "elapsed_s": elapsed,
            "error": err,
            "response_file": rel(out_path),
            "server_timing": hdrs.get("server-timing"),
            "request_id": hdrs.get("x-request-id"),
            "rate_limit_remaining": hdrs.get("x-ratelimit-remaining"),
            "retry_after": hdrs.get("retry-after"),
        }
        attempts.append(record)
        last = record
        if status == 200:
            break
        retryable = status in (0, 429, 500, 502, 503, 504) or status is None
        if not retryable or attempt == retries:
            break
        try:
            delay = float(hdrs.get("retry-after") or 0)
        except ValueError:
            delay = 0.0
        if delay <= 0:
            delay = min(2.0 * attempt, 20.0)
    result = dict(last)
    result["attempts"] = attempts
    return result


class TaskLogger:
    """Per-task request/iteration logging."""

    def __init__(self, task_id: str, temp_dir: Path | None = None):
        self.task_id = task_id
        self.temp_dir = temp_dir or (SUITE_ROOT / "tmp" / RUN_ID / task_id)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.requests_path = self.temp_dir / "requests.jsonl"
        self.iterations_path = self.temp_dir / "iterations.jsonl"
        self.tool_usage_path = self.temp_dir / "tool-usage.jsonl"
        self.seq = self._next_seq()

    def _next_seq(self) -> int:
        n = 0
        if self.requests_path.exists():
            for line in self.requests_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    n += 1
        return n

    def render(
        self,
        dsl_path: Path,
        png_path: Path,
        tag: str,
        round_id: str | None = None,
    ) -> dict:
        """Render a DSL file through the real service and store raw PNG bytes."""
        dsl_text = dsl_path.read_text(encoding="utf-8")
        body = dsl_text.encode("utf-8")
        self.seq += 1
        req_id = f"{self.task_id}-{round_id + '-' if round_id else ''}R{self.seq:04d}"
        raw_response = self.temp_dir / "responses" / f"{req_id}.bin"
        url = f"{SERVICE_URL}/snapshot"
        started_at = iso_now()
        t0 = time.time()
        res = http_call(
            "POST", url, body, raw_response,
            headers={
                "Content-Type": "text/plain; charset=utf-8",
                "X-Request-Id": req_id,
            },
        )
        wall = round(time.time() - t0, 3)
        ok = (res["status"] == 200 and (res["content_type"] or "").startswith("image/")
              and res["bytes"] > 0)
        # the deployment occasionally drops the tail of larger bodies: verify PNG completeness
        _raw = raw_response.read_bytes() if raw_response.exists() else b""
        if ok and _raw[:8] == b"\x89PNG\r\n\x1a\n" and b"IEND" not in _raw[-32:]:
            retry = http_call(
                "POST", url, body, raw_response,
                headers={"Content-Type": "text/plain; charset=utf-8",
                         "X-Request-Id": req_id + "r"},
                timeout=240,
            )
            attempts = res.get("attempts", []) + retry.get("attempts", [])
            res = dict(retry)
            res["attempts"] = attempts
            res["error"] = (res.get("error") or "") + " | first transfer truncated, retried"
            wall = round(time.time() - t0, 3)
            ok = (res["status"] == 200 and (res["content_type"] or "").startswith("image/")
                  and res["bytes"] > 0)
        if ok:
            png_path.parent.mkdir(parents=True, exist_ok=True)
            png_path.write_bytes(raw_response.read_bytes())
        record = {
            "id": req_id,
            "task_id": self.task_id,
            "round": round_id,
            "kind": "render",
            "tag": tag,
            "method": "POST",
            "url_path": "/snapshot",
            "started_at": started_at,
            "ended_at": iso_now(),
            "timezone": "Asia/Shanghai",
            "elapsed_s": wall,
            "service_elapsed_s": res["elapsed_s"],
            "request_bytes": len(body),
            "http_status": res["status"],
            "content_type": res["content_type"],
            "response_bytes": res["bytes"],
            "request_file": rel(dsl_path),
            "response_file": rel(raw_response),
            "png_written": rel(png_path) if ok else None,
            "error": res["error"],
            "request_id_header": res["request_id"],
            "server_timing": res["server_timing"],
            "rate_limit_remaining": res["rate_limit_remaining"],
            "retry_after": res["retry_after"],
            "attempt_count": len(res["attempts"]),
            "path_base": "suite_root",
        }
        append_jsonl(self.requests_path, record)
        return record

    def service_get(self, path: str, out_path: Path, tag: str, round_id: str | None = None) -> dict:
        self.seq += 1
        req_id = f"{self.task_id}-{round_id + '-' if round_id else ''}G{self.seq:04d}"
        url = f"{SERVICE_URL}{path}"
        started_at = iso_now()
        t0 = time.time()
        res = http_call("GET", url, None, out_path)
        wall = round(time.time() - t0, 3)
        record = {
            "id": req_id,
            "task_id": self.task_id,
            "round": round_id,
            "kind": "service_get",
            "tag": tag,
            "method": "GET",
            "url_path": path,
            "started_at": started_at,
            "ended_at": iso_now(),
            "timezone": "Asia/Shanghai",
            "elapsed_s": wall,
            "service_elapsed_s": res["elapsed_s"],
            "http_status": res["status"],
            "content_type": res["content_type"],
            "response_bytes": res["bytes"],
            "response_file": rel(out_path),
            "error": res["error"],
            "request_id_header": res["request_id"],
            "attempt_count": len(res["attempts"]),
            "path_base": "suite_root",
        }
        append_jsonl(self.requests_path, record)
        return record

    def iteration(self, record: dict) -> None:
        payload = {
            "task_id": self.task_id,
            "logged_at": iso_now(),
            "timezone": "Asia/Shanghai",
            "path_base": "suite_root",
        }
        payload.update(record)
        append_jsonl(self.iterations_path, payload)

    def tool(self, record: dict) -> None:
        payload = {"task_id": self.task_id, "logged_at": iso_now(), "path_base": "suite_root"}
        payload.update(record)
        append_jsonl(self.tool_usage_path, payload)

    def view(self, image_path: Path, note: str, iteration_id: str | None = None) -> None:
        """Record that an image was actually opened for visual inspection."""
        self.tool({
            "kind": "view_image",
            "iteration_id": iteration_id,
            "image": rel(image_path),
            "note": note,
        })


def measure_png(path: Path) -> tuple[int, int]:
    """Return (width, height) of a PNG without external libraries."""
    data = path.read_bytes()[:33]
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not a PNG file: {path}")
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    return width, height


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

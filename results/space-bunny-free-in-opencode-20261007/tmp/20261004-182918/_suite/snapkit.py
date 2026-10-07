"""Shared Snapshot render/trace toolkit for the full suite run.

Usage (as a library):
    import snapkit
    snapkit.configure(run_id, task_id, output_dir, temp_dir)
    r = snapkit.render(dsl_text, out_name="operations.png", dsl_name="operations.snapshot")

Every render attempt is appended to <temp_dir>/requests.jsonl and
<temp_dir>/iterations.jsonl is managed by snapkit.iteration(...).
No credentials are read or stored; the public service allows anonymous access.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
import urllib.error
import uuid
from datetime import datetime, timezone, timedelta

BASE = "https://open-snapshot.muedsa.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
CST = timezone(timedelta(hours=8))

RUN_ID = "20261004-182918"
TASK_ID = "_suite"
OUTPUT_DIR = ""
TEMP_DIR = ""
_state = {"req_seq": 0, "iter_seq": 0}


def now_iso() -> str:
    return datetime.now(CST).isoformat(timespec="milliseconds")


def configure(task_id: str, output_dir: str, temp_dir: str) -> None:
    global TASK_ID, OUTPUT_DIR, TEMP_DIR
    TASK_ID = task_id
    OUTPUT_DIR = output_dir
    TEMP_DIR = temp_dir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)


def _jsonl(path: str, obj: dict) -> None:
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


def next_id(prefix: str) -> str:
    """Monotonic per-task id that survives across separate generator processes."""
    import re
    n = _state.get(prefix, 0)
    path = os.path.join(TEMP_DIR, "requests.jsonl")
    if os.path.exists(path):
        pat = re.compile(r"^%s-%s-(\d+)$" % (re.escape(TASK_ID), re.escape(prefix)))
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                m = pat.match(json.loads(line).get("request_id", ""))
                if m:
                    n = max(n, int(m.group(1)))
    n += 1
    _state[prefix] = n
    return "%s-%s-%03d" % (TASK_ID, prefix, n)


def log_render_request(*, dsl_file: str, resp_file: str | None, status: int | None,
                       content_type: str | None, started: str, elapsed_ms: float,
                       error: str | None, request_id: str | None,
                       server_timing: str | None, req_id: str,
                       extra_headers: dict | None = None, retries: int = 0) -> None:
    _jsonl(os.path.join(TEMP_DIR, "requests.jsonl"), {
        "request_id": req_id,
        "request_type": "render",
        "task_id": TASK_ID,
        "method": "POST",
        "url": BASE + "/snapshot",
        "credentials_in_request": False,
        "started_at": started,
        "ended_at": now_iso(),
        "timezone": "Asia/Shanghai (+08:00)",
        "duration_ms": round(elapsed_ms, 1),
        "http_status": status,
        "content_type": content_type,
        "request_file": dsl_file,
        "response_file": resp_file,
        "error_summary": error,
        "service_request_id": request_id,
        "server_timing": server_timing,
        "extra_headers": extra_headers or {},
        "retry_attempt": retries,
    })


def log_other_request(*, req_id: str, kind: str, url: str, started: str,
                      elapsed_ms: float, status: int | None,
                      content_type: str | None, resp_file: str | None,
                      error: str | None, request_id: str | None,
                      server_timing: str | None, extra_headers: dict | None = None) -> None:
    _jsonl(os.path.join(TEMP_DIR, "requests.jsonl"), {
        "request_id": req_id,
        "request_type": kind,
        "task_id": TASK_ID,
        "method": "GET",
        "url": url,
        "credentials_in_request": False,
        "started_at": started,
        "ended_at": now_iso(),
        "timezone": "Asia/Shanghai (+08:00)",
        "duration_ms": round(elapsed_ms, 1),
        "http_status": status,
        "content_type": content_type,
        "request_file": None,
        "response_file": resp_file,
        "error_summary": error,
        "service_request_id": request_id,
        "server_timing": server_timing,
        "extra_headers": extra_headers or {},
        "retry_attempt": 0,
    })


def log_iteration(*, version: str, parent: str | None, kind: str, dsl_file: str,
                  image_file: str | None, viewed_at: str | None,
                  observed: str | None, changes: str | None,
                  compared: str | None, complete: bool, note: str | None = None) -> None:
    _jsonl(os.path.join(TEMP_DIR, "iterations.jsonl"), {
        "iteration_id": version,
        "parent_version": parent,
        "type": kind,
        "task_id": TASK_ID,
        "dsl_file": dsl_file,
        "image_file": image_file,
        "viewed_at": viewed_at,
        "observed_issue": observed,
        "changes": changes,
        "recheck_result": compared,
        "complete_visual_iteration": complete,
        "note": note,
    })


def fetch_doc(url: str, name: str, kind: str = "document") -> tuple[int, str | None]:
    """Fetch a doc/service endpoint into the temp dir and log it."""
    req_id = next_id("req")
    started = now_iso()
    t0 = time.perf_counter()
    status, ctype, body, err, rid = None, None, None, None, None
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            status = resp.status
            ctype = resp.headers.get("Content-Type")
            rid = resp.headers.get("X-Request-Id")
            body = resp.read()
    except urllib.error.HTTPError as e:
        status = e.code
        ctype = e.headers.get("Content-Type") if e.headers else None
        rid = e.headers.get("X-Request-Id") if e.headers else None
        body = e.read()
        err = "HTTPError %s: %s" % (e.code, body[:400].decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        err = "%s: %s" % (type(e).__name__, e)
    elapsed = (time.perf_counter() - t0) * 1000
    path = os.path.join(TEMP_DIR, "docs", name) if kind == "document" else os.path.join(TEMP_DIR, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if body is not None:
        with open(path, "wb") as fh:
            fh.write(body)
    log_other_request(req_id=req_id, kind=kind, url=url, started=started,
                      elapsed_ms=elapsed, status=status, content_type=ctype,
                      resp_file=path if body is not None else None,
                      error=err, request_id=rid, server_timing=None,
                      extra_headers={"retry_after": None} if err is None else {})
    return status, path if body is not None else err


def render(dsl_text: str, out_name: str, dsl_name: str | None = None,
           final: bool = True, max_attempts: int = 6, out_dir: str | None = None) -> dict:
    """Render DSL text. final=True writes into OUTPUT_DIR; out_dir overrides both."""
    dsl_name = dsl_name or (out_name.rsplit(".", 1)[0] + ".snapshot")
    final_dir = out_dir or (OUTPUT_DIR if final else os.path.join(TEMP_DIR, "preview"))
    os.makedirs(final_dir, exist_ok=True)
    dsl_path = os.path.join(final_dir, dsl_name)
    with open(dsl_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dsl_text)
    payload = dsl_text.encode("utf-8")

    attempt = 0
    last = None
    while attempt < max_attempts:
        attempt += 1
        req_id = next_id("req")
        started = now_iso()
        t0 = time.perf_counter()
        status, ctype, rid, stime, body = None, None, None, None, None
        err = None
        extra = {}
        req = urllib.request.Request(
            BASE + "/snapshot", data=payload, method="POST",
            headers={"Content-Type": "text/plain; charset=utf-8",
                     "User-Agent": UA,
                     "X-Request-Id": req_id})
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                status = resp.status
                ctype = resp.headers.get("Content-Type")
                rid = resp.headers.get("X-Request-Id")
                stime = resp.headers.get("Server-Timing")
                body = resp.read()
        except urllib.error.HTTPError as e:
            status = e.code
            ctype = e.headers.get("Content-Type") if e.headers else None
            rid = e.headers.get("X-Request-Id") if e.headers else None
            body = e.read()
            retry_after = e.headers.get("Retry-After") if e.headers else None
            extra["retry_after"] = retry_after
            err = body[:600].decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            err = "%s: %s" % (type(e).__name__, e)
        elapsed = (time.perf_counter() - t0) * 1000

        is_image = bool(body) and (ctype or "").startswith("image/")
        resp_path = None
        if body:
            if is_image:
                resp_path = os.path.join(final_dir, out_name)
                with open(resp_path, "wb") as fh:
                    fh.write(body)
            else:
                resp_path = os.path.join(
                    TEMP_DIR, "responses",
                    "resp-%s-%s-att%d.txt" % (req_id, uuid.uuid4().hex[:6], attempt))
                os.makedirs(os.path.dirname(resp_path), exist_ok=True)
                with open(resp_path, "wb") as fh:
                    fh.write(body)

        log_render_request(dsl_file=dsl_path, resp_file=resp_path, status=status,
                           content_type=ctype, started=started, elapsed_ms=elapsed,
                           error=None if is_image else err, request_id=rid,
                           server_timing=stime, req_id=req_id,
                           extra_headers=extra, retries=attempt - 1)

        if is_image:
            last = {"ok": True, "status": status, "image": resp_path,
                    "dsl": dsl_path, "bytes": len(body), "request_id": rid,
                    "server_timing": stime, "attempts": attempt,
                    "elapsed_ms": round(elapsed, 1), "request_id_local": req_id}
            return last

        # retryable?
        if status in (429, 503) and attempt < max_attempts:
            wait = extra.get("retry_after")
            try:
                wait = float(wait)
            except (TypeError, ValueError):
                wait = 3.0 * attempt
            time.sleep(min(max(wait, 1.0), 30.0))
            continue
        last = {"ok": False, "status": status, "error": err, "response_file": resp_path,
                "content_type": ctype, "request_id": rid, "attempts": attempt,
                "elapsed_ms": round(elapsed, 1), "request_id_local": req_id,
                "dsl": dsl_path}
        return last
    return last or {"ok": False, "status": None, "error": "no attempt"}


def new_version(kind: str, parent: str | None, dsl_file: str, image_file: str | None,
                observed: str | None = None, changes: str | None = None,
                complete: bool = False, note: str | None = None,
                viewed_at: str | None = None, compared: str | None = None) -> str:
    _state["iter_seq"] = _state.get("iter_seq", 0) + 1
    v = "%s-v%02d" % (TASK_ID, _state["iter_seq"])
    log_iteration(version=v, parent=parent, kind=kind, dsl_file=dsl_file,
                  image_file=image_file, viewed_at=viewed_at, observed=observed,
                  changes=changes, compared=compared, complete=complete, note=note)
    return v
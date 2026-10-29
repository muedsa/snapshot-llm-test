#!/usr/bin/env python3
"""Render Snapshot DSL files through the real /snapshot service.

Usage:
  python render.py --task A01 [--case case-01] [--tag final] file1.snapshot ...
  python render.py --task A01 --dir outputs/<run>/A01/case-01   (renders every *.snapshot)

Each DSL is rendered to <same stem>.png next to it (or --out-dir). Raw response bytes are
written verbatim. Requests are appended to tmp/<run_id>/<task>/requests.jsonl.
Paths in logs are relative to the suite root (path_base suite_root) or to the task output
root where noted; never absolute machine paths.
"""
import argparse
import hashlib
import json
import os
import random
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_TMP = SCRIPT.parents[1]                  # tmp/<run_id>/_suite
SUITE_ROOT = SUITE_TMP.parents[1]              # task suite root
RUN_ID = SUITE_TMP.parent.name
BASE = os.environ.get("SNAPSHOT_URL", "https://open-snapshot.muedsa.com").rstrip("/")
LOCK = threading.Lock()
ATTEMPT_SEQ = [0]


def rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(SUITE_ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def log_record(task: str, rec: dict):
    d = SUITE_TMP.parent / task
    d.mkdir(parents=True, exist_ok=True)
    with LOCK:
        with (d / "requests.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def render_one(task, dsl_path: Path, out_png: Path, tag: str, timeout: int = 120) -> dict:
    body = dsl_path.read_bytes()
    att = {"task_id": task, "tag": tag, "dsl": rel(dsl_path),
           "png": rel(out_png), "dsl_sha256": hashlib.sha256(body).hexdigest(),
           "request_bytes": len(body)}
    delay = 2.0
    for attempt in range(1, 4):
        with LOCK:
            ATTEMPT_SEQ[0] += 1
            attempt_id = ATTEMPT_SEQ[0]
        req_id = uuid.uuid4().hex[:12]
        t0 = time.time()
        rec = dict(att, request_id=req_id, attempt=attempt, attempt_seq=attempt_id,
                   started_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"), url=BASE + "/snapshot")
        try:
            req = urllib.request.Request(
                BASE + "/snapshot", data=body, method="POST",
                headers={"Content-Type": "text/plain; charset=utf-8",
                         "User-Agent": "snapshot-suite/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
                rec["http_status"] = r.status
                rec["server_request_id"] = r.headers.get("X-Request-Id")
                rec["content_type"] = r.headers.get("Content-Type")
            rec["duration_ms"] = int((time.time() - t0) * 1000)
            rec["response_bytes"] = len(data)
            if rec["http_status"] == 200 and data[:4] in (b"\x89PNG", b"\xff\xd8\xff\xe0", b"RIFF"):
                out_png.parent.mkdir(parents=True, exist_ok=True)
                out_png.write_bytes(data)
                rec.update(status="success", png_bytes=len(data))
                log_record(task, rec)
                return rec
            # 200 but not an image: keep raw and treat as failure
            raw = out_png.with_suffix(out_png.suffix + ".error.bin")
            raw.write_bytes(data)
            rec.update(status="error", error="non-image response", raw=rel(raw))
            log_record(task, rec)
        except urllib.error.HTTPError as e:
            data = e.read() or b""
            rec["http_status"] = e.code
            rec["duration_ms"] = int((time.time() - t0) * 1000)
            rec["response_bytes"] = len(data)
            rec["error_body"] = data.decode("utf-8", "replace")[:4000]
            rec["status"] = "error"
            raw = out_png.with_suffix(out_png.suffix + f".http{e.code}.txt")
            raw.write_bytes(data)
            rec["raw"] = rel(raw)
            log_record(task, rec)
            retry_after = e.headers.get("Retry-After") if e.headers else None
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                wait = float(retry_after) if (retry_after or "").isdigit() else delay
                time.sleep(min(wait, 30) + random.random())
                delay *= 2
                continue
            return rec
        except Exception as e:
            rec["duration_ms"] = int((time.time() - t0) * 1000)
            rec.update(status="error", error=repr(e))
            log_record(task, rec)
            if attempt < 3:
                time.sleep(delay)
                delay *= 2
                continue
            return rec
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--tag", default="final")
    ap.add_argument("--dir", action="append", default=[])
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("files", nargs="*")
    a = ap.parse_args()

    files = []
    for f in a.files:
        p = Path(f)
        if not p.is_absolute():
            p = Path.cwd() / p
        files.append(p)
    for d in a.dir:
        p = Path(d)
        if not p.is_absolute():
            p = Path.cwd() / p
        files.extend(sorted(p.glob("*.snapshot")))
    if not files:
        print("no .snapshot files", file=sys.stderr)
        return 2

    out_dir = Path(a.out_dir) if a.out_dir else None
    results = []
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = {}
        for f in files:
            png = (out_dir / (f.stem + ".png")) if out_dir else f.with_suffix(".png")
            futs[ex.submit(render_one, a.task, f, png, a.tag)] = f
        for fu in as_completed(futs):
            rec = fu.result()
            results.append(rec)
            print(json.dumps({k: rec.get(k) for k in
                  ("dsl", "status", "http_status", "png", "duration_ms", "error_body", "error")},
                  ensure_ascii=False))
    ok = sum(1 for r in results if r.get("status") == "success")
    print(f"done: {ok}/{len(results)} succeeded")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())

"""render.py - write a DSL to disk (no BOM) and POST it to the live service.

Usage:
    python render.py <dsl_path> <out_png_path> <request_id> [phase] [case_id]

Only ever writes bytes that came back from a 200 image/* response. Failures are kept
next to the attempt as .failed.txt / .headers.txt so no failed body is ever mistaken
for a final image.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TZ = timezone(timedelta(hours=8))
BASE = "https://open-snapshot.muedsa.com"
TASK = os.environ.get("SK_TASK", "B04")
TMP = os.path.join(ROOT, "tmp", RUN_ID, TASK)
LOG = os.path.join(TMP, "requests.jsonl")


def now():
    return datetime.now(TZ)


def post(dsl_path: str, out_path: str, req_id: str, phase: str = "render",
         case_id: str | None = None, url_path: str = "/snapshot") -> dict:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    dsl_path = os.path.abspath(dsl_path)
    body = open(dsl_path, "rb").read()
    t0 = now()
    sw = time.time()
    cp = subprocess.run(
        ["curl.exe", "-sS", "-X", "POST", BASE + url_path,
         "-H", "Content-Type: text/plain; charset=utf-8",
         "--data-binary", "@" + dsl_path,
         "-D", out_path + ".headers.txt",
         "-w", "%{http_code}|%{content_type}|%{size_download}|%{time_total}",
         "-o", out_path + ".body"],
        capture_output=True)
    dur = int((time.time() - sw) * 1000)
    t1 = now()
    meta = (cp.stdout or b"").decode("utf-8", "replace").strip()
    parts = meta.split("|")
    status = int(parts[0]) if parts and parts[0].isdigit() else None
    ctype = parts[1] if len(parts) > 1 else None
    rbytes = open(out_path + ".body", "rb").read() if os.path.exists(out_path + ".body") else b""
    ok = status == 200 and ctype is not None and "image/" in ctype and len(rbytes) > 8
    req_srv, timing = None, None
    if os.path.exists(out_path + ".headers.txt"):
        for line in open(out_path + ".headers.txt", encoding="utf-8", errors="replace"):
            l = line.strip()
            if l.lower().startswith("x-request-id:"):
                req_srv = l.split(":", 1)[1].strip()
            if l.lower().startswith("server-timing:"):
                timing = l.split(":", 1)[1].strip()
    err = None
    if ok:
        with open(out_path, "wb") as fh:
            fh.write(rbytes)
        for suf in (".body",):
            try:
                os.remove(out_path + suf)
            except OSError:
                pass
    else:
        err = rbytes.decode("utf-8", "replace")[:2000] or (cp.stderr or b"").decode("utf-8", "replace")[:2000]
        with open(out_path + ".failed.txt", "wb") as fh:
            fh.write(rbytes)
        try:
            os.remove(out_path + ".body")
        except OSError:
            pass
    rec = {
        "request_id": req_id, "run_id": RUN_ID, "task_id": TASK, "round": None,
        "case_id": case_id, "phase": phase, "request_kind": "render", "method": "POST",
        "url": url_path, "query": None,
        "started_at": t0.isoformat(timespec="seconds"), "ended_at": t1.isoformat(timespec="seconds"),
        "tz": "+08:00", "duration_ms": dur,
        "http_status": status, "content_type": ctype,
        "request_file": os.path.relpath(dsl_path, ROOT), "request_bytes": len(body),
        "response_file": os.path.relpath(out_path, ROOT) if ok else None,
        "response_bytes": len(rbytes) if ok else 0,
        "service_request_id": req_srv, "server_timing": timing,
        "success": ok, "error": err,
    }
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


if __name__ == "__main__":
    dsl, out, rid = sys.argv[1], sys.argv[2], sys.argv[3]
    phase = sys.argv[4] if len(sys.argv) > 4 else "render"
    case = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] != "-" else None
    r = post(dsl, out, rid, phase, case)
    print(json.dumps({k: r[k] for k in ("request_id", "http_status", "content_type",
                                        "response_bytes", "duration_ms", "success", "error")},
                     ensure_ascii=False))
    sys.exit(0 if r["success"] else 1)

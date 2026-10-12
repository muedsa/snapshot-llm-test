"""Render a Snapshot DSL file through the open-snapshot service and log the request.

Run from the suite root (or set SNAPSHOT_TASK_ROOT to it). Requires SNAPSHOT_RUN_ID.

Usage:
  python tmp/<run_id>/_suite/scripts/render.py --task A01 --in tmp/<run_id>/A01/v01.snapshot \
      --out outputs/<run_id>/A01/operations.png --version v01 --kind visual
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

suite_root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
run_id = os.environ["SNAPSHOT_RUN_ID"]
BASE = os.environ.get("SNAPSHOT_URL", "https://open-snapshot.muedsa.com")


def log(rec, log_path):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def render(task, infile, outfile, version, kind, attempt_note, seq_dir=None):
    in_path = Path(infile)
    dsl = in_path.read_text(encoding="utf-8")
    out_path = Path(outfile)
    temp_dir = suite_root / "tmp" / run_id / task
    seq_root = Path(seq_dir) if seq_dir else out_path.parent
    req_dir = seq_root / "requests"
    req_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base_name = f"{task}-{version}-{stamp}"

    body_file = req_dir / f"{base_name}.body.txt"
    body_file.write_text(
        f"POST {BASE}/snapshot HTTP/1.1\nContent-Type: text/plain; charset=utf-8\n\n{dsl}",
        encoding="utf-8")

    hdr_file = req_dir / f"{base_name}.response-headers.txt"
    payload_file = req_dir / f"{base_name}.response.bin"

    started = datetime.now(timezone.utc)
    t0 = time.monotonic()
    cmd = [
        "curl", "-sS", "-D", str(hdr_file), "-o", str(payload_file),
        "-w", "%{http_code}\t%{content_type}\t%{size_download}",
        "--connect-timeout", "25", "--max-time", "240",
        "-X", "POST", f"{BASE}/snapshot",
        "-H", "Content-Type: text/plain; charset=utf-8",
        "--data-binary", f"@{in_path}",
    ]
    if os.environ.get("SNAPSHOT_API_KEY"):
        cmd[cmd.index("--data-binary") - 2:cmd.index("--data-binary") - 2] = [
            "-H", f"X-API-Key: {os.environ['SNAPSHOT_API_KEY']}"]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    dur = time.monotonic() - t0
    ended = datetime.now(timezone.utc)

    fields = (p.stdout or "").strip().split("\t")
    status = int(fields[0]) if fields and fields[0].isdigit() else None
    ctype = fields[1] if len(fields) > 2 else ""
    nbytes = int(float(fields[2])) if len(fields) > 2 and fields[2] else 0

    hdr_text = hdr_file.read_text(encoding="utf-8", errors="replace") if hdr_file.exists() else ""
    xrid = srv_timing = retry_after = cache = imgcount = rlimit = clen = None
    for line in hdr_text.splitlines():
        low = line.lower()
        if low.startswith("x-request-id:"):
            xrid = line.split(":", 1)[1].strip()
        elif low.startswith("server-timing:"):
            srv_timing = line.split(":", 1)[1].strip()
        elif low.startswith("retry-after:"):
            retry_after = line.split(":", 1)[1].strip()
        elif low.startswith("x-snapshot-cache:"):
            cache = line.split(":", 1)[1].strip()
        elif low.startswith("x-snapshot-image-count:"):
            imgcount = line.split(":", 1)[1].strip()
        elif low.startswith("content-length:"):
            clen = line.split(":", 1)[1].strip()
        elif low.startswith("x-ratelimit-"):
            rlimit = (rlimit + "; " if rlimit else "") + line.strip()

    ok = status == 200 and ctype.startswith("image/")
    # a reset mid-transfer still reports 200 with a short body: never accept a
    # truncated image (observed on A08 v02: 42718 of 271970 bytes).
    if ok and clen and int(clen) != nbytes:
        ok = False
        status = None
    err_summary = None
    if not ok:
        if clen and int(clen) != nbytes:
            err_summary = (f"truncated response body: got {nbytes} of {clen} bytes "
                           f"(Content-Length mismatch); retry required")
        elif payload_file.exists() and payload_file.stat().st_size:
            err_summary = payload_file.read_text(encoding="utf-8", errors="replace")[:600]
        else:
            err_summary = ("no response body written by curl; "
                           f"stderr={(p.stderr or '')[:400]}; exit={p.returncode}")

    def rel(x):
        p = Path(x)
        if not p.is_absolute():
            p = Path(os.path.abspath(str(p)))
        try:
            return p.resolve().relative_to(Path(suite_root).resolve()).as_posix()
        except ValueError:
            return p.resolve().as_posix()

    rec = {
        "request_id": base_name,
        "task_id": task,
        "kind": "render",
        "dsl_version": version,
        "iteration_kind_hint": kind,
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "duration_seconds": round(dur, 3),
        "method": "POST",
        "url": f"{BASE}/snapshot",
        "http_status": status,
        "content_type": ctype or None,
        "response_bytes": nbytes,
        "request_file": rel(body_file),
        "response_file": rel(payload_file) if not ok else None,
        "headers_file": rel(hdr_file),
        "error_summary": err_summary,
        "request_id_header": xrid,
        "server_timing": srv_timing,
        "retry_after": retry_after,
        "snapshot_cache": cache,
        "snapshot_image_count": imgcount,
        "ratelimit": rlimit,
        "attempt_note": attempt_note,
        "path_base": "suite_root",
    }

    if ok:
        ext = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}[ctype]
        if out_path.suffix.lower() != ext:
            out_path = out_path.with_suffix(ext)
            rec["note"] = f"extension corrected to {ext}"
        payload_file.write_bytes(payload_file.read_bytes())
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(payload_file.read_bytes())
        rec["response_file"] = rel(out_path)
        rec["raw_copy_file"] = rel(payload_file)
        rec["out_file"] = rel(out_path)

    log(rec, temp_dir / "requests.jsonl")
    return rec


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--in", dest="infile", required=True)
    ap.add_argument("--out", dest="outfile", required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--kind", default="visual")
    ap.add_argument("--note", default=None)
    ap.add_argument("--seq-dir", default=None)
    ap.add_argument("--retries", type=int, default=2,
                    help="extra attempts when the service is unavailable (429/503/transport)")
    a = ap.parse_args()
    r = render(a.task, a.infile, a.outfile, a.version, a.kind, a.note, a.seq_dir)
    attempt = 0
    while r["http_status"] in (429, 503, 504, 0, None) and attempt < a.retries:
        attempt += 1
        wait = float(r.get("retry_after") or 3)
        time.sleep(wait)
        r = render(a.task, a.infile, a.outfile, a.version, "retry",
                   f"retry {attempt} after {r['http_status']} "
                   f"(Retry-After={r.get('retry_after')})", a.seq_dir)
    print(json.dumps({k: r.get(k) for k in
                      ("request_id", "http_status", "content_type", "response_bytes",
                       "out_file", "error_summary", "server_timing", "request_id_header")},
                     ensure_ascii=False, indent=2))
    sys.exit(0 if r["http_status"] == 200 else 1)

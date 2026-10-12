"""Fetch one extra documentation page into the shared docs cache and log the request.

Run from the suite root (or set SNAPSHOT_TASK_ROOT). Requires SNAPSHOT_RUN_ID.
Adds a "doc" record to tmp/<run_id>/_suite/requests.jsonl and writes <out> plus <out>.txt.

Usage:
  python tmp/<run_id>/_suite/scripts/fetch_extra.py --key richtext \
      --url https://snapshot.muedsa.com/widgets/text/rich-text/ --out richtext.html
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
docs_dir = suite_root / "tmp" / run_id / "_suite" / "docs"

ap = argparse.ArgumentParser()
ap.add_argument("--key", required=True)
ap.add_argument("--url", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--task", default="shared")
a = ap.parse_args()
log_path = suite_root / "tmp" / run_id / ("_suite" if a.task == "shared" else a.task) / "requests.jsonl"
log_path.parent.mkdir(parents=True, exist_ok=True)

docs_dir.mkdir(parents=True, exist_ok=True)
dst = docs_dir / a.out
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
rid = f"{a.task}-{a.key}-{stamp}"
hdr = docs_dir / f"{a.out}.headers.txt"
t0 = time.monotonic()
started = datetime.now(timezone.utc)
p = subprocess.run(["curl", "-sS", "-L", "-D", str(hdr), "-o", str(dst),
                    "-w", "%{http_code}\t%{content_type}\t%{size_download}",
                    "--connect-timeout", "25", "--max-time", "120", a.url],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
dur = time.monotonic() - t0
f = (p.stdout or "").strip().split("\t")
status = int(f[0]) if f and f[0].isdigit() else None
ctype = f[1] if len(f) > 1 else ""
nbytes = int(float(f[2])) if len(f) > 2 and f[2] else 0
txt = None
if status == 200 and ctype.startswith("text/html"):
    sys.path.insert(0, str(Path(__file__).parent))
    os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(suite_root))
    os.environ.setdefault("SNAPSHOT_RUN_ID", run_id)
    argv_save, sys.argv = sys.argv, ["html2txt"]
    try:
        import html2txt  # noqa: E402
        html2txt.convert(a.out)
    finally:
        sys.argv = argv_save
    txt = docs_dir / f"{a.out}.txt"
rec = {"request_id": rid, "task_id": a.task, "kind": "doc", "url": a.url,
       "http_status": status, "content_type": ctype or None, "response_bytes": nbytes,
       "duration_seconds": round(dur, 3),
       "started_at": started.isoformat(),
       "ended_at": datetime.now(timezone.utc).isoformat(),
       "response_file": f"tmp/{run_id}/_suite/docs/{a.out}",
       "text_file": f"tmp/{run_id}/_suite/docs/{a.out}.txt" if txt else None,
       "headers_file": f"tmp/{run_id}/_suite/docs/{a.out}.headers.txt",
       "error_summary": None if status == 200 else (dst.read_text(encoding="utf-8",
                                                                   errors="replace")[:300]
                                                    if dst.exists() else p.stderr[:300]),
       "path_base": "suite_root"}
with log_path.open("a", encoding="utf-8") as fh:
    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
print(json.dumps(rec, ensure_ascii=False, indent=1))
sys.exit(0 if status == 200 else 1)

"""Shared preparation: fetch service guide + DSL docs, log each request.

Run from the suite root (or set SNAPSHOT_TASK_ROOT to it).
Usage: python tmp/<run_id>/_suite/scripts/fetch_docs.py
"""
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
docs_dir.mkdir(parents=True, exist_ok=True)
log_path = suite_root / "tmp" / run_id / "_suite" / "requests.jsonl"

BASE = "https://open-snapshot.muedsa.com"
DOCSITE = "https://snapshot.muedsa.com"

TARGETS = [
    ("guide-ai", f"{BASE}/ai-guide.md", "ai-guide.md"),
    ("openapi", f"{BASE}/openapi.yaml", "openapi.yaml"),
    ("doc-home", f"{DOCSITE}/", "doc-home.html"),
    ("doc-parser-tags", f"{DOCSITE}/reference/parser-tags/", "parser-tags.html"),
    ("doc-widgets", f"{DOCSITE}/guides/widgets/", "widgets.html"),
    ("doc-container", f"{DOCSITE}/widgets/layout/container/", "container.html"),
    ("doc-concepts", f"{DOCSITE}/guides/concepts/", "concepts.html"),
    ("doc-layout", f"{DOCSITE}/guides/layout/", "layout.html"),
    ("doc-painting", f"{DOCSITE}/guides/painting/", "painting.html"),
    ("doc-media-text", f"{DOCSITE}/guides/media-text/", "media-text.html"),
    ("doc-rendering", f"{DOCSITE}/guides/rendering/", "rendering.html"),
    ("doc-parser", f"{DOCSITE}/guides/parser/", "parser.html"),
]


def log(rec):
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def fetch(idx, key, url, fname):
    out = docs_dir / fname
    hdr = docs_dir / (fname + ".headers.txt")
    started = datetime.now(timezone.utc)
    t0 = time.monotonic()
    cmd = ["curl", "-sS", "-L", "-D", str(hdr), "-o", str(out), "-w",
           "%{http_code}\t%{content_type}\t%{size_download}", url]
    p = subprocess.run(cmd, capture_output=True, text=True)
    dur = time.monotonic() - t0
    ended = datetime.now(timezone.utc)
    fields = (p.stdout or "").strip().split("\t")
    status = int(fields[0]) if fields and fields[0].isdigit() else None
    ctype = fields[1] if len(fields) > 2 else None
    rec = {
        "request_id": f"shared-doc-{idx:03d}-{key}",
        "task_id": "shared",
        "kind": "document",
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "duration_seconds": round(dur, 3),
        "method": "GET",
        "url": url,
        "http_status": status,
        "content_type": ctype,
        "request_file": None,
        "response_file": out.relative_to(suite_root).as_posix(),
        "headers_file": hdr.relative_to(suite_root).as_posix(),
        "error_summary": (p.stderr or None) if status is None or status >= 400 else None,
        "request_id_header": None,
        "server_timing": None,
    }
    for line in hdr.read_text(encoding="utf-8", errors="replace").splitlines():
        low = line.lower()
        if low.startswith("x-request-id:") or low.startswith("x-request-id "):
            rec["request_id_header"] = line.split(":", 1)[1].strip()
        if low.startswith("server-timing:"):
            rec["server_timing"] = line.split(":", 1)[1].strip()
    log(rec)
    print(f"{status} {ctype} {url} -> {rec['response_file']}")
    return status


if __name__ == "__main__":
    fails = 0
    for i, (key, url, fname) in enumerate(TARGETS, start=1):
        try:
            s = fetch(i, key, url, fname)
            if s is None or s >= 400:
                fails += 1
        except Exception as exc:  # noqa: BLE001
            fails += 1
            print(f"ERROR {url}: {exc}")
    print(f"done, failures={fails}")

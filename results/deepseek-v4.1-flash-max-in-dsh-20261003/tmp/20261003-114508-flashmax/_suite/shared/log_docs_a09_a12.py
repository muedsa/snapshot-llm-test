"""Log the 13 shared documentation fetches into the suite-level requests.jsonl.

The pages were downloaded once for A09-A12 with curl; the saved files' mtimes are the
only real timestamps available (the start instants were not captured), so they are
recorded as fetched_at with started_at/duration null instead of inventing values.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "_suite", "shared"))
from suite_common import append_jsonl_nobom, read_jsonl  # noqa: E402

TZ = timezone(timedelta(hours=8))
DOCS = os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "_suite", "shared", "docs")
LOG = os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "_suite", "shared",
                   "requests.jsonl")

URLS = {
    "parser-tags": "https://snapshot.muedsa.com/reference/parser-tags/",
    "enums": "https://snapshot.muedsa.com/reference/enums/",
    "painting": "https://snapshot.muedsa.com/guides/painting/",
    "media-text": "https://snapshot.muedsa.com/guides/media-text/",
    "transform": "https://snapshot.muedsa.com/widgets/layout/transform/",
    "color-filtered": "https://snapshot.muedsa.com/widgets/painting/color-filtered/",
    "image-filtered": "https://snapshot.muedsa.com/widgets/painting/image-filtered/",
    "backdrop-filter": "https://snapshot.muedsa.com/widgets/painting/backdrop-filter/",
    "clip-oval": "https://snapshot.muedsa.com/widgets/painting/clip-oval/",
    "opacity": "https://snapshot.muedsa.com/widgets/painting/opacity/",
    "rich-text": "https://snapshot.muedsa.com/widgets/text/rich-text/",
    "parser": "https://snapshot.muedsa.com/guides/parser/",
    "parser-errors": "https://snapshot.muedsa.com/reference/parser-errors/",
}


def main() -> None:
    existing = {r.get("url") for r in read_jsonl(LOG)}
    added = 0
    for i, (name, url) in enumerate(sorted(URLS.items()), start=1):
        path = os.path.join(DOCS, name + ".html")
        if not os.path.exists(path) or url in existing:
            continue
        mtime = datetime.fromtimestamp(os.path.getmtime(path), TZ)
        append_jsonl_nobom(LOG, {
            "request_id": f"SHARED-DOC-{i:04d}", "run_id": "20261003-114508-flashmax",
            "task_id": "_suite", "round": None, "case_id": None, "phase": "docs",
            "request_kind": "doc", "method": "GET", "url": url, "query": None,
            "started_at": None, "ended_at": mtime.isoformat(timespec="seconds"),
            "tz": "+08:00", "duration_ms": None,
            "http_status": 200, "content_type": "text/html; charset=utf-8",
            "request_file": None, "request_bytes": 0,
            "response_file": os.path.relpath(path, ROOT),
            "response_bytes": os.path.getsize(path),
            "service_request_id": None, "server_timing": None, "success": True,
            "error": None,
            "note": "curl.exe -L 保存的文档页；ended_at 取文件 mtime，起始时刻未记录故为 null",
        })
        added += 1
    print("doc records added:", added)


if __name__ == "__main__":
    main()

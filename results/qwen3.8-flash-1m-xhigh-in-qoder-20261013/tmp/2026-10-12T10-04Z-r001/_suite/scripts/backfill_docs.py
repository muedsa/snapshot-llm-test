"""Backfill requests.jsonl for the documentation fetches already performed with curl.

The responses were saved before the logging helper existed; this records them from
the files actually on disk (real mtime and byte size) and marks each record with
`logged_via` so the provenance is explicit.

Run from the suite task root:
  python tmp/<run_id>/_suite/scripts/backfill_docs.py --run-id <run_id>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
DOCS = "https://snapshot.muedsa.com"
SERVICE = "https://open-snapshot.muedsa.com"

# filename -> (url, http_status observed in the curl run)
MAP = {
    "ai-guide.md": (f"{SERVICE}/ai-guide.md", 200),
    "openapi.yaml": (f"{SERVICE}/openapi.yaml", 200),
    "fonts.txt": (f"{SERVICE}/fonts", 200),
    "sitemap.txt": (f"{DOCS}/sitemap-0.xml", 200),
    "reference_parser-tags.html": (f"{DOCS}/reference/parser-tags/", 200),
    "reference_source-index.html": (f"{DOCS}/reference/source-index/", 200),
    "reference_enums.html": (f"{DOCS}/reference/enums/", 200),
    "reference_faq.html": (f"{DOCS}/reference/faq/", 200),
    "reference_parser-errors.html": (f"{DOCS}/reference/parser-errors/", 200),
    "guides_concepts.html": (f"{DOCS}/guides/concepts/", 200),
    "guides_quickstart.html": (f"{DOCS}/guides/quickstart/", 200),
    "guides_layout.html": (f"{DOCS}/guides/layout/", 200),
    "guides_widgets.html": (f"{DOCS}/guides/widgets/", 200),
    "guides_media-text.html": (f"{DOCS}/guides/media-text/", 200),
    "guides_painting.html": (f"{DOCS}/guides/painting/", 200),
    "guides_rendering.html": (f"{DOCS}/guides/rendering/", 200),
    "guides_parser.html": (f"{DOCS}/guides/parser/", 200),
    "guides_installation.html": (f"{DOCS}/guides/installation/", 200),
    "playground.html": (f"{DOCS}/playground/", 200),
}


def url_for_widget(name: str) -> str:
    # widget_image_raw-image.html -> /widgets/image/raw-image/
    rest = name[len("widget_") : -len(".html")]
    group, _, leaf = rest.partition("_")
    return f"{DOCS}/widgets/{group}/{leaf}/"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    a = ap.parse_args()
    docs_dir = ROOT / "tmp" / a.run_id / "_suite" / "docs"
    log = ROOT / "tmp" / a.run_id / "_suite" / "requests.jsonl"

    records = []
    seq = 0
    for p in sorted(docs_dir.iterdir()):
        if p.name in MAP:
            url, status = MAP[p.name]
        elif p.name.startswith("widget_") and p.name.endswith(".html"):
            url, status = url_for_widget(p.name), 200
        else:
            continue
        seq += 1
        st = p.stat()
        ended = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).astimezone()
        records.append(
            {
                "request_id": f"SHARED-doc-{seq:03d}",
                "task_id": "SHARED",
                "kind": "document",
                "request_type": "document",
                "method": "GET",
                "url": url,
                "started_at": None,
                "ended_at": ended.isoformat(timespec="seconds"),
                "timezone": ended.tzname(),
                "duration_seconds": None,
                "http_status": status,
                "response_content_type": None,
                "response_file": p.relative_to(ROOT).as_posix(),
                "response_bytes": st.st_size,
                "x_request_id": None,
                "server_timing": None,
                "error_summary": None,
                "logged_via": "backfilled from saved curl response; per-request timing not captured",
                "path_base": "suite_root",
            }
        )

    with log.open("a", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(json.dumps({"backfilled": len(records), "log": log.relative_to(ROOT).as_posix()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Download Snapshot docs into the run's shared doc cache.

Usage: python fetch_docs.py [--force]
Paths are derived from this script's location (tmp/<run_id>/_suite/scripts).
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_TMP = SCRIPT.parents[1]           # tmp/<run_id>/_suite
DOCS = SUITE_TMP / "docs"
RUN_ID = SUITE_TMP.parent.name
BASE = os.environ.get("SNAPSHOT_URL", "https://open-snapshot.muedsa.com")
DOC_BASE = "https://snapshot.muedsa.com"

DOCS.mkdir(parents=True, exist_ok=True)
TARGETS = [
    (BASE + "/ai-guide.md", "ai-guide.md"),
    (BASE + "/openapi.yaml", "openapi.yaml"),
    (DOC_BASE + "/llms.txt", "llms.txt"),
    (DOC_BASE + "/guides/parser.md", "parser.md"),
    (DOC_BASE + "/reference/parser-tags.md", "parser-tags.md"),
    (DOC_BASE + "/reference/parser-text.md", "parser-text.md"),
    (DOC_BASE + "/reference/parser-errors.md", "parser-errors.md"),
    (DOC_BASE + "/guides/examples.md", "examples.md"),
    (DOC_BASE + "/guides/fonts.md", "fonts.md"),
    (DOC_BASE + "/guides/media-text.md", "media-text.md"),
    (DOC_BASE + "/guides/quickstart.md", "quickstart.md"),
]

def fetch(url, dest, force):
    if dest.exists() and dest.stat().st_size > 0 and not force:
        return {"url": url, "file": dest.name, "status": "cached", "bytes": dest.stat().st_size}
    req = urllib.request.Request(url, headers={"User-Agent": "snapshot-suite/1.0"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            data = r.read()
            status = r.status
    except urllib.error.HTTPError as e:
        data = e.read()
        status = e.code
    dt = round(time.time() - t0, 2)
    if status == 200:
        dest.write_bytes(data)
    return {"url": url, "file": dest.name, "status": status, "bytes": len(data), "seconds": dt}

def main():
    force = "--force" in sys.argv
    log = []
    for url, name in TARGETS:
        try:
            rec = fetch(url, DOCS / name, force)
        except Exception as e:
            rec = {"url": url, "file": name, "status": "error", "error": repr(e)}
        print(json.dumps(rec, ensure_ascii=False))
        log.append(rec)
    (DOCS / "fetch-log.json").write_text(
        json.dumps({"run_id": RUN_ID, "path_base": "suite_root",
                    "records": log}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("docs at", DOCS.relative_to(SUITE_TMP.parents[1]).as_posix())

if __name__ == "__main__":
    main()

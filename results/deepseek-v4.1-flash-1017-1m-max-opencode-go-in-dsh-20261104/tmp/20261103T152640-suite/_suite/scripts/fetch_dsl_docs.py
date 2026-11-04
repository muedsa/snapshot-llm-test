# -*- coding: utf-8 -*-
"""Shared preparation: fetch the DSL documentation pages used by this suite.

Script base: suite_root. Uses SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID.
"""
import os
import json
import hashlib
import datetime
import urllib.request
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "20261103T152640-suite")
DOCS = SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "shared" / "docs"
DOCS.mkdir(parents=True, exist_ok=True)

PAGES = {
    "llms.txt": "https://snapshot.muedsa.com/llms.txt",
    "index.md": "https://snapshot.muedsa.com/index.md",
    "quickstart.md": "https://snapshot.muedsa.com/guides/quickstart.md",
    "parser.md": "https://snapshot.muedsa.com/guides/parser.md",
    "parser-tags.md": "https://snapshot.muedsa.com/reference/parser-tags.md",
    "parser-text.md": "https://snapshot.muedsa.com/reference/parser-text.md",
    "parser-errors.md": "https://snapshot.muedsa.com/reference/parser-errors.md",
    "examples.md": "https://snapshot.muedsa.com/guides/examples.md",
    "fonts.md": "https://snapshot.muedsa.com/guides/fonts.md",
    "media-text.md": "https://snapshot.muedsa.com/guides/media-text.md",
    "dsl-collection.txt": "https://snapshot.muedsa.com/_llms-txt/dsl.txt",
    "openapi.yaml": "https://open-snapshot.muedsa.com/openapi.yaml",
}

records = []
for name, url in PAGES.items():
    target = DOCS / name
    if target.exists() and target.stat().st_size > 0:
        records.append({"file": name, "url": url, "status": "cached",
                        "bytes": target.stat().st_size,
                        "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        print(f"CACHED  {name:22s} {target.stat().st_size:8d}")
        continue
    req = urllib.request.Request(url, headers={"User-Agent": "snapshot-suite-runner/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read()
            status = resp.status
            ctype = resp.headers.get("Content-Type")
    except Exception as exc:  # noqa: BLE001
        records.append({"file": name, "url": url, "status": "error", "error": str(exc)})
        print(f"ERROR   {name}: {exc}")
        continue
    target.write_bytes(raw)
    records.append({"file": name, "url": url, "status": status, "content_type": ctype,
                    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                    "fetched_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")})
    print(f"FETCHED {name:22s} {len(raw):8d} {ctype}")

meta = DOCS / "manifest-dsl.json"
old = []
if meta.exists():
    try:
        old = json.loads(meta.read_text(encoding="utf-8"))
    except Exception:
        old = []
keys = {(e.get("file"), e.get("url")) for e in records}
merged = records + [e for e in old if (e.get("file"), e.get("url")) not in keys]
meta.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
print("manifest:", meta.relative_to(SUITE_ROOT).as_posix())

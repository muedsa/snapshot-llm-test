# -*- coding: utf-8 -*-
"""Shared preparation: fetch and cache service documents.

Script base: suite_root (the directory that contains run-config.json).
Paths are relative to the suite root via SNAPSHOT_TASK_ROOT (default: cwd).
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

DOC_SET = {
    "ai-guide.md": "https://open-snapshot.muedsa.com/ai-guide.md",
    "ai-guide-root.html": "https://open-snapshot.muedsa.com/",
    "dsl-docs-index.html": "https://snapshot.muedsa.com/",
}

manifest = []
for name, url in DOC_SET.items():
    target = DOCS / name
    if target.exists() and target.stat().st_size > 0:
        manifest.append({
            "file": name, "url": url, "status": "cached",
            "bytes": target.stat().st_size,
            "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        })
        print(f"CACHED {name} ({target.stat().st_size} bytes)")
        continue
    req = urllib.request.Request(url, headers={"User-Agent": "snapshot-suite-runner/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            status = resp.status
            ctype = resp.headers.get("Content-Type")
    except Exception as exc:  # noqa: BLE001
        manifest.append({"file": name, "url": url, "status": "error", "error": str(exc)})
        print(f"ERROR {name}: {exc}")
        continue
    target.write_bytes(raw)
    manifest.append({
        "file": name, "url": url, "status": status, "content_type": ctype,
        "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
        "fetched_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    })
    print(f"FETCHED {name}: {status} {len(raw)} bytes {ctype}")

meta = DOCS / "manifest.json"
existing = []
if meta.exists():
    try:
        existing = json.loads(meta.read_text(encoding="utf-8"))
    except Exception:
        existing = []
keys = {(e.get("url"), e.get("file")) for e in manifest}
merged = manifest + [e for e in existing if (e.get("url"), e.get("file")) not in keys]
meta.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
print("manifest:", meta.relative_to(SUITE_ROOT).as_posix())

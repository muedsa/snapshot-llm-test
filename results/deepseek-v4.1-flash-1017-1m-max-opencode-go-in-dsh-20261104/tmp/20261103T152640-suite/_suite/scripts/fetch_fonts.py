# -*- coding: utf-8 -*-
"""Shared preparation: query /fonts from the live service and cache the list."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import snapshot_api as api  # noqa: E402

docs = api.SUITE_ROOT / "tmp" / api.RUN_ID / "_suite" / "shared"
out = docs / "fonts.txt"
rec = api.http_call("GET", f"{api.SERVICE_URL}/fonts", None, out)
print("status:", rec["status"], rec["content_type"], rec["bytes"], "bytes")
if rec["status"] == 200:
    text = out.read_text(encoding="utf-8", errors="replace")
    fams = [line.strip() for line in text.splitlines() if line.strip()]
    print("font families:", len(fams))
    for f in fams:
        print(" -", f)

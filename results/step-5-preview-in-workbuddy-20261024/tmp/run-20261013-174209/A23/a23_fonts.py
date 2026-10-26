#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A23 · 查询服务实际可用字体族（GET /fonts，text/plain，每行一个族名）。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "_suite"))
from render import Log, get_resource, rel, suite_root  # noqa: E402

ROOT = suite_root()
RUN_ID = "run-20261013-174209"
TMP = ROOT / "tmp" / RUN_ID / "A23"

if __name__ == "__main__":
    log = Log(ROOT, RUN_ID, "A23")
    r = get_resource("https://open-snapshot.muedsa.com/fonts")
    body = r.get("body") or b""
    text = body.decode("utf-8", "replace")
    (TMP / "fonts.txt").write_text(text, encoding="utf-8")
    fams = [l.strip() for l in text.splitlines() if l.strip()]
    rec = {
        "id": f"A23-fonts-{len(fams)}",
        "type": "fonts", "label": "A23-fonts",
        "method": "GET", "url": "https://open-snapshot.muedsa.com/fonts",
        "http_status": r.get("status"), "content_type": r.get("content_type"),
        "elapsed_s": r.get("elapsed_s"), "error": r.get("error"),
        "response_file": rel(TMP / "fonts.txt", ROOT),
        "font_family_count": len(fams),
        "task_id": "A23", "path_base": "suite_root",
    }
    log.request(rec)
    want = ["Noto Sans CJK SC", "Noto Sans Mono CJK SC"]
    for w in want:
        print(f"{w}: {'AVAILABLE' if w in fams else 'MISSING'}")
    print(f"total families={len(fams)} http={r.get('status')} "
          f"elapsed={r.get('elapsed_s')}s err={r.get('error')}")

# -*- coding: utf-8 -*-
"""A10：把本次真实抓取的官方文档记入本任务 requests.jsonl（snapkit.fetch_doc）。"""
from __future__ import annotations

import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import state as S  # noqa: E402

TASK = "A10"
snapkit.configure(TASK, os.path.join(S.OUT_ROOT, TASK),
                  os.path.join(S.TMP_ROOT, TASK))

DOCS = [
    ("https://snapshot.muedsa.com/reference/parser-tags/", "parser-tags.html"),
    ("https://snapshot.muedsa.com/guides/painting/", "guides-painting.html"),
    ("https://snapshot.muedsa.com/widgets/painting/color-filtered/",
     "widget-color-filtered.html"),
    ("https://snapshot.muedsa.com/widgets/painting/image-filtered/",
     "widget-image-filtered.html"),
    ("https://snapshot.muedsa.com/widgets/painting/backdrop-filter/",
     "widget-backdrop-filter.html"),
    ("https://snapshot.muedsa.com/widgets/painting/clip-oval/", "widget-clip-oval.html"),
    ("https://open-snapshot.muedsa.com/ai-guide.md", "ai-guide.md"),
]

for url, name in DOCS:
    status, path = snapkit.fetch_doc(url, name)
    size = os.path.getsize(path) if isinstance(path, str) and os.path.exists(path) else None
    print(status, name, size)
# -*- coding: utf-8 -*-
"""A09 setup: configure paths, start suite task, fetch DSL docs about Transform."""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
SUITE = os.path.join(ROOT, "tmp", "20261004-182918", "_suite")
sys.path.insert(0, SUITE)
import snapkit  # noqa: E402
import state as S  # noqa: E402

TASK = "A09"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)
snapkit.configure(TASK, OUT, TMP)
S.start_task(TASK)
print("started", TASK)
print("OUT", OUT)
print("TMP", TMP)

DOCS = [
    ("https://snapshot.muedsa.com/guides/layout/", "layout.html", "document"),
    ("https://snapshot.muedsa.com/reference/parser-tags/", "parser-tags.html", "document"),
]
for url, name, kind in DOCS:
    st, path = snapkit.fetch_doc(url, name, kind)
    print("fetch", url, "->", st, path)
# -*- coding: utf-8 -*-
"""Fetch the Transform widget doc and dump its text to a file for reading."""
import html
import os
import re
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
SUITE = os.path.join(ROOT, "tmp", "20261004-182918", "_suite")
sys.path.insert(0, SUITE)
import snapkit  # noqa: E402
import state as S  # noqa: E402

snapkit.configure("A09", os.path.join(S.OUT_ROOT, "A09"), os.path.join(S.TMP_ROOT, "A09"))

URLS = [
    ("https://snapshot.muedsa.com/widgets/layout/transform/", "transform.html"),
    ("https://snapshot.muedsa.com/guides/core-concepts/", "core-concepts.html"),
]
paths = []
for url, name in URLS:
    st, path = snapkit.fetch_doc(url, name, "document")
    print("fetch", url, "->", st, path)
    if st == 200:
        paths.append(path)

out_lines = []
for p in paths:
    t = open(p, encoding='utf-8', errors='replace').read()
    t = re.sub(r'<script.*?</script>', ' ', t, flags=re.S)
    t = re.sub(r'<style.*?</style>', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '\n', t)
    t = html.unescape(t)
    lines = [l.strip() for l in t.split('\n')]
    keep = [l for l in lines if l]
    dedup = []
    prev = ''
    for l in keep:
        if l == prev:
            continue
        dedup.append(l)
        prev = l
    out_lines.append("#### FILE: %s (%d lines)" % (os.path.basename(p), len(dedup)))
    out_lines.extend(dedup)

dst = os.path.join(S.TMP_ROOT, "A09", "docs", "transform-doc-text.txt")
with open(dst, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(out_lines))
print("wrote", dst, len(out_lines), "lines")
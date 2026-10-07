# -*- coding: utf-8 -*-
"""A13: fetch Text / DecoratedBox / ClipOval / ClipRRect docs and dump readable text."""
import io
import os
import re
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import state as S  # noqa: E402

TASK = "A13"
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, os.path.join(S.OUT_ROOT, TASK), TMP)

PAGES = [
    ("https://snapshot.muedsa.com/widgets/text/text/", "text.html"),
    ("https://snapshot.muedsa.com/widgets/painting/decorated-box/", "decorated-box.html"),
    ("https://snapshot.muedsa.com/widgets/painting/clip-oval/", "clip-oval.html"),
    ("https://snapshot.muedsa.com/widgets/painting/clip-rrect/", "clip-rrect.html"),
    ("https://snapshot.muedsa.com/widgets/painting/colored-box/", "colored-box.html"),
]


def to_text(html: str) -> str:
    html = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    html = re.sub(r"(?s)<[^>]+>", "\n", html)
    html = html.replace("&quot;", '"').replace("&#39;", "'").replace("&amp;", "&")
    html = html.replace("&lt;", "<").replace("&gt;", ">").replace("&nbsp;", " ")
    out, prev = [], None
    for line in html.split("\n"):
        t = line.strip()
        if t and t != prev:
            out.append(t)
        prev = t
    return "\n".join(out)


lines = []
for url, name in PAGES:
    st, path = snapkit.fetch_doc(url, name, "document")
    print("fetch", st, name)
    if st == 200 and path:
        lines.append("=== %s ===" % url)
        lines.append(to_text(io.open(path, encoding="utf-8").read()))

dst = os.path.join(TMP, "docs", "widget-attrs.txt")
with open(dst, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lines))
print("wrote", dst, len(lines), "lines")
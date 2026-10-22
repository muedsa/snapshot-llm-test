# -*- coding: utf-8 -*-
"""Find boxShadow / shadow format examples in the cached parser docs."""
import pathlib
import re

html = pathlib.Path("tmp/run-20261011-01/_suite/docs/parser-tags.html").read_text(
    encoding="utf-8")
plain = re.sub(r"<[^>]+>", " ", html)
plain = re.sub(r"\s+", " ", plain)

for kw in ("boxShadow", "shadow", "offset", "blurSigma"):
    for m in list(re.finditer(kw, plain))[:8]:
        s = max(0, m.start() - 140)
        print("--- %s: %s" % (kw, plain[s:m.start() + 200]))
    print()

# enums page may document shadow
enums = pathlib.Path("tmp/run-20261011-01/_suite/docs/enums.html").read_text(
    encoding="utf-8")
ep = re.sub(r"<[^>]+>", " ", enums)
ep = re.sub(r"\s+", " ", ep)
for kw in ("shadow", "Shadow"):
    for m in list(re.finditer(kw, ep))[:5]:
        s = max(0, m.start() - 140)
        print("=== enums %s: %s" % (kw, ep[s:m.start() + 200]))

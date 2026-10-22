# -*- coding: utf-8 -*-
import pathlib
import re

base = pathlib.Path("tmp/run-20261011-01/_suite/docs")
for fn in ["parser-guide.html", "parser-tags.html", "ai-guide.md"]:
    raw = (base / fn).read_text(encoding="utf-8")
    if fn.endswith(".md"):
        text = raw
    else:
        text = re.sub(r"<[^>]+>", " ", raw)
        text = re.sub(r"\s+", " ", text)
    for kw in ["PARSE_ERROR", "Retry-After", "X-Request-Id", "requestId",
               "errorImage", "credentials", "rate limit", "限流", "429",
               "401", "fonts", "root", "第一个开始标签"]:
        k = text.find(kw)
        if k >= 0:
            print(f"--- {fn} | {kw} @ {k} ---")
            print(text[max(0, k - 200):k + 300].strip()[:480])
            print()

# -*- coding: utf-8 -*-
import pathlib
import re

html = pathlib.Path("tmp/run-20261011-01/_suite/docs/parser-tags.html").read_text(
    encoding="utf-8")
text = re.sub(r"<[^>]+>", " ", html)
text = re.sub(r"\s+", " ", text)
i = text.find("SizedBo", 19853)
print("=== Expanded example region ===")
print(text[20100:20400])
print()
# Row/Column section attributes
j = text.find("Row", 19273)
print("=== Row/Column section ===")
print(text[19273:19790])
print()
# error handling section (page1 citation)
for kw in ["PARSE_ERROR", "Retry-After", "X-Request-Id", "requestId",
           "errorImage", "text/plain"]:
    k = text.find(kw)
    if k >= 0:
        print(f"=== {kw} @ {k} ===")
        print(text[max(0, k - 160):k + 240])
        print()

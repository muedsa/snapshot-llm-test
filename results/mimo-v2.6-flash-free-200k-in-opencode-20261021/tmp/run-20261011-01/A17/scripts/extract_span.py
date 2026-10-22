# -*- coding: utf-8 -*-
import pathlib
import re

html = pathlib.Path("tmp/run-20261011-01/_suite/docs/parser-tags.html").read_text(
    encoding="utf-8")
text = re.sub(r"<[^>]+>", " ", html)
text = re.sub(r"\s+", " ", text)
for kw in ["Span Section", "TextSpan", "可以嵌套行内", "RichText Section",
           "fontStyle", "color = \" #"]:
    k = text.find(kw)
    if k >= 0:
        print(f"--- {kw} @ {k} ---")
        print(text[k:k + 520])
        print()
# find a nested-span example
for m in re.finditer(r"< Span", text):
    i = m.start()
    print("--- < Span example @", i, "---")
    print(text[i:i + 360])
    print()
    break
for m in re.finditer(r"RichText", text):
    i = m.start()
    if i > 24000:
        print("--- RichText content @", i, "---")
        print(text[i:i + 400])
        print()
        break

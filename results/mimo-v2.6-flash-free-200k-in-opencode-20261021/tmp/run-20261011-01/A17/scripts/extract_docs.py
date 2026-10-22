# -*- coding: utf-8 -*-
"""Extract filter + Raw/RichText/CDATA semantics from cached parser docs."""
import pathlib
import re

html = pathlib.Path("tmp/run-20261011-01/_suite/docs/parser-tags.html").read_text(
    encoding="utf-8")
text = re.sub(r"<[^>]+>", " ", html)
text = re.sub(r"\s+", " ", text)

# locate the drawing/effects section (filters) and text section
for anchor in ["ColorFilter", "ImageFilter", "BackdropFilter", "blur(",
               "saturate", "grayscale", "invert", "matrix", "Raw", "RichText",
               "CDATA", "TextSpan", "textScaleFactor", "softWrap", "overflow"]:
    for m in re.finditer(re.escape(anchor), text):
        idx = m.start()
        snippet = text[idx:idx + 280]
        # only print if it looks like a doc section (contains Chinese + props)
        if "Section titled" in text[max(0, idx - 40):idx + 60] or \
           "默认" in snippet or "属性" in snippet or "filter" in snippet.lower():
            print(f"===== {anchor} @ {idx} =====")
            print(snippet)
            print()
            break

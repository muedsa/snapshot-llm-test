# -*- coding: utf-8 -*-
"""Pull the real widget API sections for filters + RichText + CDATA."""
import pathlib
import re

html = pathlib.Path("tmp/run-20261011-01/_suite/docs/parser-tags.html").read_text(
    encoding="utf-8")
text = re.sub(r"<[^>]+>", " ", html)
text = re.sub(r"\s+", " ", text)

# The real sections appear AFTER the sidebar (sidebar ~< 12000). Search >12000.
def find_sections(kw, start=12000):
    out = []
    for m in re.finditer(re.escape(kw), text):
        if m.start() >= start:
            out.append(m.start())
    return out


for kw in ["ImageFiltered", "ColorFiltered", "BackdropFilter", "Opacity",
           "RichText", "TextSpan", "WidgetSpan", "Raw", "blur", "saturate",
           "grayscale", "invert"]:
    idxs = find_sections(kw)
    if idxs:
        i = idxs[0]
        print(f"===== {kw} @ {i} =====")
        print(text[i:i + 420])
        print()

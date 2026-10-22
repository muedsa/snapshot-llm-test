# -*- coding: utf-8 -*-
import pathlib
import re

html = pathlib.Path("tmp/run-20261011-01/_suite/docs/parser-tags.html").read_text(
    encoding="utf-8")
text = re.sub(r"<[^>]+>", " ", html)
text = re.sub(r"\s+", " ", text)

# ImageFiltered / ColorFiltered / BackdropFilter attribute tables
for kw in ["ImageFiltered Section titled", "ColorFiltered Section titled",
           "BackdropFilter Section titled", "RichText Section titled"]:
    i = text.find(kw)
    if i >= 0:
        print(f"===== {kw} =====")
        print(text[i:i+600])
        print()

# RichText attributes - find the Text/RichText widget API region
for kw in ["RichText", "textScale", "maxLines", "TextSpan", "style="]:
    for m in re.finditer(re.escape(kw), text):
        i = m.start()
        if i > 20000:  # real content
            print(f"===== {kw} @ {i} =====")
            print(text[i:i+300])
            print()
            break

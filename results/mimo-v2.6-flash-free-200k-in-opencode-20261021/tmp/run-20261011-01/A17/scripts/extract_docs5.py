# -*- coding: utf-8 -*-
import pathlib
import re

html = pathlib.Path("tmp/run-20261011-01/_suite/docs/parser-tags.html").read_text(
    encoding="utf-8")
text = re.sub(r"<[^>]+>", " ", html)
text = re.sub(r"\s+", " ", text)

# find the ImageFiltered section by locating its attribute table near sigma
i = text.find("sigmaX")
print("=== ImageFiltered region (around first sigmaX) ===")
print(text[i-200:i+500])
print()

# ColorFiltered: find its attribute table
for m in re.finditer("ColorFiltered", text):
    j = m.start()
    seg = text[j:j+400]
    if "blendMode" in seg and "color" in seg and j > 13000:
        print("=== ColorFiltered region @", j, "===")
        print(seg)
        print()
        break

# RichText region: find "RichText" with style/span context
for m in re.finditer("RichText", text):
    j = m.start()
    seg = text[j:j+400]
    if ("span" in seg.lower() or "style" in seg) and j > 20000:
        print("=== RichText region @", j, "===")
        print(seg)
        print()
        break

# CDATA
i = text.find("CDATA")
if i>=0:
    print("=== CDATA @", i, "===")
    print(text[i-100:i+300])

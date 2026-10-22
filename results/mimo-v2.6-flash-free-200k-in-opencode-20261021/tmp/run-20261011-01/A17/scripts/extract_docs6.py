# -*- coding: utf-8 -*-
"""Extract Row/Expanded, RichText/TextSpan, BackdropFilter real syntax."""
import pathlib
import re

base = pathlib.Path("tmp/run-20261011-01/_suite/docs")
for fn in ["parser-tags.html", "parser-guide.html", "enums.html"]:
    html = (base / fn).read_text(encoding="utf-8")
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    for kw in ["BackdropFilter", "RichText", "TextSpan", "Expanded",
               "mainAxisSize", "flex", "blendMode", "Grayscale", "invert"]:
        hits = [m.start() for m in re.finditer(re.escape(kw), text)]
        for i in hits:
            seg = text[i:i + 320]
            if i > 13000 and ("=" in seg) and (
                    "sigma" in seg or "span" in seg.lower() or "flex" in seg
                    or "blendMode" in seg or "Row" in seg or "text=" in seg):
                print(f"==== {fn} | {kw} @ {i} ====")
                print(seg)
                print()
                break

# -*- coding: utf-8 -*-
import pathlib
import re

html = pathlib.Path("tmp/run-20261011-01/_suite/docs/parser-tags.html").read_text(
    encoding="utf-8")
text = re.sub(r"<[^>]+>", " ", html)
text = re.sub(r"\s+", " ", text)

# Look for the filter widget API detail sections (they have "sigma" / "filter")
for kw in ["sigma", "ColorFilter Section", "ImageFilter Section",
           "filter=", "filter ", "ColorFiltered Section",
           "ImageFiltered Section titled", "BackdropFilter Section titled"]:
    for m in re.finditer(re.escape(kw), text):
        i = m.start()
        snip = text[i:i+360]
        if "sigma" in snip or "filter" in snip.lower():
            print(f"===== {kw} @ {i} =====")
            print(snip)
            print()
            break

# also grep for 'filter' attribute occurrences with context
print("########## filter= contexts ##########")
for m in re.finditer(r'filter', text):
    i = m.start()
    ctx = text[max(0,i-60):i+120]
    if 'sigma' in ctx or 'blur' in ctx or 'grayscale' in ctx or 'saturate' in ctx or 'ColorMatrix' in ctx or 'matrix' in ctx.lower():
        print(f"@{i}: ...{ctx}...")
        print()

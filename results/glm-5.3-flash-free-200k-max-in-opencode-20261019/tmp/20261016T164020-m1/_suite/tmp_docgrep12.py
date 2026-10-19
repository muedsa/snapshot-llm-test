# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import re, os
DOC = "tmp/20261016T164020-m1/docs"
for fn in ("parser-text.txt", "parser-tags.txt", "painting.txt"):
    p = os.path.join(DOC, fn)
    if not os.path.exists(p):
        continue
    t = open(p, encoding="utf-8").read()
    for a, b in (("&#x3C;", "<"), ("&#34;", '"'), ("&quot;", '"'), ("&lt;", "<"), ("&gt;", ">"), ("&amp;", "&")):
        t = t.replace(a, b)
    hits = [m.start() for m in re.finditer(r"(?:height|lineHeight|行高|maxLines|overflow|strut)", t)]
    seen = set()
    shown = 0
    for i in hits:
        key = i // 400
        if key in seen:
            continue
        seen.add(key)
        if any(k in t[max(0, i - 200):i + 240] for k in ("Text", "行", "maxLines", "height")):
            print("=====", fn, "@", i)
            print(t[max(0, i - 260):i + 300].replace("\n\n", "\n"))
            shown += 1
        if shown > 7:
            break

# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
t = open("tmp/20261016T164020-m1/docs/parser-tags.txt", encoding="utf-8").read()
for a, b in [("&#x3C;", "<"), ("&#34;", '"'), ("&quot;", '"'), ("&lt;", "<"), ("&gt;", ">"), ("&amp;", "&")]:
    t = t.replace(a, b)
i = t.find("Snapshot")  # 标签定义段
while i != -1:
    seg = t[max(0, i - 100):i + 700]
    if "background" in seg and ("透明" in seg or "transparent" in seg.lower() or "默认" in seg):
        print("=====@ ", i)
        print(seg)
        break
    i = t.find("Snapshot", i + 1)

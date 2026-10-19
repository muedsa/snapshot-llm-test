# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "tmp/20261016T164020-m1/docs/"
t = open(BASE + "parser-text.txt", encoding="utf-8").read()
for a, b in [("&#x3C;", "<"), ("&#34;", '"'), ("&quot;", '"'), ("&lt;", "<"), ("&gt;", ">"), ("&amp;", "&")]:
    t = t.replace(a, b)
for kw in ["Span 参数", "Span 属性", "行内 Span", "<Span", "Span 标签", "backgroundColor"]:
    i = t.find(kw)
    print("=====", kw, "@", i)
    if i != -1:
        print(t[max(0, i - 200):i + 900])
pt = open(BASE + "parser-tags.txt", encoding="utf-8").read()
for a, b in [("&#x3C;", "<"), ("&#34;", '"'), ("&quot;", '"'), ("&lt;", "<"), ("&gt;", ">"), ("&amp;", "&")]:
    pt = pt.replace(a, b)
i = pt.find("Raw")
while i != -1 and i < 20000:
    seg = pt[i - 150:i + 120]
    if "保留空白" in seg:
        print("===== tags Raw @", i)
        print(seg)
        break
    i = pt.find("Raw", i + 1)

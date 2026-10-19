# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
t = open("tmp/20261016T164020-m1/docs/parser-tags.txt", encoding="utf-8").read()
t = t.replace("&#x3C;", "<").replace("&#34;", "\"").replace("&quot;", "\"").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
seen = set()
for kw in ["ColorFiltered", "ImageFiltered", "BackdropFilter", "ClipRRect", "Opacity", "boxShadow"]:
    i = t.find(kw)
    while i != -1:
        seg = t[max(0, i - 150):i + 950]
        print("=====", kw, "@", i)
        print(seg)
        print()
        i = t.find(kw, i + 950)

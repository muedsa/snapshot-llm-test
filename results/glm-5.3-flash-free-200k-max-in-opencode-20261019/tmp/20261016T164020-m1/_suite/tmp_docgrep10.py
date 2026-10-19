# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "tmp/20261016T164020-m1/docs/"
t = open(BASE + "parser-tags.txt", encoding="utf-8").read()
for a, b in [("&#x3C;", "<"), ("&#34;", '"'), ("&quot;", '"'), ("&lt;", "<"), ("&gt;", ">"), ("&amp;", "&")]:
    t = t.replace(a, b)
i = t.find("ClipPath")
n = 0
while i != -1 and n < 4:
    seg = t[max(0, i - 200):i + 900]
    if "path" in seg and ("轮廓" in seg or "clip" in seg.lower()):
        print("===== @", i)
        print(seg)
        n += 1
    i = t.find("ClipPath", i + 1)
pt = open(BASE + "painting.txt", encoding="utf-8").read()
for a, b in [("&#x3C;", "<"), ("&#34;", '"'), ("&quot;", '"'), ("&lt;", "<"), ("&gt;", ">"), ("&amp;", "&")]:
    pt = pt.replace(a, b)
j = pt.find("clipRule")
if j == -1:
    j = pt.find("多轮廓")
print("===== painting clip @", j)
print(pt[max(0, j - 300):j + 800])

# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "tmp/20261016T164020-m1/docs/"
for fn in ["media-text.txt", "parser-text.txt", "concepts.txt", "widgets.txt"]:
    t = open(BASE + fn, encoding="utf-8").read()
    for a, b in [("&#x3C;", "<"), ("&#34;", '"'), ("&quot;", '"'), ("&lt;", "<"), ("&gt;", ">"), ("&amp;", "&")]:
        t = t.replace(a, b)
    i = 0
    n = 0
    print("#####", fn)
    while n < 3:
        i = t.find("<Span", i)
        if i == -1:
            print("(no <Span>)")
            break
        print(t[max(0, i - 260):i + 480].replace("\n\n", "\n"))
        print("-----")
        i += 400
        n += 1

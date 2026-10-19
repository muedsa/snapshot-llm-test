# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "tmp/20261016T164020-m1/docs/"
p = open(BASE + "painting.txt", encoding="utf-8").read()
p = p.replace("&#x3C;", "<").replace("&#34;", '"').replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
q = open(BASE + "faq.txt", encoding="utf-8").read()
q = q.replace("&#x3C;", "<").replace("&#34;", '"').replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
w = open(BASE + "widgets.txt", encoding="utf-8").read()
w = w.replace("&#x3C;", "<").replace("&#34;", '"').replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

def show(tag, text, kw, n=2, span=640, back=120):
    print("#####", tag)
    i = 0
    for _ in range(n):
        i = text.find(kw, i)
        if i == -1:
            break
        print("--- @", i)
        print(text[max(0, i - back):i + span])
        i += span

show("painting BackdropFilter", p, "BackdropFilter", 2, 620)
show("painting ImageFiltered", p, "ImageFiltered", 1, 700)
show("painting ColorFilter", p, "ColorFilter", 1, 700)
show("faq Opacity", q, "Opacity", 2, 500)
show("widgets Opacity", w, "Opacity", 1, 400)

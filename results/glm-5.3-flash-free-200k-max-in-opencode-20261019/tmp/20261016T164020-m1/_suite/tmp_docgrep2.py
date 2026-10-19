# -*- coding: utf-8 -*-
"""抓取 docs 缓存中四个效果标签/颜色格式的原文段落，供 visual_checks 引用。"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "tmp/20261016T164020-m1/docs/"
t = open(BASE + "parser-tags.txt", encoding="utf-8").read()
t = t.replace("&#x3C;", "<").replace("&#34;", '"').replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
p = open(BASE + "painting.txt", encoding="utf-8").read()
p = p.replace("&#x3C;", "<").replace("&#34;", '"').replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

def show(name, text, kw, n=2, span=520):
    print("#####", name)
    i = 0
    hits = 0
    while hits < n:
        i = text.find(kw, i)
        if i == -1:
            break
        print("--- hit@", i)
        print(text[max(0, i - 100):i + span].replace("\n", "\n")[:620])
        i += span
        hits += 1

show("parser-tags: BackdropFilter", t, "BackdropFilter", 1, 700)
show("parser-tags: ImageFiltered", t, "ImageFiltered", 1, 700)
show("parser-tags: ColorFiltered", t, "ColorFiltered", 1, 700)
show("parser-tags: Opacity", t, "Opacity ", 1, 500)
show("parser-tags: 颜色 8位", t, "最后一组是透明度", 1, 400)
show("painting: 透明间隙着色", p, "透明间隙", 2, 500)
show("painting: 混合模式 multiply", p, "MULTIPLY", 1, 400)

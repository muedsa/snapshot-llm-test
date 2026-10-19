# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "tmp/20261016T164020-m1/docs/"

def load(fn):
    t = open(BASE + fn, encoding="utf-8").read()
    for a, b in [("&#x3C;", "<"), ("&#34;", '"'), ("&quot;", '"'), ("&lt;", "<"), ("&gt;", ">"), ("&amp;", "&")]:
        t = t.replace(a, b)
    return t

def show(tag, text, kws, span=760, back=120):
    print("#####", tag)
    for kw in kws:
        i = text.find(kw)
        if i == -1:
            print("--- no hit:", kw)
            continue
        print("--- @", i, "kw:", kw)
        print(text[max(0, i - back):i + span])

pt = load("parser.txt")
show("parser.txt CDATA/转义", pt, ["CDATA", "转义"], 3)
pe = load("parser-errors.txt")
show("parser-errors CDATA/转义/实体", pe, ["CDATA", "转义", "实体"], 2)
q = load("faq.txt")
show("faq 实体", q, ["实体"], 1, 500)
tg = load("parser-text.txt")
show("parser-text Raw", tg, ["<Raw", "Raw"], 2, 700)
ex = load("examples.txt")
show("examples CDATA/实体", ex, ["CDATA", "实体"], 1, 600)

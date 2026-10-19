# -*- coding: utf-8 -*-
import io, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "tmp/20261016T164020-m1/docs/"
for kw in ["转义", "CDATA", "实体", "XML", "非法字符", "&amp", "Raw", "textRaw", "literal"]:
    for f in sorted(glob.glob(BASE + "*.txt")):
        t = open(f, encoding="utf-8").read()
        n = t.count(kw)
        if n:
            print("%-10s %-22s x%d" % (kw, f.split("\\")[-1], n))

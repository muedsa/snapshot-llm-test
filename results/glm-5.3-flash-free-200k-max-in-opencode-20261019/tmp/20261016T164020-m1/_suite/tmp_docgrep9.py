# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "tmp/20261016T164020-m1/docs/"
t = open(BASE + "parser-text.txt", encoding="utf-8").read()
i = t.find("fontFeatures")
while i != -1:
    print("--- @", i)
    print(t[max(0, i - 420):i + 260].replace("\n\n", "\n"))
    i = t.find("fontFeatures", i + 500)
    if i > 6000:
        break

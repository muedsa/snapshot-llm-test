# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
p = "tmp/20261016T164020-m1/A10/iterations.jsonl"
t = open(p, encoding="utf-8").read()
t = t.replace("glass() 颜色 #60?? → #FFFFFF59", "glass() 颜色 #B3FFFFFF→#FFFFFF59（白 35%；此前两值实为不透明青色）")
open(p, "w", encoding="utf-8").write(t)
print("patched")

# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
p = "tmp/20261016T164020-m1/A17/build_pages.py"
t = open(p, encoding="utf-8").read()
a = 'mk_mid="…… 行 17–20 省略：定位文本标注（毛玻璃说明）……"'
b = 'mk_mid="…… 行 17–21 省略：毛玻璃说明标题及上级容器 ……"'
print("count", t.count(a))
t = t.replace(a, b)
open(p, "w", encoding="utf-8").write(t)

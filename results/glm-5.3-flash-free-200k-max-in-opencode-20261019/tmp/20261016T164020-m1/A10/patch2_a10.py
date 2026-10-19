# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
p = "tmp/20261016T164020-m1/A10/build_a10.py"
t = open(p, encoding="utf-8").read()
n0 = t.count("#0000003A")
t = t.replace("#0000003A", "#00000055")
open(p, "w", encoding="utf-8").write(t)
print("patched #0000003A x", n0, "-> #00000055")

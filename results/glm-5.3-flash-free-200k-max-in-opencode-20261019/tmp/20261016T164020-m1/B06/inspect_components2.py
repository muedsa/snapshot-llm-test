# -*- coding: utf-8 -*-
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = Path(r"D:\mine\test\glm-5.3-flash\tmp\20261016T164020-m1\B05\b05_common.py").read_text(encoding="utf-8")
i = c.find("def person")
print(c[i:i + 900])
print("=== wrap_dsl ===")
j = c.find("def wrap_dsl")
print(c[j:j + 900])

# -*- coding: utf-8 -*-
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
t = Path(r"D:\mine\test\glm-5.3-flash\outputs\20261016T164020-m1\B05\case-02\final.snapshot").read_text(encoding="utf-8")
for line in t.splitlines():
    if re.search(r'radius="[0-9]{2,}"|<Ellipse|<Circle|<Poly', line):
        print(line[:200])
print("---- sample_curve impl ----")
c = Path(r"D:\mine\test\glm-5.3-flash\tmp\20261016T164020-m1\B05\b05_common.py").read_text(encoding="utf-8")
i = c.find("def sample_curve")
print(c[i:i + 800])

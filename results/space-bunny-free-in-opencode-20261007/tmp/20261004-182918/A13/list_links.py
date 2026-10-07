# -*- coding: utf-8 -*-
import io
import os
import re
import sys

p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
s = io.open(os.path.join(p, "index.html"), encoding="utf-8").read()
hrefs = sorted(set(re.findall(r'href="(/[^"#]+)"', s)))
print("index links:", len(hrefs))
for h in hrefs:
    print("  ", h)
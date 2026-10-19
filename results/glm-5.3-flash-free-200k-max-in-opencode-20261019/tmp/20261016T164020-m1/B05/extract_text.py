# -*- coding: utf-8 -*-
"""抽取 final.snapshot 内全部 text= 文案，供 case.md 与内容核对。"""
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
OUT = Path(r"D:\mine\test\glm-5.3-flash\outputs\20261016T164020-m1\B05")
for i in range(1, 11):
    cs = "case-%02d" % i
    t = (OUT / cs / "final.snapshot").read_text(encoding="utf-8")
    strs = re.findall(r"<Text[^>]*>([^<]+)</Text>", t)
    print("==== " + cs + " ====")
    for s in strs:
        print("  |", s)

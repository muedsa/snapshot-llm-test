#!/usr/bin/env python
"""打印 B05 第 10 件里「贴片只通过蓝牙…」那段所在的上下文，确认该用哪个 y 变量。"""
from pathlib import Path

s = (Path(__file__).parent / "cases_b05b.py").read_text(encoding="utf-8")
key = "贴片只通过蓝牙"
i = s.index(key)
start = s.rfind("def ", 0, i)
print(s[start:i - 400][-1100:])
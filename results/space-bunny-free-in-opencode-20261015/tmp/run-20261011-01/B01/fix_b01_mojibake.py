#!/usr/bin/env python
# 一次性修补：deliver_b01.py 里 case-09 的文案混入了两个 U+FFFD 替换字符。
# 启动基准：总任务根 (suite_root)。用法：python fix_b01_mojibake.py
from pathlib import Path

p = Path(__file__).with_name("deliver_b01.py")
s = p.read_text(encoding="utf-8")
bad = "警戒/关闭两段一\ufffd\ufffd分得清。"
good = "警戒与关闭两段一分得清。"
assert bad in s, "pattern not found"
p.write_text(s.replace(bad, good), encoding="utf-8")
print("mojibake fixed")
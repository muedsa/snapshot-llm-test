#!/usr/bin/env python
# 一次性补丁：case06 里超出容量的空槽用了非法颜色 "0A"，改为合法的 #0B1220。
# 启动基准：总任务根 (suite_root)。用法：python patch_b01_c6b.py
from pathlib import Path

p = Path(__file__).with_name("cases_b01_b.py")
s = p.read_text(encoding="utf-8")
old = 'col + ("66" if occupied else "18") if within else "0A",'
new = '(col + ("66" if occupied else "18")) if within else "#0B1220",'
assert old in s, "pattern not found"
p.write_text(s.replace(old, new), encoding="utf-8")
print("case06 color fixed")
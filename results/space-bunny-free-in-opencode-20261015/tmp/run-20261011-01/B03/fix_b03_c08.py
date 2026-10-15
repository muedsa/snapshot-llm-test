#!/usr/bin/env python
# B03 第 08 件修正：柱高最高到 y≈310，穿过了右上角的曲线章面。
# 把柱高比例从「占 420px」压到「每公里 8px」（最高 34.2 → 274px，柱顶 446），
# 章面上移到 100–390，三者互不相交。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_c08.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")
subs = [
    ("        h = km / 35.0 * 420",
     "        h = km * 8.0        # 首版最高柱到 y≈310，穿过了右上角的章面"),
    ("b.append('<Positioned left=\"640\" top=\"120\" width=\"300\" height=\"300\">'",
     "b.append('<Positioned left=\"640\" top=\"100\" width=\"300\" height=\"290\">'"),
    ('b.append(txt("4", 700, 200, 180, None, 120, "#4ADE80", W600,\n                 align="CENTER"))',
     'b.append(txt("4", 700, 186, 180, None, 120, "#4ADE80", W600,\n                 align="CENTER"))'),
    ('b.append(txt("天达标", 700, 330, 180, None, 26, "#6FA07F", align="CENTER"))',
     'b.append(txt("天达标", 700, 316, 180, None, 26, "#6FA07F", align="CENTER"))'),
]
missing = [a for a, _ in subs if a not in s]
for a, bb in subs:
    s = s.replace(a, bb)
p.write_text(s, encoding="utf-8")
print("applied", len(subs) - len(missing), "of", len(subs))
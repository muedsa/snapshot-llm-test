# -*- coding: utf-8 -*-
"""A01 v04 补丁：小图内部注记 16px -> 18px，月份基线微调。"""
from pathlib import Path
p = Path(__file__).resolve().parent / "build_a01.py"  # 本补丁与 build_a01.py 同目录
s = p.read_text(encoding="utf-8")
pairs = [
    ('sep(g), 16, MUT, family=FONT_NUM, align="END"', 'sep(g), 18, MUT, family=FONT_NUM, align="END"'),
    ('f"{g}%", 16, MUT, family=FONT_NUM, align="END"', 'f"{g}%", 18, MUT, family=FONT_NUM, align="END"'),
    ('sep(m["sessions"]), 16, "#C8F5E4"', 'sep(m["sessions"]), 18, "#C8F5E4"'),
    ("f\"{m['conversion'] * 100:.2f}%\", 16, \"#C8F5E4\"", "f\"{m['conversion'] * 100:.2f}%\", 18, \"#C8F5E4\""),
    ('m["month"][5:7] + "月", 16, MUT', 'm["month"][5:7] + "月", 18, MUT'),
    ('p2_bot + 5, m["month"][5:7]', 'p2_bot + 4, m["month"][5:7]'),
]
for old, new in pairs:
    if old not in s:
        print("WARN not found:", old)
        continue
    s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("patched ok")

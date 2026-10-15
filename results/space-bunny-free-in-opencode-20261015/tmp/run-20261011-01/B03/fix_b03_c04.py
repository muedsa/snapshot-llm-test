#!/usr/bin/env python
# B03 第 04 件修正：
#   · #0E0E1244 的压暗层把扇形渐变压成了灰扑扑的粉彩，失去了唱片该有的鲜艳
#     → 压暗层减到 1A，靠白色同心线提结构。
#   · SWEEP 的 gradientCenter 只能给对齐常量，没法把中心挪到 (500,440)，
#     所以唱片中心回到画布正中 (500,500)，和渐变中心对齐。
#   · 中心圆半径 150 装不下 "ROTATION"，文字被黑圆边缘切掉 → 放大到 176 并缩字。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_c04.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")
subs = [
    ('b.append(rect(0, 0, 1000, 1000, "#0E0E1244"))',
     'b.append(rect(0, 0, 1000, 1000, "#0E0E121A"))'),
    ("        rr = 90 + i * 13\n        b.append(circle(500, 440, rr * 2, None, border=\"1 SOLID #FFFFFF22\"))",
     "        rr = 110 + i * 13\n        b.append(circle(500, 500, rr * 2, None, border=\"1 SOLID #FFFFFF33\"))"),
    ("b.append(circle(500, 440, 150, \"#0E0E12\"))\n"
     "    b.append(circle(500, 440, 150, None, border=\"3 SOLID #FFFFFF66\"))\n"
     "    b.append(circle(500, 440, 26, \"#FFFFFF22\"))\n"
     "    b.append(txt(\"SLOW\", 400, 418, 200, None, 40, INK, W600, align=\"CENTER\"))\n"
     "    b.append(txt(\"ROTATION\", 372, 460, 256, None, 24, \"#9AA0AA\", align=\"CENTER\"))",
     "b.append(circle(500, 500, 182, \"#0E0E12\"))\n"
     "    b.append(circle(500, 500, 182, None, border=\"3 SOLID #FFFFFF88\"))\n"
     "    b.append(circle(500, 500, 22, \"#FFFFFF33\"))\n"
     "    b.append(txt(\"SLOW\", 380, 466, 240, None, 44, INK, W600, align=\"CENTER\"))\n"
     "    b.append(txt(\"ROTATION\", 372, 518, 256, None, 22, \"#9AA0AA\", align=\"CENTER\"))"),
    ('b.append(txt("慢转 · 33⅓", 80, 840, 600, None, 54, INK, W600))',
     'b.append(txt("慢转 · 33⅓", 80, 812, 600, None, 54, INK, W600))'),
    ('b.append(txt("厂牌 夜潮唱片", 80, 80, 500, None, 24, "#FFB03B"))',
     'b.append(txt("厂牌 夜潮唱片", 80, 76, 500, None, 24, "#1A1A1E"))'),
    ('b.append(txt("NT-017 · 2026 夏", 80, 910, 600, None, 26, "#9AA0AA"))',
     'b.append(txt("NT-017 · 2026 夏", 80, 878, 600, None, 26, "#1A1A1EF0"))'),
    ('b.append(txt("12 吋 · 透明橙胶", 640, 912, 280, None, 22, "#9AA0AA",\n                 align="END"))',
     'b.append(txt("12 吋 · 透明橙胶", 640, 880, 280, None, 22, "#1A1A1ED0",\n                 align="END"))'),
    ('footer(b, 80, 954, 840, "封套设计稿；厂牌与编号为示例")',
     'footer(b, 80, 928, 840, "封套设计稿；厂牌与编号为示例", dark=False)'),
]
missing = [a for a, _ in subs if a not in s]
for a, bb in subs:
    s = s.replace(a, bb)
p.write_text(s, encoding="utf-8")
print("applied", len(subs) - len(missing), "of", len(subs), "missing:", missing[:1])
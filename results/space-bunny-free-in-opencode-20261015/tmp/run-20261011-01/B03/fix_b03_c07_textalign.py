#!/usr/bin/env python
# c07 服务返回 400：Attr [textAlign] value is invalid:
# No enum constant org.jetbrains.skia.paragraph.Alignment.MIDDLE。
# textAlign 只接受 START/CENTER/END/JUSTIFY/LEFT/RIGHT，是**水平**对齐，
# 没有「垂直居中」这个值。改成给固定宽度的盒子 + CENTER，手算好盒子的 x/y。
# 同时把「南」从 GY+R+12(842) 上移到 GY+R-6(824)，避免压到 840 的页脚横线；
# 「北」从 -R-34(176) 上移到 -R-30(180)，让开标题下沿 160。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_c07_textalign.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")
old = '''    for lbl, dx, dy, anc in (("北", 0, -R - 34, "MIDDLE"),
                             ("南", 0, R + 12, "MIDDLE"),
                             ("东", R + 12, 0, "MIDDLE"),
                             ("西", -R - 66, 0, "MIDDLE")):
        b.append(txt(lbl, GX + dx - 33, GY + dy - 13, 66, None, 22,
                     "#A8937A", align=anc))'''
new = '''    # textAlign 只有 START/CENTER/END/JUSTIFY/LEFT/RIGHT，是水平对齐；
    # 没有 MIDDLE。这里给 66px 的盒子 + CENTER，盒子的 x/y 手工居中。
    for lbl, bx, by in (("北", GX - 33, GY - R - 43),
                        ("南", GX - 33, GY + R - 19),
                        ("东", GX + R - 21, GY - 13),
                        ("西", GX - R - 99, GY - 13)):
        b.append(txt(lbl, bx, by, 66, None, 22, "#A8937A", align="CENTER"))'''
assert s.count(old) == 1
p.write_text(s.replace(old, new), encoding="utf-8")
print("c07 compass fixed")
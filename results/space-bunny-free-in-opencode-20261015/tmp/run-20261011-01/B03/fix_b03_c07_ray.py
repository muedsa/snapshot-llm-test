#!/usr/bin/env python
# c07 续修：方向对齐后，橙色入射射线**完全看不见**了。
# 原因：我把射线也画在 +u 侧，而投影带（148→148+shl）正好画在同一条轴上、
# 且后画，把 150–300 的射线整段盖住了。
# 物理上太阳在影子��**反方向**：u 是背阳方向，所以入射射线要画在 −u 侧
# （从 −300u 射向楼体外缘 −148u）。这样两者在楼体两侧，一眼能看懂。
# 时刻标签跟着改挂到射线末端 r=300。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_c07_ray.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")

old = '''        # 入射光线：从楼体外缘往里指（仅示意，用短箭头段）
        b.append(segment(GX + 150 * ux, GY + 150 * uy,
                         GX + 300 * ux, GY + 300 * uy, "#E8A33B", 3))'''
new = '''        # 入射射线在 **−u 侧**（太阳所在的一侧），投影在 +u 侧。
        # 首版两边都画在 +u，射线被后画的投影带整段盖住，图上完全看不到。
        b.append(segment(GX - 300 * ux, GY - 300 * uy,
                         GX - 148 * ux, GY - 148 * uy, "#E8A33B", 3))'''
assert s.count(old) == 1
s = s.replace(old, new)

old2 = '''        # 时刻标签挂在入射射线的末端（r=330），不再跟着投影带甩到圈外
        b.append(txt(lbl, GX + 330 * ux - 48, GY + 330 * uy - 13, 96, None,
                     21, "#8A6D3B", align="CENTER"))'''
new2 = '''        # 时刻标签挂在入射射线的末端（−u 方向 r=300），跟着射线走而不是投影带
        b.append(txt(lbl, GX - 300 * ux - 48, GY - 300 * uy - 13, 96, None,
                     21, "#8A6D3B", align="CENTER"))'''
assert s.count(old2) == 1
s = s.replace(old2, new2)
p.write_text(s, encoding="utf-8")
print("c07 rays moved to sun side")
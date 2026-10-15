#!/usr/bin/env python
# c07 修正（看图发现的几何错误）：
#   ① Transform 的 matrix 把盒子的局部 x 轴映到 (cosθ, sinθ)。我传 θ=az，
#      而投影方向 u=(-sin az, cos az) —— **两者差 90°**。
#      图上表现为灰蓝投影带与橙色入射光线**互相垂直**，与物理不符。
#      平面日照图里两者本来就共线（影子就在太阳的反方向）。
#      → 传 θ=az+90，使局部 x 轴正好落在 u 上。
#   ② 投影带以圆心为起点，而楼体对角线半径约 143px，把带子前半段盖住了，
#      09:00/15:00 只剩 130px 可见。→ 起点改为楼体外缘 bd=148。
#   ③ 时刻标签挂在投影带末端，会甩到圆圈外还压住「西侧…」文字
#      （那条文字还被静默裁成「复核平」）。→ 标签改挂在射线末端 r=330，
#      并把提示文字拆成两行、盒子给 300px。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_c07_geom.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")

old = '''        # 投影带：从楼体往背阳侧延伸
        b.append(f'<Positioned left="{GX - shl / 2:.1f}" top="{GY - 9:.1f}" '
                 f'width="{shl:.1f}" height="18">'
                 f'<Transform matrix="({_mat(az):s})" alignment="CENTER">'
                 f'<Container width="{shl:.1f}" height="18" color="#B8C4D0" '
                 f'opacity="0.85"/></Transform></Positioned>')
        # 时刻标签放在投影带的另一端，避开楼体
        lx, ly = GX + (shl + 42) * ux, GY + (shl + 42) * uy
        b.append(txt(lbl, lx - 48, ly - 13, 96, None, 21, "#8A6D3B",
                     align="CENTER"))'''
new = '''        # 投影带：从楼体外缘 bd 起、沿 u 延伸 shl。
        # 角度要传 az+90：matrix 把盒子局部 x 轴映到 (cosθ, sinθ)，
        # 要落在 u=(-sin az, cos az) 上必须 θ=az+90；首版传 az，差了 90°，
        # 图上投影带与入射光线互相垂直。
        bd = 148.0
        ccx, ccy = GX + (bd + shl / 2) * ux, GY + (bd + shl / 2) * uy
        b.append(f'<Positioned left="{ccx - shl / 2:.1f}" top="{ccy - 9:.1f}" '
                 f'width="{shl:.1f}" height="18">'
                 f'<Transform matrix="({_mat(az + 90):s})" alignment="CENTER">'
                 f'<Container width="{shl:.1f}" height="18" color="#B8C4D0" '
                 f'opacity="0.85"/></Transform></Positioned>')
        # 时刻标签挂在入射射线的末端（r=330），不再跟着投影带甩到圈外
        b.append(txt(lbl, GX + 330 * ux - 48, GY + 330 * uy - 13, 96, None,
                     21, "#8A6D3B", align="CENTER"))'''
assert s.count(old) == 1
s = s.replace(old, new)

old2 = '''    b.append(txt("西侧 2–4 层午后日照不足，需复核平面。", 64, 552, 380, None,
                 22, "#B0573A"))'''
new2 = '''    # 300px 的盒子在 22px 字号下只装得下约 13 个全角字，原先一行写完 18 个字
    # 会被**静默裁掉**末尾（渲染出来是「…需复核平」）。拆成两行。
    b.append(txt("西侧 2–4 层午后日照不足，", 64, 552, 300, None, 22, "#B0573A"))
    b.append(txt("需复核平面。", 64, 582, 300, None, 22, "#B0573A"))'''
assert s.count(old2) == 1
s = s.replace(old2, new2)
p.write_text(s, encoding="utf-8")
print("c07 geometry fixed")
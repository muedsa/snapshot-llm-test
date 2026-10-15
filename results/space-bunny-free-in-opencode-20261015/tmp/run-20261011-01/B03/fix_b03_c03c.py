#!/usr/bin/env python
# B03 第 03 件第二轮修正（看图发现）：
#   ① 右侧 24 行表从 y=276 起、行距 26 → 末行到 874，已顶到画布下沿；
#      而 y=704/734 的两行图例正好压在 08.5 / 09.0 两行上。
#      → 行距收成 24、起点提到 262（末行 814），两行图例并成一行放到 840。
#   ② 页脚在 H-60=840，横贯整个画布，穿过极坐标柔光方块（底 876）和表格末三行。
#      → 极坐标方块缩到 600×600（上 224 底 824），页脚只占左侧 700px，y 收到 H-46。
#   ③ 极坐标圆心随之上移到 524，各半径同比缩小，点与刻度都还在方块内。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_c03c.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")
subs = [
    ('    CX, CY = 430, 556', '    CX, CY = 430, 524'),
    ('b.append(\'<Positioned left="110" top="236" width="640" height="640">\'\n'
     '             \'<Container width="640" height="640" gradientType="RADIAL" \'',
     'b.append(\'<Positioned left="130" top="224" width="600" height="600">\'\n'
     '             \'<Container width="600" height="600" gradientType="RADIAL" \''),
    ('    b.append(circle(CX, CY, 292, "#5FD3E81A"))',
     '    b.append(circle(CX, CY, 274, "#5FD3E81A"))'),
    ('    for rr in (120, 200, 280):', '    for rr in (112, 186, 260):'),
    ('                         CX + 292 * math.sin(a), CY - 292 * math.cos(a),\n'
     '                         "#0B243088", 1))',
     '                         CX + 274 * math.sin(a), CY - 274 * math.cos(a),\n'
     '                         "#0B243088", 1))'),
    ('        b.append(txt(f"{k:02d}", CX + 308 * math.sin(a) - 26,\n'
     '                     CY - 308 * math.cos(a) - 13, 52, None, 18, "#7FB6C9",',
     '        b.append(txt(f"{k:02d}", CX + 292 * math.sin(a) - 26,\n'
     '                     CY - 292 * math.cos(a) - 13, 52, None, 18, "#7FB6C9",'),
    ('        r = 96 + 176 * (lv / 4.2)', '        r = 90 + 160 * (lv / 4.2)'),
    ('    b.append(circle(CX, CY, 96, "#071A22"))\n'
     '    b.append(circle(CX, CY, 96, None, border="2 SOLID #9BE8F5"))',
     '    b.append(circle(CX, CY, 90, "#071A22"))\n'
     '    b.append(circle(CX, CY, 90, None, border="2 SOLID #9BE8F5"))'),
    ('    b.append(txt("潮位", CX - 90, CY - 42, 180, None, 24, "#9BE8F5", W600,\n'
     '                 align="CENTER"))\n'
     '    b.append(txt("1.1 – 4.2 m", CX - 90, CY + 4, 180, None, 18, "#5FD3E8",\n'
     '                 align="CENTER"))',
     '    b.append(txt("潮位", CX - 86, CY - 40, 172, None, 24, "#9BE8F5", W600,\n'
     '                 align="CENTER"))\n'
     '    b.append(txt("1.1 – 4.2 m", CX - 86, CY + 4, 172, None, 18, "#5FD3E8",\n'
     '                 align="CENTER"))'),
    ('    b.append(txt("时刻", X0, 236, 110, None, 20, "#7FB6C9", W600))\n'
     '    b.append(txt("潮位", X0 + 110, 236, 100, None, 20, "#7FB6C9", W600))\n'
     '    b.append(txt("m", X0 + 218, 236, 78, None, 20, "#7FB6C9", W600,\n'
     '                 align="END"))\n'
     '    b.append(rect(X0, 264, 300, 1, "#1E4A5C"))',
     '    b.append(txt("时刻", X0, 224, 110, None, 20, "#7FB6C9", W600))\n'
     '    b.append(txt("潮位", X0 + 110, 224, 100, None, 20, "#7FB6C9", W600))\n'
     '    b.append(txt("m", X0 + 218, 224, 78, None, 20, "#7FB6C9", W600,\n'
     '                 align="END"))\n'
     '    b.append(rect(X0, 250, 300, 1, "#1E4A5C"))'),
    ('        y = 276 + i * 26', '        y = 262 + i * 24'),
    ('        b.append(txt(f"{h:04.1f}", X0, y, 110, None, 19, INK))\n'
     '        b.append(rect(X0 + 110, y + 7, 100, 10, "#0B4A5C", 5))\n'
     '        b.append(rect(X0 + 110, y + 7, 100 * lv / 4.2, 10,\n'
     '                      "#5FD3E8" if hi else "#1E6C86", 5))\n'
     '        b.append(txt(f"{lv:.1f}", X0 + 218, y, 78, None, 19,',
     '        b.append(txt(f"{h:04.1f}", X0, y, 110, None, 18, INK))\n'
     '        b.append(rect(X0 + 110, y + 6, 100, 9, "#0B4A5C", 5))\n'
     '        b.append(rect(X0 + 110, y + 6, 100 * lv / 4.2, 9,\n'
     '                      "#5FD3E8" if hi else "#1E6C86", 5))\n'
     '        b.append(txt(f"{lv:.1f}", X0 + 218, y, 78, None, 18,'),
    ('    b.append(txt("青色 = 高潮 ≥ 3.5 m", X0, 704, 300, None, 18, "#5FD3E8"))\n'
     '    b.append(txt("潮位越高，点离圆心越远。", X0, 734, 300, None, 18, "#4A7F93"))\n'
     '    footer(b, 64, H - 60, 1072, "预报为示例；潮位数据非实时")',
     '    b.append(txt("青色 = 高潮 ≥ 3.5 m · 潮位越高，点离圆心越远",\n'
     '                 X0, 838, 300, None, 17, "#5FD3E8"))\n'
     '    footer(b, 64, H - 44, 700, "预报为示例；潮位数据非实时")'),
]
missing = [a for a, _ in subs if a not in s]
for a, bb in subs:
    s = s.replace(a, bb)
p.write_text(s, encoding="utf-8")
print("applied", len(subs) - len(missing), "of", len(subs))
if missing:
    print("MISSING:", repr(missing[0][:110]))
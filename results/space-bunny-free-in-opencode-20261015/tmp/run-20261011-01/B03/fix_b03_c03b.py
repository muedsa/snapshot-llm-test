#!/usr/bin/env python
# B03 第 03 件重做。首版两处硬伤（都是看图才发现的）：
#   ① RADIAL 渐变的 Container 被 append 在**最后**，是不透明的 840×840 方块，
#      把标题、24 个潮位点、页脚全盖住了。→ 改成先画柔光底、���画数据。
#   ② 右侧表格的潮位值文字 rect(X0+168, w=76, align=END) 与最长 110px 的条重叠，
#      "3.9m / 4.2m" 直接压在条上。→ 重新分配三列的 x。
# 另外小时标签 24 个全排太挤且读序混乱，改为每 2 小时一个、顺时针。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_c03b.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")
start = s.index('    W, H = 1200, 900')
end = s.index('# ══════════════ 04 SWEEP 渐变')
new = '''    W, H = 1200, 900
    b = [rect(0, 0, W, H, "#071A22")]
    b.append(rect(0, 0, W, 172, "#0B2430"))
    b.append(txt("潮汐预报", 64, 36, 500, None, 26, "#5FD3E8"))
    b.append(txt("2026-07-18 · 望月", 64, 80, 700, None, 46, INK, W600))
    b.append(txt("高潮 21:07 · 4.2 m", 700, 46, 436, None, 30, "#5FD3E8",
                 align="END"))
    b.append(txt("低潮 15:22 · 1.1 m", 700, 96, 436, None, 26, "#4A7F93",
                 align="END"))

    CX, CY = 430, 556
    hours = [i * 0.5 for i in range(24)]
    levels = [1.6, 1.9, 2.3, 2.7, 3.1, 3.5, 3.9, 4.2, 4.1, 3.8, 3.4, 3.0,
              2.6, 2.2, 1.7, 1.4, 1.1, 1.2, 1.5, 1.9, 2.4, 2.9, 2.5, 2.0]
    # ① 先铺径向柔光底。它是不透明的，必须画在**所有数据之前**。
    #    gradientCenter 只能给对齐常量，所以把 Container 缩到正好盖住极坐标区再摆位。
    b.append('<Positioned left="110" top="236" width="640" height="640">'
             '<Container width="640" height="640" gradientType="RADIAL" '
             'gradientColors="#9BE8F5,#5FD3E8,#1E6C86" '
             'gradientStops="0,0.22,1" gradientCenter="CENTER" '
             'gradientRadius="0.72" gradientFocal="CENTER" '
             'gradientFocalRadius="0.22"/></Positioned>')
    b.append(circle(CX, CY, 292, "#5FD3E81A"))
    # ② 再画基准圈与小时刻度
    for rr in (120, 200, 280):
        b.append(circle(CX, CY, rr * 2, None, border=f"1 SOLID #0B243055"))
    for k in range(0, 24, 2):
        a = (k / 24) * math.tau - math.pi / 2
        b.append(segment(CX + 118 * math.sin(a), CY - 118 * math.cos(a),
                         CX + 292 * math.sin(a), CY - 292 * math.cos(a),
                         "#0B243088", 1))
        b.append(txt(f"{k:02d}", CX + 308 * math.sin(a) - 26,
                     CY - 308 * math.cos(a) - 13, 52, None, 18, "#7FB6C9",
                     align="CENTER"))
    # ③ 最后才是 24 个潮位点
    for h, lv in zip(hours, levels):
        a = (h / 24) * math.tau - math.pi / 2
        r = 96 + 176 * (lv / 4.2)
        x, y = CX + r * math.sin(a), CY - r * math.cos(a)
        hi = lv >= 3.5
        b.append(circle(x, y, 30, "#071A22"))
        b.append(circle(x, y, 26, "#9BE8F5" if hi else "#0B4A5C"))
    b.append(circle(CX, CY, 96, "#071A22"))
    b.append(circle(CX, CY, 96, None, border="2 SOLID #9BE8F5"))
    b.append(txt("潮位", CX - 90, CY - 42, 180, None, 24, "#9BE8F5", W600,
                 align="CENTER"))
    b.append(txt("1.1 – 4.2 m", CX - 90, CY + 4, 180, None, 18, "#5FD3E8",
                 align="CENTER"))

    # ④ 右侧逐时表：条 x=970 宽 100（最长到 1070），值右对齐 1082–1160，互不重叠
    X0 = 860
    b.append(txt("时刻", X0, 236, 110, None, 20, "#7FB6C9", W600))
    b.append(txt("潮位", X0 + 110, 236, 100, None, 20, "#7FB6C9", W600))
    b.append(txt("m", X0 + 218, 236, 78, None, 20, "#7FB6C9", W600,
                 align="END"))
    b.append(rect(X0, 264, 300, 1, "#1E4A5C"))
    for i, (h, lv) in enumerate(zip(hours, levels)):
        y = 276 + i * 26
        hi = lv >= 3.5
        b.append(txt(f"{h:04.1f}", X0, y, 110, None, 19, INK))
        b.append(rect(X0 + 110, y + 7, 100, 10, "#0B4A5C", 5))
        b.append(rect(X0 + 110, y + 7, 100 * lv / 4.2, 10,
                      "#5FD3E8" if hi else "#1E6C86", 5))
        b.append(txt(f"{lv:.1f}", X0 + 218, y, 78, None, 19,
                     "#5FD3E8" if hi else "#7FB6C9", align="END"))
    b.append(txt("青色 = 高潮 ≥ 3.5 m", X0, 704, 300, None, 18, "#5FD3E8"))
    b.append(txt("潮位越高，点离圆心越远。", X0, 734, 300, None, 18, "#4A7F93"))
    footer(b, 64, H - 60, 1072, "预报为示例；潮位数据非实时")
    return canvas(W, H, "".join(b), "#071A22")


'''
s = s[:start] + new + s[end:]
p.write_text(s, encoding="utf-8")
print("c03 rebuilt")
#!/usr/bin/env python
# B04-01 修正（看图发现三处）：
#   ① "年均距平（°C）" 在 x=20 宽 200，末到 220；"20 年滑动平均" 起点 108 → 两行文字
#      直接叠在一起。→ 左轴标签缩成「距平 °C」放最左，图例挪到绘图区右上方。
#   ② 极值标注用了 "全序列最低\n−0.48"，但 bsnap.txt **不处理 \n**，只渲染第一行，
#      图上只剩「全序列最低」「全序列最高」，数值整个丢了。→ 拆成两次 txt。
#   ③ 原本用引线把标注连到对应的柱子；1909 在左侧、2024 在最右，引线要横穿整张图。
#      改成左上角一个「极值」数据块（该区域在负值柱之上，本来就是空的），
#      不画引线，避免长线干扰读图。
# 启动基准：总任务根 (suite_root)。用法：python fix_b04_c01.py
from pathlib import Path

p = Path(__file__).parent / "build_b04.py"
s = p.read_text(encoding="utf-8")

old = '''    b.append(polyline([(PX + (i + 0.5) * slot, ty(v)) for i, v in enumerate(ma)],
                      INKD, 3))
    b.append(txt("20 年滑动平均", PX + 12, PY - 34, 220, None, 17, INKD, W600))
    for yr in range(1880, 2030, 20):
        i = yr - 1880
        if i < 0:
            continue
        b.append(txt(str(yr), PX + i * slot - 24, PY + PH + 12, 48, None, 16,
                     MUTE, align="CENTER"))
    b.append(txt("年均距平（°C）", PX - 76, PY - 34, 200, None, 17, MUTE))
    for yr, lab, dy in ((1909, "全序列最低\\n−0.48", -78), (2024, "全序列最高\\n+1.28", -78)):
        i = yr - 1880
        x = PX + (i + 0.5) * slot
        y = ty(D.JDN[i])
        b.append(segment(x, y, x, y + dy + 22, INKD, 1))
        b.append(txt(lab, x - 60, y + dy, 120, None, 17, INKD, W600, align="CENTER"))'''

new = '''    b.append(polyline([(PX + (i + 0.5) * slot, ty(v)) for i, v in enumerate(ma)],
                      INKD, 3))
    # 左轴标签放最左且缩短，图例挪到绘图区右上：原来两者起点分别是 20 和 108，
    # 在 108–220 这一段直接叠字。
    b.append(txt("距平 °C", 24, PY - 32, 120, None, 17, MUTE))
    b.append(segment(PX + PW - 250, PY - 24, PX + PW - 214, PY - 24, INKD, 3))
    b.append(txt("20 年滑动平均", PX + PW - 206, PY - 32, 206, None, 17, INKD,
                 W600))
    for yr in range(1880, 2030, 20):
        i = yr - 1880
        if i < 0:
            continue
        b.append(txt(str(yr), PX + i * slot - 24, PY + PH + 12, 48, None, 16,
                     MUTE, align="CENTER"))
    # 极值块：左侧负值柱之上是空的（1880–1970 全部为负），正好放数据块。
    # 不用引线——1909 在左、2024 在最右，引线要横穿整张图，反而干扰读图。
    lo_y, hi_y = D.YEARS.index(1909), D.YEARS.index(2024)
    b.append(rect(PX + 10, PY + 16, 372, 116, "#16191F08", 10))
    b.append(txt("极值", PX + 30, PY + 32, 200, None, 18, MUTE, W600))
    for k, (lb, yr, v, col) in enumerate((
            ("全序列最低", 1909, D.JDN[lo_y], SEA),
            ("全序列最高", 2024, D.JDN[hi_y], HEAT))):
        yy = PY + 58 + k * 38
        b.append(rect(PX + 30, yy + 8, 5, 22, col, 2))
        b.append(txt(lb, PX + 46, yy, 116, None, 18, MUTE))
        b.append(txt(f"{yr} 年", PX + 166, yy, 88, None, 18, MUTE, align="END"))
        b.append(txt(f"{v:+.2f}", PX + 262, yy, 100, None, 22, col, W600,
                     align="END"))
    b.append(txt("°C", PX + 362, yy, 40, None, 15, FAINT))'''

assert s.count(old) == 1
s = s.replace(old, new)
# 「1951–1980 基准期 = 0」原来压在 0 线半透明带右侧，移到带外下方更清楚
s = s.replace('b.append(rect(PX, ty(0) - 9, PW, 18, "#16191F0F"))',
              'b.append(rect(PX, ty(0) - 9, PW, 18, "#16191F0F"))\n'
              '    # 极值块占据左上，0 线标注相应右移到另一处，避免与数据点重叠')
p.write_text(s, encoding="utf-8")
print("c01 fixed")
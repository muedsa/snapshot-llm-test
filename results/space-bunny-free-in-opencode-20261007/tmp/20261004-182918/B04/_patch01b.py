"""One-off re-layout patcher for B04 case-01 (v3)."""
import io

p = r'tmp\20261004-182918\B04\build_c01.py'
s = io.open(p, encoding='utf-8').read()

pairs = [
    # taller top band
    ("BAND_H = 316", "BAND_H = 332"),
    # unit kicker must not sit on the curve: move it under the axis
    ('kids.append(K.kicker("ppm · 年均 · NOAA GML", cx1 - 300, cy(ser[-1][1]) + 18,\n'
     '                     size=11, color=K.INK_3, w=300, align="RIGHT"))',
     'kids.append(K.kicker("ppm · 年均", cx1 - 200, plot_bot + 16,\n'
     '                     size=11, color=K.INK_3, w=200, align="RIGHT"))'),
    # big-number baseline / caption collisions
    ("NUM_Y, NUM_S = MY + 108, 168", "NUM_Y, NUM_S = MY + 120, 168"),
    ("CAP_Y = NUM_Y + NUM_S - 18", "CAP_Y = NUM_Y + int(NUM_S * 1.10)"),
    ('kids.append(D.text_el("≈", x=406, y=NUM_Y + 30, size=92',
     'kids.append(D.text_el("≈", x=406, y=NUM_Y + 38, size=92'),
    # ruler panel geometry
    ("LX, LY, LW, LH = 1078, MY + 30, 414, 300",
     "LX, LY, LW, LH = 1078, MY + 26, 414, 402"),
    ('kids.append(K.body("pH 是对数刻度：降 1 个单位 = 氢离子 ×10。下面这把尺子"\n'
     '                   "按十进制等宽排布 pH 7.0–8.2。",\n'
     '                   LX + 22, LY + 46, LW - 44, size=13, color=K.INK_3))',
     'kids.append(K.body("pH 是对数刻度：降 1 个单位 = 氢离子 ×10。"\n'
     '                   "这把尺子按十进制等宽排布 pH 7.0–8.2。",\n'
     '                   LX + 22, LY + 48, LW - 44, size=13, color=K.INK_3))'),
    ("RULER_Y = LY + 132", "RULER_Y = LY + 176"),
    ('kids.append(K.body("真实换算来自来源，本图只是把它摆在同一把尺上。"\n'
     '                   "海水仍是碱性的（约 8.1），这里的「酸」是相对它自己而言。",\n'
     '                   LX + 26, RULER_Y + 132, LW - 52, size=13, color=K.INK_3))',
     'kids.append(K.body("换算数字来自来源；本图只把它摆在同一把尺上。"\n'
     '                   "海水仍是碱性的（约 8.1），这里的「酸」是相对它自己。",\n'
     '                   LX + 26, RULER_Y + 138, LW - 52, size=13, color=K.INK_3))'),
]
for a, b in pairs:
    if a not in s:
        print('MISS:', a.splitlines()[0][:70])
    s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched c01 v3')

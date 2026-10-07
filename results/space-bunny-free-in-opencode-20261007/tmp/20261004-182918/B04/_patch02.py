"""One-off label-collision patch for B04 case-02 (v2)."""
import io

p = r'tmp\20261004-182918\B04\build_c02.py'
s = io.open(p, encoding='utf-8').read()
pairs = [
    ('kids.append(K.mono("\'%02d" % (yr % 100), mx - 20, my + 12, size=13,\n'
     '                       color=K.AMBER, w=40, align="CENTER"))',
     'dx = 12 if up else -52\n'
     '    kids.append(K.mono("\'%02d" % (yr % 100), mx + dx, my + (10 if up else -2),\n'
     '                       size=13, color=K.AMBER))'),
    ('kids.append(K.mono("%.2f" % gmax, M - 4, GY0 + 2, size=11, color=K.INK_3, w=56))',
     'kids.append(K.mono("%.2f" % gmax, W - M - 120, GY0 + 4, size=11,\n'
     '                   color=K.INK_3, w=120, align="RIGHT"))'),
    ('kids.append(K.mono("0", M - 4, GY1 + 8, size=11, color=K.INK_3, w=40))',
     'kids.append(K.mono("0", M - 42, GY1 - 6, size=11, color=K.INK_3, w=34,\n'
     '                   align="RIGHT"))'),
    ('kids.append(K.mono("1958-03 由 C. D. Keeling 启动；1974-05 起 NOAA 平行测量至今",\n'
     '                   M, GY1 + 26, size=12, color=K.INK_3, w=600))',
     'kids.append(K.mono("1958-03 由 C. D. Keeling 启动；1974-05 起 NOAA 平行测量至今",\n'
     '                   M, GY1 + 20, size=12, color=K.INK_3, w=600))'),
    ('kids.append(K.legend([("2020 前", K.AMBER), ("2020 后", K.CORAL)], W - M - 200,\n'
     '                     GY1 + 22, size=12, gap=16))',
     'kids.append(K.legend([("2020 前", K.AMBER), ("2020 后", K.CORAL)], W - M - 200,\n'
     '                     GY1 + 16, size=12, gap=16))'),
]
for a, b in pairs:
    if a not in s:
        print('MISS:', a.splitlines()[0][:70])
    s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched c02 v2')

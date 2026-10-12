"""One-off layout patch for B04 case-07 (v2)."""
import io

p = r'tmp\20261004-182918\B04\build_c07.py'
s = io.open(p, encoding='utf-8').read()
pairs = [
    ('W, H = 1600, 1060', 'W, H = 1600, 1080'),
    ('AX0, AXW, AY, AH = M + 40, W - 2 * M - 80, 400, 56',
     'AX0, AXW, AY, AH = M + 40, W - 2 * M - 80, 322, 56'),
    # "Ω = 1" sat on top of the zone tick "1.0"
    ('kids.append(K.mono("Ω = 1", ox(1.0) + 12, AY - 26, size=13, color=K.CORAL))',
     'kids.append(K.mono("Ω = 1 · 建材分界", ox(1.0) - 188, AY - 26, size=13,\n'
     '                   color=K.CORAL, w=180, align="RIGHT"))'),
    ('TY = 566', 'TY = 500'),
    # the mini-bar Ω=1 caption collided with the source rule
    ('kids.append(K.mono("Ω=1", BX + BW / OM_HI - 26, SY + 46 + 6 * 21 - 4, size=10.5,\n'
     '                   color=K.CORAL, w=52, align="CENTER"))', ''),
    ('kids.append(K.kicker("今天与 2100 分别落在哪里 · 全球表层 Ωarag", AX0 + 20,\n'
     '                     SY + 16, size=11, color=K.CYAN))',
     'kids.append(K.kicker("今天与 2100 分别落在哪里 · 竖线为 Ω=1", AX0 + 20,\n'
     '                     SY + 16, size=11, color=K.CYAN))'),
    ('    yy = SY + 46 + i * 21', '    yy = SY + 50 + i * 20'),
    ('kids.append(K.vline(BX + BW / OM_HI, SY + 40, SY + 46 + 6 * 21 - 6,\n'
     '                    K.A(K.CORAL, "99"), 2))',
     'kids.append(K.vline(BX + BW / OM_HI, SY + 44, SY + 50 + 5 * 20 + 12,\n'
     '                    K.A(K.CORAL, "99"), 2))'),
]
for a, b in pairs:
    if a not in s:
        print('MISS:', a.splitlines()[0][:70])
    s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched c07 v2')

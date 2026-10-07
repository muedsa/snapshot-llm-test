"""One-off patcher: replace invalid string-concatenated colours with okit.A()."""
import io

p = r'tmp\20261004-182918\B04\okit.py'
s = io.open(p, encoding='utf-8').read()
reps = [
    ('fillc = fill if fill else color + "22"',
     'fillc = fill if fill else A(color, "22")'),
    ('b = "1 SOLID " + color + "66" if border else None',
     'b = "1 SOLID " + A(color, "66") if border else None'),
    ('"gradientColors": [CORAL + "00", g, CORAL + "00"],',
     '"gradientColors": [A(CORAL, "00"), g, A(CORAL, "00")],'),
    ('g = _mix(CORAL + "00", CORAL + "55", warm)',
     'g = _mix(A(CORAL, "00"), A(CORAL, "55"), warm)'),
    ('color=fill or (color + "1F")', 'color=fill or A(color, "1F")'),
    ('border="1 SOLID " + color + "55"', 'border="1 SOLID " + A(color, "55")'),
    ('out.append(D.box(x, y, s, s, color=color + alpha))',
     'out.append(D.box(x, y, s, s, color=A(color, alpha)))'),
]
for a, b in reps:
    if a not in s:
        print('MISS kit:', a[:70])
    s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)

p = r'tmp\20261004-182918\B04\build_c01.py'
s = io.open(p, encoding='utf-8').read()
reps = [
    ('K.fade_area(curve, cy_base, CYAN := K.CYAN + "4D", K.CYAN + "08")',
     'K.fade_area(curve, cy_base, K.A(K.CYAN, "4D"), K.A(K.CYAN, "08"))'),
    ('K.DEEP + "CC"', 'K.A(K.DEEP, "CC")'),
    ('K.CORAL + "99"', 'K.A(K.CORAL, "99")'),
]
for a, b in reps:
    if a not in s:
        print('MISS c01:', a[:70])
    s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched')

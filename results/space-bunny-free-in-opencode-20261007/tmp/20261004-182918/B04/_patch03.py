"""One-off collision patch for B04 case-03 (v2)."""
import io

p = r'tmp\20261004-182918\B04\build_c03.py'
s = io.open(p, encoding='utf-8').read()
pairs = [
    # band labels move to the vertical middle of each band
    ('    kids.append(D.text_el(lab, x=AX_X + AX_W + 20, y=ay(hi) + 4, size=12,\n'
     '                          color=col, font=D.UI, w=222))',
     '    mid = (ay(hi) + ay(lo)) / 2\n'
     '    kids.append(D.text_el(lab, x=AX_X + AX_W + 20, y=mid - 7, size=12,\n'
     '                          color=col, font=D.UI, w=222))'),
    ('    kids.append(D.box(AX_X + AX_W + 10, ay(hi) + 6, 3, ay(lo) - ay(hi) - 12,\n'
     '                      color=col))',
     '    kids.append(D.box(AX_X + AX_W + 10, mid - 30, 3, 16, color=col))'),
    # shorter leader lines so the tick labels stay clear
    ('kids.append(K.hline(AX_X - 14, AX_X + AX_W + 6, py, col, 2))',
     'kids.append(K.hline(AX_X - 8, AX_X + AX_W + 6, py, col, 2))'),
    # drop the redundant in-plot Δ label (it fought the tick labels)
    ('kids.append(K.mono("Δ0.12", AX_X + AX_W / 2 + 8, (ay(8.19) + ay(8.07)) / 2 - 7,\n'
     '                   size=12, color=K.CORAL))', ''),
    # inset bars must sit inside their panel
    ('BB, BH = IY + 84, 208', 'BB, BH = IY + IH - 64, 190'),
    ('kids.append(D.box(IX + 74, BB - BH, 72, BH, color=K.A(K.AMBER, "4D"), radius=4))',
     'kids.append(D.box(IX + 74, BB - BH, 72, BH, color=K.A(K.AMBER, "4D"), radius=4))\n'
     'kids.append(K.hline(IX + 60, IX + 224, BB - BH - 8, K.A(K.HAIR_2, "AA"), 1))'),
    ('kids.append(K.num("×1.32", IX + 250, BB - 66, size=44, color=K.CORAL))',
     'kids.append(K.num("×1.32", IX + 250, BB - 130, size=44, color=K.CORAL))'),
    # mono offset uses the real 0.602em advance
    ('kids.append(K.mono(approx, cx + 20 + D.est_width(pct, 38) + 10, CY + 116,\n'
     '                       size=14, color=K.INK_3))',
     'kids.append(K.mono(approx, cx + 20 + K.mono_w(pct, 38) + 12, CY + 116,\n'
     '                       size=14, color=K.INK_3))'),
]
for a, b in pairs:
    if a not in s:
        print('MISS:', a.splitlines()[0][:70])
    s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched c03 v2')

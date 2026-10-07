"""One-off label patch for B04 case-06 (v2)."""
import io

p = r'tmp\20261004-182918\B04\build_c06.py'
s = io.open(p, encoding='utf-8').read()
pairs = [
    # endpoint value labels must sit clear of the lines and inside the plot
    ('    for y, v in P["obs"]:\n'
     '        kids.append(K.mono("%d · %.2f" % (y, v), fx(y) + 14, fy(v) - 8,\n'
     '                           size=12.5, color=P["col"]))',
     '    for j, (y, v) in enumerate(P["obs"]):\n'
     '        ox = fx(y) + 12\n'
     '        oy = fy(v) - (26 if j == 0 else 16)\n'
     '        if j == 1:\n'
     '            ox = fx(y) - 150\n'
     '        kids.append(K.mono("%d · %.2f" % (y, v), ox, oy, size=12.5,\n'
     '                           color=P["col"]))'),
    # scenario endpoint value: merge into the left-side name label
    ('        ly = y_b - 34 if pi == 0 else y_b + 16\n'
     '        kids.append(K.mono(name, x_b - 210, ly, size=13, color=col, w=196,\n'
     '                           align="RIGHT"))\n'
     '        if pi == 0:\n'
     '            kids.append(K.mono("%.2f" % v210, x_b + 14, ly, size=15, color=col))\n'
     '        else:\n'
     '            kids.append(K.mono("%.1f" % v210, x_b + 14, ly, size=15, color=col))',
     '        ly = y_b - 34 if pi == 0 else y_b + 14\n'
     '        fmt = "%.2f" if pi == 0 else "%.1f"\n'
     '        kids.append(K.mono("%s  →  %s" % (name, fmt % v210), x_b - 250, ly,\n'
     '                           size=13, color=col, w=236, align="RIGHT"))\n'
     '        if pi == 0:\n'
     '            kids.append(D.text_el("低排放·高减缓", x=x_b - 250, y=ly + 18,\n'
     '                              size=11.5, color=K.INK_3, font=D.UI, w=236,\n'
     '                              align="RIGHT"))\n'
     '        else:\n'
     '            kids.append(D.text_el("高排放·低减缓", x=x_b - 250, y=ly + 18,\n'
     '                              size=11.5, color=K.INK_3, font=D.UI, w=236,\n'
     '                              align="RIGHT"))'),
    ('    yy = 330 + i * 74', '    yy = 328 + i * 80'),
    ('    kids.append(K.mono(tail, RX + 20, yy + 58, size=10.5, color=col))',
     '    kids.append(K.mono(tail, RX + 20, yy + 60, size=10.5, color=col))'),
]
for a, b in pairs:
    if a not in s:
        print('MISS:', a.splitlines()[0][:70])
    s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched c06 v2')

p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A22\build_a22.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('''REG = dict(header=[28, 20, 1572, 94], kpis=[28, 130, 1544, 138],
           conclusion=[28, 284, 1544, 114],
           chart=[28, 414, 1108, 416], table=[1148, 414, 424, 416],
           footer=[28, 854, 1572, 112])''',
     '''REG = dict(header=[28, 20, 1572, 112], kpis=[28, 142, 1544, 128],
           conclusion=[28, 282, 1544, 96],
           chart=[28, 390, 1108, 416], table=[1148, 390, 424, 416],
           footer=[28, 822, 1572, 120])'''),
    ('''    doc.text(hx + 28, hy + 16, title, 34, "#F8FAFCFF", weight="BOLD", maxw=hw - 420)
    doc.rtext(hx + hw - 28, hy + 14, f'{t["months"]} 个月 · {t["period"]}', 22, "#94A3B8FF")
    doc.text(hx + 28, hy + 52, sub, 20, "#CBD5E1FF", maxw=hw - 56)''',
     '''    doc.text(hx + 28, hy + 14, title, 34, "#F8FAFCFF", weight="BOLD", maxw=hw - 420)
    doc.rtext(hx + hw - 28, hy + 30, f'{t["months"]} 个月 · {t["period"]}', 22,
              "#94A3B8FF")
    doc.text(hx + 28, hy + 78, sub, 20, "#CBD5E1FF", maxw=hw - 56)'''),
    # KPI note moves with the shorter card
    ('        doc.text(x + 26, ky + 100, note, 20, "#64748BFF", maxw=CARD_W - 44)',
     '        doc.text(x + 26, ky + 98, note, 20, "#64748BFF", maxw=CARD_W - 44)'),
    ('        measured.append(dict(text=note, size=20, color="#64748BFF", y=ky + 100,',
     '        measured.append(dict(text=note, size=20, color="#64748BFF", y=ky + 98,'),
    ('        doc.text(fx + 26, fy + 10 + i * 24, nt, 20, SUB, maxw=fw - 56)\n'
     '        measured.append(dict(text=nt, size=20, color=SUB, y=fy + 10 + i * 24,',
     '        doc.text(fx + 26, fy + 12 + i * 26, nt, 20, SUB, maxw=fw - 56)\n'
     '        measured.append(dict(text=nt, size=20, color=SUB, y=fy + 12 + i * 26,'),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched', len(pairs))

import io
p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A22\build_a22.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('table=[1196, 392, 376, 480],', 'table=[1172, 392, 400, 480],'),
    ('''    cols = [("月份", 16, 96, "left"), ("净收入", 116, 62, "right"),
            ("经营利润", 182, 62, "right"), ("退款率", 248, 60, "right"),
            ("转化率", 312, 50, "right")]''',
     '''    cols = [("月份", 16, 108, "left"), ("净收入", 128, 64, "right"),
            ("经营利润", 196, 64, "right"), ("退款率", 264, 62, "right"),
            ("转化率", 330, 54, "right")]'''),
    ('    doc.rtext(tx + tw - 20, ty + 18, f"{n} 行", 20, "#64748BFF")',
     '    doc.text(tx + 20, ty + 44, f"{n} 行 · 与柱高同一数据源", 20, "#64748BFF", maxw=tw - 40)'),
    ('    ttop = ty + 54\n    theight = th - (ttop - ty) - 14',
     '    ttop = ty + 74\n    theight = th - (ttop - ty) - 10'),
    ('        doc.text(x + 26, ky + 108, note, 20, "#64748BFF", maxw=CARD_W - 40)',
     '        doc.text(x + 26, ky + 99, note, 20, "#64748BFF", maxw=CARD_W - 40)'),
    ('        measured.append(dict(text=note, size=20, color="#64748BFF", y=ky + 108,',
     '        measured.append(dict(text=note, size=20, color="#64748BFF", y=ky + 99,'),
]
for a, b in pairs:
    assert a in s, a[:60]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched', len(pairs))

p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A22\build_a22.py'
s = open(p, encoding='utf-8').read()
pairs = [
    # legend shares the title row (short titles), and the table gets more inner height
    ('    lx = px + 24\n    ly = py + 70', '    lx = px + 430\n    ly = py + 34'),
    ('''    doc.text(px + 24, py + 16, "净收入 / 经营利润（共用零起点）", 24, INK, weight="BOLD",
             maxw=pw - 260)''',
     '''    doc.text(px + 24, py + 14, "净收入 / 经营利润（共用零起点）", 24, INK, weight="BOLD",
             maxw=390)'''),
    ('    doc.rtext(px + pw - 24, py + 38, "单位：元", 20, "#64748BFF")',
     '    doc.rtext(px + pw - 24, py + 18, "单位：元", 20, "#64748BFF")'),
    ('''    doc.text(tx + 20, ty + 14, "月度明细", 24, INK, weight="BOLD", maxw=200,)
    doc.text(tx + 20, ty + 44, f"{n} 行 · 与柱高同一数据源", 20, "#64748BFF", maxw=tw - 40)''',
     '''    doc.text(tx + 18, ty + 12, "月度明细", 24, INK, weight="BOLD", maxw=180)
    doc.text(tx + 18, ty + 40, f"{n} 行 · 与柱高同一数据源", 20, "#64748BFF",
             maxw=tw - 36)'''),
    ('    ttop = ty + 74\n    theight = th - (ttop - ty) - 10',
     '    ttop = ty + 68\n    theight = th - (ttop - ty) - 8'),
    ('    assert ttop + rh * (n + 1) <= ty + th - 6, "table rows overflow the panel"',
     '    assert ttop + rh * (n + 1) <= ty + th - 8, "table rows overflow the panel"'),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:60]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched legend row + table height')

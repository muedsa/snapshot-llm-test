p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A22\build_a22.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('''    doc.text(tx + 18, ty + 12, "月度明细", 24, INK, weight="BOLD", maxw=180)
    doc.text(tx + 18, ty + 40, f"{n} 行 · 与柱高同一数据源", 20, "#64748BFF",
             maxw=tw - 36)''',
     '''    doc.text(tx + 18, ty + 12, "月度明细", 24, INK, weight="BOLD", maxw=170)
    doc.rtext(tx + tw - 18, ty + 18, f"{n} 行", 20, "#64748BFF")'''),
    ('''    ttop = ty + 68
    theight = th - (ttop - ty) - 8
    rh = theight / (n + 1)''',
     '''    ttop = ty + 48
    # every row (text and its tint) must stay inside the panel: solve the row height from
    # the bottom edge instead of guessing it
    rh = (ty + th - 14 - ttop) / (n + 1)
    assert rh >= 40, f"table rows would be crushed to {rh:.1f}px"'''),
    ('''            yy = round(ry + rh * 0.26)
            if align == "right":
                doc.rtext(tx + off + wdt, yy, val, 20, col, family=fam)
            else:
                doc.text(tx + off, yy, val, 20, col, weight="BOLD", family=fam,
                         maxw=wdt)''',
     '''            yy = round(ry + max(6, (rh - 26) / 2))
            if align == "right":
                doc.rtext(tx + off + wdt, yy, val, 20, col, family=fam)
            else:
                doc.text(tx + off, yy, val, 20, col, weight="BOLD", family=fam,
                         maxw=wdt)'''),
    ('''    assert ttop + rh * (n + 1) <= ty + th - 8, "table rows overflow the panel"''',
     '''    assert ttop + rh * (n + 1) <= ty + th - 10, "table rows overflow the panel"'''),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:60]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched table row height solver')

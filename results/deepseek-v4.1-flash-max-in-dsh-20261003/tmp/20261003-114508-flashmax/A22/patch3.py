p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A22\build_a22.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('chart=[28, 414, 1180, 416], table=[1172, 414, 400, 416],',
     'chart=[28, 414, 1108, 416], table=[1148, 414, 424, 416],'),
    # table cells at 20px so five columns of real numbers fit the panel
    ('''    _hdr = [("月份", "left", 22, CJK), ("净收入", "right", 22, MONO),
            ("经营利润", "right", 22, MONO), ("退款率", "right", 22, MONO),
            ("转化率", "right", 22, MONO)]''',
     '''    _hdr = [("月份", "left", 20, CJK), ("净收入", "right", 20, MONO),
            ("经营利润", "right", 20, MONO), ("退款率", "right", 20, MONO),
            ("转化率", "right", 20, MONO)]'''),
    ('''    _w = [max(text_width(v, 22, mono=(fam is MONO)) for v in col) + 10
          for col, _a, _sz, fam in zip(_vals, [c[1] for c in _hdr],
                                       [c[2] for c in _hdr], [c[3] for c in _hdr])]
    _avail = tw - 34''',
     '''    _w = [max(text_width(v, 20, mono=(fam is MONO)) for v in col) + 6
          for col, _a, _sz, fam in zip(_vals, [c[1] for c in _hdr],
                                       [c[2] for c in _hdr], [c[3] for c in _hdr])]
    _avail = tw - 32'''),
    ('''        yy = round(ttop + rh * 0.30)
        if align == "right":
            doc.rtext(tx + off + wdt, yy, name, 20, "#64748BFF", weight="BOLD")
        else:
            doc.text(tx + off, yy, name, 20, "#64748BFF", weight="BOLD", maxw=wdt)''',
     '''        yy = round(ttop + rh * 0.30)
        if align == "right":
            doc.rtext(tx + off + wdt, yy, name, 20, "#64748BFF", weight="BOLD")
        else:
            doc.text(tx + off, yy, name, 20, "#64748BFF", weight="BOLD", maxw=wdt)
        measured.append(dict(text=name, size=20, color="#64748BFF", y=yy,
                             role="table_head"))'''),
    ('''            if align == "right":
                doc.rtext(tx + off + wdt, yy, val, 22, col, family=fam)
            else:
                doc.text(tx + off, yy, val, 22, col, weight="BOLD", family=fam,
                         maxw=wdt)
            measured.append(dict(text=val, size=22, color=col, y=yy, role="table_row"))''',
     '''            if align == "right":
                doc.rtext(tx + off + wdt, yy, val, 20, col, family=fam)
            else:
                doc.text(tx + off, yy, val, 20, col, weight="BOLD", family=fam,
                         maxw=wdt)
            measured.append(dict(text=val, size=20, color=col, y=yy, role="table_row"))'''),
    ('''        if m["month"] == "2026-10":
            doc.text(tx + 16, round(ry + rh * 0.26 + 24), "新增月份", 20, PROFIT,
                     weight="BOLD", maxw=90)''',
     '''        if m["month"] == "2026-10":
            doc.text(tx + 16, round(ry + rh * 0.26 + 22), "新增月份", 20, PROFIT,
                     weight="BOLD", maxw=90)'''),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched', len(pairs))

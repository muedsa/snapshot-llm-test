import re
p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A22\build_a22.py'
s = open(p, encoding='utf-8').read()
pairs = [
    # regions: real gaps so no panel can touch another
    ('''REG = dict(header=[28, 20, 1572, 94], kpis=[28, 126, 1544, 124],
           conclusion=[28, 262, 1544, 118],
           chart=[28, 392, 1180, 380], table=[1172, 392, 400, 480],
           footer=[28, 900, 1572, 76])''',
     '''REG = dict(header=[28, 20, 1572, 94], kpis=[28, 130, 1544, 138],
           conclusion=[28, 284, 1544, 114],
           chart=[28, 414, 1180, 416], table=[1172, 414, 400, 416],
           footer=[28, 854, 1572, 112])'''),
    # KPI card internals
    ('''        doc.text(x + 26, ky + 18, label, 22, SUB, maxw=CARD_W - 40)
        vw = text_width(value, 52, mono=True)
        doc.text(x + 26, ky + 50, value, 52, INK, weight="BOLD", family=MONO, maxw=CARD_W - 40)
        doc.text(x + 26 + vw + 12, ky + 74, unit, 22, SUB, maxw=CARD_W - 60 - vw)
        doc.text(x + 26, ky + 99, note, 20, "#64748BFF", maxw=CARD_W - 40)
        measured.append(dict(text=label, size=22, color=SUB, y=ky + 18, role="kpi_label"))
        measured.append(dict(text=value, size=52, color=INK, y=ky + 50, role="kpi_value"))
        measured.append(dict(text=note, size=20, color="#64748BFF", y=ky + 99,
                             role="kpi_note"))''',
     '''        doc.text(x + 26, ky + 14, label, 22, SUB, maxw=CARD_W - 44)
        vw = text_width(value, 48, mono=True)
        doc.text(x + 26, ky + 44, value, 48, INK, weight="BOLD", family=MONO,
                 maxw=CARD_W - 44)
        doc.text(x + 30 + vw, ky + 66, unit, 22, SUB, maxw=CARD_W - 54 - vw)
        doc.text(x + 26, ky + 100, note, 20, "#64748BFF", maxw=CARD_W - 44)
        measured.append(dict(text=label, size=22, color=SUB, y=ky + 14, role="kpi_label"))
        measured.append(dict(text=value, size=48, color=INK, y=ky + 44, role="kpi_value"))
        measured.append(dict(text=note, size=20, color="#64748BFF", y=ky + 100,
                             role="kpi_note"))'''),
    # chart legend laid out with measured widths instead of fixed guesses
    ('''    doc.box(px + 24, py + 46, 22, 12, NET, radius=6)
    doc.text(px + 54, py + 42, "净收入", 20, SUB, maxw=120)
    doc.box(px + 150, py + 46, 22, 12, PROFIT, radius=6)
    doc.text(px + 180, py + 42, "经营利润", 20, SUB, maxw=140)
    doc.box(px + 300, py + 46, 22, 12, NEG, radius=6)
    doc.text(px + 330, py + 42, "零起点", 20, SUB, maxw=120)
    doc.rtext(px + pw - 24, py + 42, "单位：元", 20, "#64748BFF")''',
     '''    lx = px + 24
    ly = py + 50
    for lbl, col in (("净收入", NET), ("经营利润", PROFIT), ("零起点", NEG)):
        doc.box(lx, ly - 6, 22, 12, col, radius=6)
        doc.text(lx + 30, ly - 12, lbl, 20, SUB, maxw=int(text_width(lbl, 20)) + 8)
        lx += 30 + int(text_width(lbl, 20)) + 34
    doc.rtext(px + pw - 24, py + 38, "单位：元", 20, "#64748BFF")'''),
    # table columns: measured widths so no two columns can touch
    ('''    cols = [("月份", 16, 108, "left"), ("净收入", 128, 64, "right"),
            ("经营利润", 196, 64, "right"), ("退款率", 264, 62, "right"),
            ("转化率", 330, 54, "right")]''',
     '''    _hdr = [("月份", "left", 22, CJK), ("净收入", "right", 22, MONO),
            ("经营利润", "right", 22, MONO), ("退款率", "right", 22, MONO),
            ("转化率", "right", 22, MONO)]
    _vals = [["月份"] + [m["month"] for m in months],
             ["净收入"] + [fmt(m["net_revenue"]) for m in months],
             ["经营利润"] + [fmt(m["operating_profit"]) for m in months],
             ["退款率"] + [f'{m["refund_rate"]:.2f}%' for m in months],
             ["转化率"] + [f'{m["conversion_rate"]:.2f}%' for m in months]]
    _w = [max(text_width(v, 22, mono=(fam is MONO)) for v in col) + 10
          for col, _a, _sz, fam in zip(_vals, [c[1] for c in _hdr],
                                       [c[2] for c in _hdr], [c[3] for c in _hdr])]
    _avail = tw - 34
    if sum(_w) > _avail:
        k = _avail / sum(_w)
        _w = [x * k for x in _w]
    _gap = (_avail - sum(_w)) / 4
    cols = []
    _x = 16.0
    for i, (name, align, sz, fam) in enumerate(_hdr):
        cols.append((name, round(_x), round(_w[i]), align, fam))
        _x += _w[i] + _gap'''),
    ('''    for name, off, wdt, align in cols:
        yy = round(ttop + rh * 0.30)
        if align == "right":
            doc.rtext(tx + off + wdt, yy, name, 20, "#64748BFF", weight="BOLD")
        else:
            doc.text(tx + off, yy, name, 20, "#64748BFF", weight="BOLD", maxw=wdt)''',
     '''    for name, off, wdt, align, _fam in cols:
        yy = round(ttop + rh * 0.30)
        if align == "right":
            doc.rtext(tx + off + wdt, yy, name, 20, "#64748BFF", weight="BOLD")
        else:
            doc.text(tx + off, yy, name, 20, "#64748BFF", weight="BOLD", maxw=wdt)'''),
    ('''        vals = [(m["month"], INK, "left", CJK),
                (fmt(m["net_revenue"]), INK, "right", MONO),
                (fmt(m["operating_profit"]),
                 NEG if m["operating_profit"] < 0 else INK, "right", MONO),
                (f'{m["refund_rate"]:.2f}%', SUB, "right", MONO),
                (f'{m["conversion_rate"]:.2f}%', SUB, "right", MONO)]
        for j, (val, col, align, fam) in enumerate(vals):
            _name, off, wdt, _al = cols[j]
            yy = round(ry + rh * 0.26)
            if align == "right":
                doc.rtext(tx + off + wdt, yy, val, 22, col, family=fam)
            else:
                doc.text(tx + off, yy, val, 22, col, weight="BOLD", family=fam,
                         maxw=wdt)
            measured.append(dict(text=val, size=22, color=col, y=yy, role="table_row"))
        if m["month"] == "2026-10":
            doc.text(tx + 16, round(ry + rh * 0.26 + 24), "新增月份", 20, PROFIT,
                     weight="BOLD", maxw=90)''',
     '''        vals = [(m["month"], INK, "left", CJK),
                (fmt(m["net_revenue"]), INK, "right", MONO),
                (fmt(m["operating_profit"]),
                 NEG if m["operating_profit"] < 0 else INK, "right", MONO),
                (f'{m["refund_rate"]:.2f}%', SUB, "right", MONO),
                (f'{m["conversion_rate"]:.2f}%', SUB, "right", MONO)]
        for j, (val, col, align, fam) in enumerate(vals):
            _name, off, wdt, _al, _fam = cols[j]
            yy = round(ry + rh * 0.26)
            if align == "right":
                doc.rtext(tx + off + wdt, yy, val, 22, col, family=fam)
            else:
                doc.text(tx + off, yy, val, 22, col, weight="BOLD", family=fam,
                         maxw=wdt)
            measured.append(dict(text=val, size=22, color=col, y=yy, role="table_row"))
        if m["month"] == "2026-10":
            doc.text(tx + 16, round(ry + rh * 0.26 + 24), "新增月份", 20, PROFIT,
                     weight="BOLD", maxw=90)'''),
    # footer: 4 notes need 21px leading inside a 112px panel
    ('        doc.text(fx + 26, fy + 6 + i * 17, nt, 20, SUB, maxw=fw - 56)\n'
     '        measured.append(dict(text=nt, size=20, color=SUB, y=fy + 6 + i * 17,',
     '        doc.text(fx + 26, fy + 10 + i * 24, nt, 20, SUB, maxw=fw - 56)\n'
     '        measured.append(dict(text=nt, size=20, color=SUB, y=fy + 10 + i * 24,'),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched', len(pairs))

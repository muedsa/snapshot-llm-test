p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A24\build_a24.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('    rows_h = 344', '    rows_h = 356'),
    ('''    # 12 real rows: the row height is solved so the last row still ends inside the panel
    rh = (rows_h - 56) / 12
    assert rh >= 22, f"table rows would be crushed to {rh:.1f}px"''',
     '''    # 12 real rows at 18px type: the row height is solved so the last row still ends
    # inside the panel and the canvas
    rh = 26.0
    assert ty0 + 42 + 12 * rh <= H - 12, (
        f"table would end at {ty0 + 42 + 12 * rh:.0f}px, past the canvas")'''),
    ('''        vals = [(t["id"], INK, MONO, "BOLD"), (t["label"], INK, CJK, "NORMAL"),
                (f'{t["minutes"]} 分钟', SUB, MONO, "NORMAL"),
                ("、".join(t["depends"]) or "—", SUB, MONO, "NORMAL"),
                (t["team"], col + "FF", CJK, "BOLD"),
                (f'{t["start"]}–{t["end"]}', SUB, MONO, "NORMAL"),
                (f'依赖 {"、".join(t["depends"]) or "无"} 完成后开始', DIMC, CJK,
                 "NORMAL")]
        for j, (val, vc, fam, wt) in enumerate(vals):
            name, off, wdt = cols[j]
            assert_fits(val, 20, wdt, f"tbl-{t['id']}-{j}")
            d.text(24 + off, ry, val, 20, vc, weight=wt, maxw=wdt, family=fam)
            measured.append(dict(text=val, size=20, color=vc, y=ry, role="table"))''',
     '''        vals = [(t["id"], INK, MONO, "BOLD"), (t["label"], INK, CJK, "NORMAL"),
                (f'{t["minutes"]} 分钟', SUB, MONO, "NORMAL"),
                ("、".join(t["depends"]) or "—", SUB, MONO, "NORMAL"),
                (t["team"], col + "FF", CJK, "BOLD"),
                (f'{t["start"]}–{t["end"]}', SUB, MONO, "NORMAL"),
                (f'依赖 {"、".join(t["depends"]) or "无"} 完成后开始', DIMC, CJK,
                 "NORMAL")]
        for j, (val, vc, fam, wt) in enumerate(vals):
            name, off, wdt = cols[j]
            assert_fits(val, 18, wdt, f"tbl-{t['id']}-{j}")
            d.text(24 + off, ry + 3, val, 18, vc, weight=wt, maxw=wdt, family=fam)
            measured.append(dict(text=val, size=18, color=vc, y=ry + 3, role="table"))'''),
    ('''        need.append(m + 12)''', '''        need.append(m + 12)
    # the table body is set at 18px, so the header widths are solved at 18px too
    need = round_need = [max(text_width(col_names[j], 18, mono=(col_fams[j] is MONO)),
                             max(text_width(r[j], 18, mono=(col_fams[j] is MONO))
                                 for r in rows_vals)) + 12 for j in range(7)]'''),
    ('''    for name, off, wdt in cols:
        d.text(24 + off, hdr_y, name, 20, SUB, weight="BOLD", maxw=wdt)''',
     '''    for name, off, wdt in cols:
        d.text(24 + off, hdr_y, name, 18, SUB, weight="BOLD", maxw=wdt)'''),
    ('''    d.text(48, ty0 + rows_h + 12,''', '''    d.text(48, ty0 + rows_h - 46,'''),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')

p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A24\build_a24.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('''    app = [f'{t["id"]} {t["label"]}' for t in sch["tasks"]]
    app2 = [f'{t["team"]} · {t["start"]}–{t["end"]} · {t["minutes"]} 分钟'
            for t in sch["tasks"]]
    col_w2 = (W - 96 - 32) / 2
    rows_n = 6
    for i in range(rows_n):
        for c in range(2):
            k = i + c * rows_n
            if k >= len(app):
                continue
            x = 48 + c * (col_w2 + 32)
            yy = ly + i * 26
            assert_fits(app[k], 20, col_w2 * 0.5, "appendix-name")
            d.text(x, yy, app[k], 20, INK, maxw=col_w2 * 0.5)
            d.text(x + col_w2 * 0.5 + 8, yy, app2[k], 20, SUB, family=MONO,
                   maxw=col_w2 * 0.5 - 8)
            measured.append(dict(text=app[k], size=20, color=INK, y=yy,
                                 role="appendix"))''',
     '''    app = [f'{t["id"]} {t["label"]}' for t in sch["tasks"]]
    app2 = [f'{t["team"]}  {t["start"]}–{t["end"]}  {t["minutes"]}m'
            for t in sch["tasks"]]
    col_w2 = (W - 96 - 32) / 2
    name_w = 132.0
    rows_n = 6
    for i in range(rows_n):
        for c in range(2):
            k = i + c * rows_n
            if k >= len(app):
                continue
            x = 48 + c * (col_w2 + 32)
            yy = ly + i * 26
            assert_fits(app[k], 20, name_w, "appendix-name")
            assert_fits(app2[k], 20, col_w2 - name_w - 8, "appendix-time", mono=True)
            d.text(x, yy, app[k], 20, INK, maxw=name_w)
            d.text(x + name_w + 8, yy, app2[k], 20, SUB, family=MONO,
                   maxw=col_w2 - name_w - 8)
            measured.append(dict(text=app[k], size=20, color=INK, y=yy,
                                 role="appendix"))'''),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')

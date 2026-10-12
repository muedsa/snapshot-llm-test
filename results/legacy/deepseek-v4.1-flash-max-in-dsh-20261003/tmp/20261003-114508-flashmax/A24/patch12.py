p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A24\build_a24.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('''    col_w2 = (W - 96 - 32) / 2
    name_w = 150.0''',
     '''    col_w2 = (W - 96 - 32) / 2
    name_w = max(text_width(x, 20) for x in app) + 10
    assert name_w + max(text_width(x, 20, mono=True) for x in app2) + 12 <= col_w2, \\
        "the brief appendix needs two wider columns"'''),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')

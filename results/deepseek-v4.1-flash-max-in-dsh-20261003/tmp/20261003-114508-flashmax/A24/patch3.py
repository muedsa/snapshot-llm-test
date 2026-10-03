p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A24\build_a24.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('    d.text(48, 162, "真实时间（同尺度）", 22, INK, weight="BOLD", maxw=180)',
     '    d.text(48, 162, "真实时间（同尺度）", 22, INK, weight="BOLD", maxw=196)'),
    ('    d.text(48, 190, "每 30 分钟一格", 20, DIMC, maxw=180)',
     '    d.text(48, 190, "每 30 分钟一格", 20, DIMC, maxw=196)'),
    ('''        d.text(48, lane_y + 12, title, 20, SUB, weight="BOLD", maxw=180,
               )''',
     '''        d.text(48, lane_y + 12, title, 20, SUB, weight="BOLD", maxw=180)'''),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:60]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')

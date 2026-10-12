p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A24\build_a24.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('''    lanes = (("design", "design 团队（单队，不可并行/不可抢占）"),
             ("engineering", "engineering 团队（单队，不可并行/不可抢占）"))''',
     '''    lanes = (("design", "design", "单队 · 不可并行"),
             ("engineering", "engineering", "单队 · 不可并行"))'''),
    ('''        d.text(48, lane_y + 12, title, 20, SUB, weight="BOLD", maxw=180)
        seq = [t for t in tasks if t["team"] == tm]''',
     '''        d.text(48, lane_y + 12, title, 22, t["accent"] if False else SUB,
               weight="BOLD", maxw=196)
        d.text(48, lane_y + 40, note, 18, DIMC, maxw=196)
        seq = [t for t in tasks if t["team"] == tm]'''),
    ('''    for tm, title in lanes:''', '''    for tm, title, note in lanes:'''),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')

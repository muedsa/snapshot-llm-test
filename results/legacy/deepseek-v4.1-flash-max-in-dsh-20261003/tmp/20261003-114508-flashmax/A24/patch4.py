p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A24\build_a24.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('    lx0, lx1 = 232, W - 46', '    lx0, lx1 = 268, W - 46'),
    ('    rx0, rx1 = 96, W - 44', '    rx0, rx1 = 118, W - 44'),
    ('''    cols = [("编号", 46, 70), ("任务", 130, 190), ("时长", 336, 76), ("依赖", 424, 150),
            ("团队", 590, 130), ("起止", 736, 150), ("依赖说明", 906, 900)]''',
     '''    cols = [("编号", 46, 64), ("任务", 120, 150), ("时长", 280, 84), ("依赖", 372, 140),
            ("团队", 520, 130), ("起止", 656, 140), ("说明", 806, 1000)]'''),
    ('''                (f'依赖 {"、".join(t["depends"]) or "无"} 完成后开始', DIMC, CJK, "NORMAL")]''',
     '''                (f'依赖 {"、".join(t["depends"]) or "无"} 完成后开始', DIMC, CJK,
                 "NORMAL")]'''),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:60]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')

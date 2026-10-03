p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A24\build_a24.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('''        ("计划完成", f'{sch["makespan_end"]} / 第 {sch["makespan_minutes"]} 分钟', BLUE),''',
     '''        ("计划完成", f'{sch["makespan_end"]} 完成', BLUE),'''),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:60]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')

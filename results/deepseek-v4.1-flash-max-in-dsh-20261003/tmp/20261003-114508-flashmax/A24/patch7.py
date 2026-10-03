p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A24\build_a24.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('    assert_fits(headline, 24, W - 120, "brief-headline")\n'
     '    d.text(48, y + 20, headline, 24, "#0F172AFF", weight="BOLD", maxw=W - 96)',
     '    assert_fits(headline, 22, W - 110, "brief-headline")\n'
     '    d.text(48, y + 18, headline, 22, "#0F172AFF", weight="BOLD", maxw=W - 96)'),
    ('''    headline = (f'最早完成 {sch["makespan_end"]}（第 {sch["makespan_minutes"]} 分钟），'
                f'距 16:00 截止还有 {sch["buffer_minutes"]} 分钟缓冲；'
                f'12 项任务一项不删、时长不缩。')''',
     '''    headline = (f'最早完成 {sch["makespan_end"]}（第 {sch["makespan_minutes"]} 分钟）；'
                f'距 16:00 还有 {sch["buffer_minutes"]} 分钟缓冲；12 项任务不删不减。')'''),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')

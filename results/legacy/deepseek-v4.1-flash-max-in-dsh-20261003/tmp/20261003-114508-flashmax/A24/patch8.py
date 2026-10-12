p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A24\build_a24.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('''    d.box(24, y, W - 48, 96, "#CCFBF1FF", radius=14, border="1 SOLID #5EEAD4")
    d.box(24, y, 6, 96, TEAL, radius=3)''',
     '''    d.box(24, y, W - 48, 124, "#CCFBF1FF", radius=14, border="1 SOLID #5EEAD4")
    d.box(24, y, 6, 124, TEAL, radius=3)'''),
    ('''    sub = (f'忽略资源约束的关键路径 {sch["lower_bounds"]["critical_path_minutes"]} 分钟'
           f'（{"→".join(sch["lower_bounds"]["critical_path_chain"])}），'
           f'总工作量 {sch["lower_bounds"]["total_work_minutes"]} 分钟，'
           f'两团队下界 {sch["lower_bounds"]["work_per_team_bound_minutes"]} 分钟；'
           f'实际比下界多 {sch["assignment_search"]["gap_to_lower_bound_minutes"]} 分钟。')
    assert_fits(sub, 20, W - 120, "brief-sub")
    d.text(48, y + 58, sub, 20, SUB, maxw=W - 96)
    y += 118''',
     '''    sub1 = (f'忽略资源约束的关键路径 {sch["lower_bounds"]["critical_path_minutes"]} 分钟'
            f'（{"→".join(sch["lower_bounds"]["critical_path_chain"])}）；'
            f'总工作量 {sch["lower_bounds"]["total_work_minutes"]} 分钟。')
    sub2 = (f'两团队下界 {sch["lower_bounds"]["work_per_team_bound_minutes"]} 分钟，'
            f'实际比下界多 {sch["assignment_search"]["gap_to_lower_bound_minutes"]} 分钟；'
            f'本计划不声称已证明全局最优。')
    for i, sub in enumerate((sub1, sub2)):
        assert_fits(sub, 20, W - 110, "brief-sub")
        d.text(48, y + 56 + i * 28, sub, 20, SUB, maxw=W - 96)
        measured.append(dict(text=sub, size=20, color=SUB, y=y + 56 + i * 28,
                             role="sub"))
    y += 146''')
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')

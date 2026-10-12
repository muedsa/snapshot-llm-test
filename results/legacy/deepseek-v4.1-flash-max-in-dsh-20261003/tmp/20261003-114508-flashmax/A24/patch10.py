p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A24\build_a24.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('''    rh_ = 300
    card(d, 24, y, W - 48, rh_, radius=14)
    d.text(48, y + 14, "三大风险与对策", 24, INK, weight="BOLD", maxw=400)
    ry = y + 52''',
     '''    rh_ = 344
    card(d, 24, y, W - 48, rh_, radius=14)
    d.text(48, y + 14, "三大风险与对策", 24, INK, weight="BOLD", maxw=400)
    d.text(48, y + 46, "每项风险都指向一个真实任务与一个可执行对策；对策不改变任务时长。",
           20, SUB, maxw=W - 96)
    ry = y + 82'''),
    ('''        d.box(44, ry, W - 88, 78, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")
        d.box(44, ry, 5, 78, AMBER, radius=2)''',
     '''        d.box(44, ry, W - 88, 84, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")
        d.box(44, ry, 5, 84, AMBER, radius=2)'''),
    ('''            assert_fits(ln, sz, W - 130, f"risk-{k['id']}")
            d.text(64, ry + 8 + i * 23, ln, sz, col, weight=wt, maxw=W - 130)
            measured.append(dict(text=ln, size=sz, color=col, y=ry + 8 + i * 23,
                                 role="risk"))
        ry += 80''',
     '''            assert_fits(ln, sz, W - 130, f"risk-{k['id']}")
            d.text(64, ry + 10 + i * 23, ln, sz, col, weight=wt, maxw=W - 130)
            measured.append(dict(text=ln, size=sz, color=col, y=ry + 10 + i * 23,
                                 role="risk"))
        ry += 88'''),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')

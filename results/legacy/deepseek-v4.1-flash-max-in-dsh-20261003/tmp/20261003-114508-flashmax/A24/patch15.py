p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A24\build_a24.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('''    lane_rows = 2
    lane_rh = 32
    lane_top = 44
    lane_h = lane_top + lane_rows * lane_rh + 12''',
     '''    lane_rows = 3
    lane_rh = 28
    lane_top = 40
    lane_h = lane_top + lane_rows * lane_rh + 8'''),
    ('''        per_row = 3
        for i, t in enumerate(seq):
            ty = round(lane_y + lane_top + (i // per_row) * lane_rh)
            bh = 24''',
     '''        per_row = 2
        for i, t in enumerate(seq):
            ty = round(lane_y + lane_top + (i // per_row) * lane_rh)
            bh = 22'''),
    ('    rows_h = 392', '    rows_h = 400'),
    ('''    d.text(48, ty0 + rows_h - 46,''',
     '''    d.text(48, ty0 + rows_h + 12,'''),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')

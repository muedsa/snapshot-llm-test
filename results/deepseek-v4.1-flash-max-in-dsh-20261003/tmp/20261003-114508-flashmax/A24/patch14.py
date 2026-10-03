p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A24\build_a24.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('''    lane_rows = 6
    lane_rh = 34
    lane_top = 44
    lane_h = lane_top + lane_rows * lane_rh + 10''',
     '''    # each lane wraps its six tasks into two rows of three, which halves the lane block
    # and leaves the bottom of the canvas free for the full 12-row dependency table
    lane_rows = 2
    lane_rh = 32
    lane_top = 44
    lane_h = lane_top + lane_rows * lane_rh + 12'''),
    ('''        seq = [t for t in tasks if t["team"] == tm]
        for i, t in enumerate(seq):
            ty = round(lane_y + lane_top + i * lane_rh)
            bh = 24''',
     '''        seq = [t for t in tasks if t["team"] == tm]
        per_row = 3
        for i, t in enumerate(seq):
            ty = round(lane_y + lane_top + (i // per_row) * lane_rh)
            bh = 24'''),
    ('    rows_h = 356', '    rows_h = 392'),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')

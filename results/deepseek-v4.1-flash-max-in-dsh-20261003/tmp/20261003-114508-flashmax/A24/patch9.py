p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A24\build_a24.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('''    bars = []
    for tm, title, note in (("design", "design", "单队 · 不可并行"),''',
     '''    bars = []
    lane_block_top = lane_y
    for tm, title, note in (("design", "design", "单队 · 不可并行"),'''),
    ('''    # buffer band + deadline line (tall enough to cover both lanes)
    lane_block_top = 226
    lane_block_h = lane_y - 10 - lane_block_top''',
     '''    # buffer band + deadline line (tall enough to cover both lanes)
    lane_block_h = lane_y - 10 - lane_block_top'''),
    ('''    ty0 = lane_y + lane_h + 12''',
     '''    ty0 = lane_y - 10 + 14'''),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')

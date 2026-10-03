p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A24\build_a24.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('''    avail = W - 24 - 24 - 40 - 24
    if sum(col_w) > avail:
        k = avail / sum(col_w)
        col_w = [w * k for w in col_w]
    col_gap = (avail - sum(col_w)) / 6
    cols = []
    _x = 46.0
    for j, name in enumerate(col_names):
        cols.append((name, round(_x), round(col_w[j])))
        _x += col_w[j] + col_gap''',
     '''    avail = W - 24 - 24 - 40 - 24
    col_gap = 12.0
    if sum(col_w) + col_gap * 6 > avail:
        # keep every column at the width its longest value really needs: shrink the
        # generous ones only, instead of scaling everything and re-introducing clipping
        need = {j: max(text_width(col_names[j], 20, mono=(fams[j] is MONO)),
                       max(text_width(r[j], 20, mono=(fams[j] is MONO)) for r in rows_vals))
                for j in range(7)}
        slack = avail - col_gap * 6 - sum(need.values())
        assert slack >= 0, f"execution-board table needs {-slack:.0f}px more width"
        extra = [max(0.0, col_w[j] - need[j]) for j in range(7)]
        tot_extra = sum(extra) or 1.0
        col_w = [need[j] + slack * extra[j] / tot_extra for j in range(7)]
    else:
        col_gap = (avail - sum(col_w)) / 6
    cols = []
    _x = 46.0
    for j, name in enumerate(col_names):
        cols.append((name, math.ceil(_x), math.ceil(col_w[j])))
        _x += col_w[j] + col_gap'''),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')

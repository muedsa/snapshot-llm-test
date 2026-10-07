# -*- coding: utf-8 -*-
"""Raise every A07 map label to >= 20px (task hard requirement) and tidy the
info-panel strings so nothing truncates at the larger size."""
import io

P = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\A07\build_map_a07.py"
s = io.open(P, encoding="utf-8").read()
PAIRS = [
    ('row("%s %s　%d站 %d区间" % (lid, C.LNAME[lid], n, n - 1), xoff=30)',
     'row("%s %s　%d站 %d区间" % (lid, C.LNAME[lid], n, n - 1), size=20, xoff=30)'),
    ('"／".join(C.LNAME[l] for l in C.LINES_AT[sid])), size=18)',
     '"／".join(C.LNAME[l] for l in C.LINES_AT[sid])), size=20)'),
    ('row("无障碍站 %d ／ %d" % (okc, len(C.STATIONS)), size=19)',
     'row("无障碍站 %d ／ %d" % (okc, len(C.STATIONS)), size=20)'),
    ('row("非无障碍站 %d（仍保留在线路上）" % len(bad), size=18, color=ACC_OFF, bold=True)',
     'row("非无障碍站 %d（仍在线路上）" % len(bad), size=20, color=ACC_OFF, bold=True)'),
    ('row("　".join("%s %s" % (s, C.NAME[s]) for s in bad[i:i + 2]), size=18,',
     'row("　".join("%s %s" % (s, C.NAME[s]) for s in bad[i:i + 2]), size=20,'),
    ('row("跨线交叉 %d 处：%s × %s" % (len(CROSS), C.LNAME["G"], C.LNAME["B"]), size=18)',
     'row("跨线交叉 %d 处：%s × %s" % (len(CROSS), C.LNAME["G"], C.LNAME["B"]), size=20)'),
    ('row("站间区间 %d 段 · 双向可走" % len(C.EDGES), size=18)',
     'row("站间区间 %d 段 · 双向可走" % len(C.EDGES), size=20)'),
    ('n["transfers"]), size=18, xoff=30)',
     'n["transfers"]), size=20, xoff=30)'),
    ('x=x0 + 36, y=y, w=258, h=24, size=17,',
     'x=x0 + 36, y=y, w=258, h=26, size=20,'),
    ('kids.append(D.box(px - 104, py + 108, 208, 30, color=HALO, radius=7))',
     'kids.append(D.box(px - 106, py + 108, 212, 32, color=HALO, radius=7))'),
    ('kids.append(D.text_el("跨线交叉 · 不可换乘", x=px - 104, y=py + 112, w=208, h=24,\n'
     '                              size=19, color=MUTED, align="CENTER", font=D.UI))',
     'kids.append(D.text_el("跨线交叉 · 不可换乘", x=px - 106, y=py + 112, w=212, h=28,\n'
     '                              size=20, color=MUTED, align="CENTER", font=D.UI))'),
    ('x=44, y=904, w=1512, h=26, size=18, color=MUTED, font=D.UI))',
     'x=44, y=904, w=1512, h=28, size=20, color=MUTED, font=D.UI))'),
    ('x=44, y=932, w=1512, h=26, size=18, color=MUTED, font=D.UI))',
     'x=44, y=936, w=1512, h=28, size=20, color=MUTED, font=D.UI))'),
]
missing = []
for a, b in PAIRS:
    if a not in s:
        missing.append(a[:60])
    s = s.replace(a, b)
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("missing patterns:", missing)

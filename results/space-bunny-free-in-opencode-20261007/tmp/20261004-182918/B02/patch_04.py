# -*- coding: utf-8 -*-
"""Patch build_04.py: strikethrough position, remove floating select dot, tab bar fit."""
p = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\B02\build_04.py"
s = open(p, encoding="utf-8").read()
reps = [
    ('        out.append(D.dashed(x + 14, x + w - 14, y + h - 8, "#B7AE9AFF", 1.5, 8, 6))',
     '        out.append(D.dashed(x + 18, x + w - 18, y + h * 0.52, "#B0A694FF", 1.6, 8, 6))'),
    ('''        k.append(wide_chip(x, y, COLW, lab + " ✓", fg=G.WHITE, bg=G.IRON, size=18))
        k.append(G.dot(x + COLW - 20, y + 14, 6, G.BRASS))
    elif state == "sel2":''',
     '''        k.append(wide_chip(x, y, COLW, lab + " ✓", fg=G.WHITE, bg=G.IRON, size=18))
    elif state == "sel2":'''),
    ("CB = 1200", "CB = 1188"),
    ("TB = 1436", "TB = 1424"),
    ("    k.append(G.illus_tool(tx + 12, TB + 16, 44, glyph,",
     "    k.append(G.illus_tool(tx + 12, TB + 12, 44, glyph,"),
    ('    k.append(D.text_el(lab, x=tx, y=TB + 66, w=80, h=20, size=14,',
     '    k.append(D.text_el(lab, x=tx, y=TB + 64, w=80, h=20, size=14,'),
]
for a, b in reps:
    if a not in s:
        raise SystemExit("NOT FOUND: %r" % a[:70])
    s = s.replace(a, b)
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched build_04.py")

import io
p = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\gen_handbook.py"
s = io.open(p, encoding="utf-8").read()
# page 1: card 2 shorter, illustration further right so the caption never crosses the page edge
s = s.replace("""    h2 = 284
    p.card(48, y, 1104, h2, "2 · 响应：两条分支", ACCENT)""",
              """    h2 = 240
    p.card(48, y, 1104, h2, "2 · 响应：两条分支", ACCENT)""")
s = s.replace('p.d.box(bx, by, bw, 214, "#F0FDF9FF"', 'p.d.box(bx, by, bw, 170, "#F0FDF9FF"')
s = s.replace('p.d.box(bx + bw + 24, by, bw, 214, "#FEF2F2FF"', 'p.d.box(bx + bw + 24, by, bw, 170, "#FEF2F2FF"')
s = s.replace("limit=by + 204)", "limit=by + 160)")
s = s.replace("fx, fy, fw, fh = 848, y + 58, 240, 144", "fx, fy, fw, fh = 868, y + 58, 240, 144")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("page1 v6 tweaks applied")
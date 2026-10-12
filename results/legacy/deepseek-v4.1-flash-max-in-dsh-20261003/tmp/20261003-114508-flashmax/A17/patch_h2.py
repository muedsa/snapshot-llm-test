import io
p = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\gen_handbook.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace("    h2 = 216\n", "    h2 = 240\n")
s = s.replace('p.d.box(bx, by, bw, 138, "#F0FDF9FF"', 'p.d.box(bx, by, bw, 156, "#F0FDF9FF"')
s = s.replace('p.d.box(bx + bw + 24, by, bw, 138, "#FEF2F2FF"', 'p.d.box(bx + bw + 24, by, bw, 156, "#FEF2F2FF"')
s = s.replace("limit=by + 132)", "limit=by + 146)")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("card2 adjusted")
import io
p = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\gen_handbook.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace("    h1 = 272\n", "    h1 = 296\n")
s = s.replace("    h3 = 620\n", "    h3 = 596\n")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("heights adjusted")
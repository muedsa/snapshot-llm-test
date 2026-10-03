import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from dslkit import Doc
d = Doc(1000, 500, background="#FFFFFFFF")
d.box(0,0,1000,500,"#FFFFFFFF")
rows = [
  ("mono-20-default", "Noto Sans Mono CJK SC", 20, "HHHHHHHHHH"),
  ("mono-40", "Noto Sans Mono CJK SC", 40, "HHHHHHHHHH"),
  ("nofont-20", None, 20, "HHHHHHHHHH"),
  ("sans-20", "Noto Sans CJK SC", 20, "HHHHHHHHHH"),
  ("dejavu-20", "DejaVu Sans Mono", 20, "HHHHHHHHHH"),
]
for i,(name,fam,sz,txt) in enumerate(rows):
    y = 30 + i*90
    d.text(10, y, name, 16, "#334155FF")
    kw = {}
    d.text(200, y, txt, sz, "#000000FF", family=fam)
open(r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\probe-size.snapshot","w",encoding="utf-8").write(d.finish())
print("ok")
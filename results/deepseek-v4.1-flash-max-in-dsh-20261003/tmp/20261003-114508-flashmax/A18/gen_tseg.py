import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from dslkit import Doc
d = Doc(400, 300, background="#FFFFFFFF")
d.box(0,0,400,300,"#FFFFFFFF")
d.seg(40, 40, 360, 260, "#1D4ED8FF", 6)      # diagonal
d.seg(40, 260, 360, 40, "#D92D20FF", 6)      # other diagonal
d.seg(40, 150, 360, 150, "#0E9F8FFF", 6)     # horizontal
d.seg(200, 20, 200, 280, "#D97706FF", 6)     # vertical
open(r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A18\t-seg.snapshot","w",encoding="utf-8").write(d.finish())
print("ok")
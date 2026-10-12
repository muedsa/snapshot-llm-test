import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from dslkit import Doc

TXT = "ABCDEFGHIJ0123456789"
fams = [("mono20", "Noto Sans Mono CJK SC", 20), ("mono20b", "Noto Sans Mono CJK SC", 20),
        ("sans20", "Noto Sans CJK SC", 20), ("mono16", "Noto Sans Mono CJK SC", 16)]
d = Doc(1200, 420, background="#FFFFFFFF")
d.box(0, 0, 1200, 420, "#FFFFFFFF")
d.raw('<Positioned left="0" top="0"><Container width="4" height="420" color="#FF0000FF"/></Positioned>')
for r in range(4):
    y = 40 + r * 90
    d.raw(f'<Positioned left="0" top="{y}"><Container width="1200" height="1" color="#00AA00FF"/></Positioned>')
    for c in range(20):
        x = 100 + c * 50
        d.raw(f'<Positioned left="{x}" top="{y-30}"><Container width="1" height="60" color="#0000FFFF"/></Positioned>')
        d.text(x, y, TXT[c], 20, "#000000FF", family="Noto Sans Mono CJK SC")
    d.text(10, y, f"row{r} mono20", 18, "#334155FF")
open(r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\probe-adv.snapshot", "w", encoding="utf-8").write(d.finish())
print("ok")
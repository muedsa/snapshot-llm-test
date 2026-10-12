import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from dslkit import Doc, MONO, CJK

rows = [
    ("Noto Sans Mono CJK SC", "ABCDEFGHIJ"),
    ("Noto Sans Mono CJK SC", "0123456789"),
    ("Noto Sans Mono CJK SC", "\u5b57\u4f53\u5b57\u4f53\u5b57\u4f53\u5b57\u4f53\u5b57\u4f53"),
    ("Noto Sans CJK SC", "ABCDEFGHIJ"),
    ("Noto Sans CJK SC", "\u5b57\u4f53\u5b57\u4f53\u5b57\u4f53\u5b57\u4f53\u5b57\u4f53"),
]
sizes = [20, 24, 28]
d = Doc(1200, 600, background="#FFFFFFFF")
d.box(0, 0, 1200, 600, "#FFFFFFFF")
d.box(0, 0, 200, 600, "#E2E8F0FF")
d.raw('<Positioned left="0" top="0"><Container width="1200" height="4" color="#FF0000FF"/></Positioned>')
for i, (fam, txt) in enumerate(rows):
    y = 60 + i * 90
    sz = sizes[i % len(sizes)]
    d.text(8, y + 8, f"{fam[:12]} {sz}", 18, "#334155FF", family=CJK)
    d.text(200, y, txt, sz, "#000000FF", family=fam)
open(r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\probe-metrics.snapshot", "w", encoding="utf-8").write(d.finish())
print("ok")
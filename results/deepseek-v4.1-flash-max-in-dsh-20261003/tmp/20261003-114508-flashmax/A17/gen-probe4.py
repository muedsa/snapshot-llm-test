import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from dslkit import Doc
d = Doc(1000, 560, background="#FFFFFFFF")
d.box(0,0,1000,560,"#FFFFFFFF")
# row A: alpha variants over white and over dark
d.text(20, 20, "A: \u5c3e\u90e8 alpha \u5bf9\u6bd4", 20, "#334155FF")
sw = ["#1D4ED8FF", "#1D4ED880", "#1D4ED840", "#1D4ED800"]
for i,c in enumerate(sw):
    d.box(40+i*120, 60, 100, 60, c, radius=8)
    d.text(40+i*120, 128, c, 16, "#334155FF", family="Noto Sans Mono CJK SC")
d.box(520, 60, 440, 60, "#0F172AFF")
for i,c in enumerate(sw):
    d.box(540+i*100, 72, 80, 36, c, radius=6)
# row B: letterSpacing on mono code
d.text(20, 190, "B: letterSpacing", 20, "#334155FF")
code = '<Container width="200" height="100" color="#1D4ED8FF"/>'
d.text(40, 224, code, 20, "#0F172AFF", family="Noto Sans Mono CJK SC")
d.text(40, 260, code, 20, "#0F172AFF", family="Noto Sans Mono CJK SC", spacing=0.5)
d.text(40, 296, code, 20, "#0F172AFF", family="Noto Sans Mono CJK SC", spacing=1)
d.text(40, 332, code, 20, "#0F172AFF", family="Noto Sans Mono CJK SC", spacing=2)
# row C: CJK body vs latin words width check
d.text(20, 380, "C: \u6df7\u6392\u5bbd\u5ea6\u6821\u9a8c", 20, "#334155FF")
d.text(40, 412, "Snapshot \u628a\u5e03\u5c40\u5199\u6210\u4e00\u68f5\u6811", 24, "#0F172AFF")
d.text(40, 452, "HTTP 400 \u9519\u8bef\u4f53\u662f JSON", 24, "#0F172AFF")
d.text(40, 492, "PNG 200 \u5b57\u8282", 24, "#0F172AFF")
open(r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\probe-alpha.snapshot","w",encoding="utf-8").write(d.finish())
print("ok")
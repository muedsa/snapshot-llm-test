import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from dslkit import Doc

MONO="Noto Sans Mono CJK SC"
d = Doc(1000, 560, background="#FFFFFFFF")
d.box(0,0,1000,560,"#FFFFFFFF")
d.text(20, 16, "P1: CDATA multiline", 20, "#334155FF")
body = '<Raw><![CDATA[<Container width="200" height="100"\n           color="#1D4ED8FF"/>\n<Text fontSize="24">\u4f60\u597d Snapshot</Text>]]></Raw>'
for i in range(4):
    d.text(40, 48+ i*30, "X"*44 + "|", 20, "#CBD5E1FF", family=MONO)
d.raw(f'<Positioned left="40" top="48"><Text fontSize="20" color="#0F172AFF" fontFamily="{MONO}" fontStyle="NORMAL">{body}</Text></Positioned>')

d.text(20, 200, "P2: letterSpacing 0 / 3 / 6 (mono 20)", 20, "#334155FF")
for i,sp in enumerate([0,3,6]):
    d.text(40, 232+i*30, 'color="#1D4ED8FF"', 20, "#0F172AFF", family=MONO, spacing=(sp or None))
for i in range(3):
    d.text(40, 232+i*30, "", 20, "#00000000")
    d.text(560, 232+i*30, f"sp={[0,3,6][i]}", 18, "#334155FF")
d.text(20, 340, "P3: single Text with real newline via attr", 20, "#334155FF")
d.raw('<Positioned left="40" top="372"><Text fontSize="18" color="#0F172AFF" fontFamily="Noto Sans Mono CJK SC" text="line1&#10;line2"/></Positioned>')
d.text(20, 430, "P4: Raw without CDATA containing <", 20, "#334155FF")
d.raw('<Positioned left="40" top="462"><Text fontSize="18" color="#0F172AFF" fontFamily="Noto Sans Mono CJK SC"><Raw><![CDATA[<a> &amp; &lt; b]]></Raw></Text></Positioned>')
d.text(20, 500, "P5: &lt; entity in normal text", 20, "#334155FF")
d.raw('<Positioned left="40" top="530"><Text fontSize="18" color="#0F172AFF" fontFamily="Noto Sans Mono CJK SC">A&lt;B &amp; C&gt;D</Text></Positioned>')
open(r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\probe-cdata.snapshot","w",encoding="utf-8").write(d.finish())
print("ok")
import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from dslkit import Doc
MONO = "Noto Sans Mono CJK SC"
d = Doc(760, 300, background="#FFFFFFFF")
d.box(0, 0, 760, 300, "#FFFFFFFF")
rows = [
    ("raw-amp",     "A & B"),
    ("amp-entity",  "A &amp; B"),
    ("lt-entity",   "A &lt; B"),
    ("gt-entity",   "A &gt; B"),
    ("cdata",       "A < B > C"),
]
for i, (tag, txt) in enumerate(rows):
    y = 24 + i * 52
    d.text(16, y, tag, 18, "#94A3B8FF", family=MONO)
    d.raw(f'<Positioned left="200" top="{y}"><Text fontSize="26" color="#0F172AFF" '
          f'fontFamily="{MONO}"><Raw><![CDATA[{txt}]]></Raw></Text></Positioned>')
open(r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\entity-probe.snapshot", "w", encoding="utf-8").write(d.finish())
print("ok")
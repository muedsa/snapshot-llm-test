import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from dslkit import Doc
MONO="Noto Sans Mono CJK SC"
# T1: Stack with width/height attrs directly
t1 = '<Snapshot background="#FFFFFFFF" type="png"><Stack width="200" height="80" alignment="TOP_LEFT" fit="EXPAND"><Positioned left="10" top="10"><Container width="60" height="40" color="#1D4ED8FF" borderRadius="8"/></Positioned></Stack></Snapshot>'
open(r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\t-stack-size.snapshot","w",encoding="utf-8").write(t1)
# T2: real < > inside a normal Text (no CDATA)
d = Doc(700, 300, background="#FFFFFFFF")
d.box(0,0,700,300,"#FFFFFFFF")
d.raw('<Positioned left="20" top="20"><Text fontSize="22" color="#0F172AFF" fontFamily="' + MONO + '">A < B > C</Text></Positioned>')
d.raw('<Positioned left="20" top="60"><Text fontSize="22" color="#0F172AFF" fontFamily="' + MONO + '">a&lt;b</Text></Positioned>')
d.raw('<Positioned left="20" top="100"><Text fontSize="22" color="#0F172AFF" fontFamily="' + MONO + '"><Raw><![CDATA[  two  spaces]]></Raw></Text></Positioned>')
d.raw('<Positioned left="20" top="140"><Text fontSize="22" color="#0F172AFF" fontFamily="' + MONO + '">  two  spaces</Text></Positioned>')
open(r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\t-ltgt.snapshot","w",encoding="utf-8").write(d.finish())
print("ok")
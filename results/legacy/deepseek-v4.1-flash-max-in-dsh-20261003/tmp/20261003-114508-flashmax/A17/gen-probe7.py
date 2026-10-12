import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from dslkit import Doc
MONO="Noto Sans Mono CJK SC"
d = Doc(700, 320, background="#FFFFFFFF")
d.box(0,0,700,320,"#FFFFFFFF")
d.raw('<Positioned left="20" top="20"><Text fontSize="20" color="#0F172AFF" fontFamily="' + MONO + '"><Raw><![CDATA[A < B > C]]></Raw></Text></Positioned>')
d.raw('<Positioned left="20" top="55"><Text fontSize="20" color="#0F172AFF" fontFamily="' + MONO + '">a&lt;b</Text></Positioned>')
d.raw('<Positioned left="20" top="90"><Text fontSize="20" color="#0F172AFF" fontFamily="' + MONO + '"><Raw><![CDATA[  two  spaces]]></Raw></Text></Positioned>')
d.raw('<Positioned left="20" top="125"><Text fontSize="20" color="#0F172AFF" fontFamily="' + MONO + '">  two  spaces</Text></Positioned>')
d.raw('<Positioned left="20" top="160"><Text fontSize="20" color="#0F172AFF" fontFamily="' + MONO + '"><Raw><![CDATA[ &amp; ]]></Raw></Text></Positioned>')
d.raw('<Positioned left="20" top="195"><Text fontSize="20" color="#0F172AFF" fontFamily="' + MONO + '">&amp;</Text></Positioned>')
d.raw('<Positioned left="20" top="230"><Text fontSize="20" color="#0F172AFF" fontFamily="' + MONO + '"><Raw><![CDATA[<b>bold</b>]]></Raw></Text></Positioned>')
open(r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\t-ltgt2.snapshot","w",encoding="utf-8").write(d.finish())
print("ok")
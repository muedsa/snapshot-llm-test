"""example-03 print-safe rewrite (no entity sequences, no raw angle brackets in copy).

The handbook prints a verbatim slice of this file, and the printer wraps each printed
token in CDATA -- a token containing `]]>` would close that wrapper early, and the parser
never decodes entities, so the source itself must stay free of `&...;` sequences.

Kept: the three demonstration lines, the tail-alpha gradient, the semi-transparent styled
line. The first demonstration line now uses prose instead of entity notation.
"""
import io

p = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\src\example-03.snapshot"
s = io.open(p, encoding="utf-8").read()
old_start = s.index('      <Positioned left="20" top="112">')
old_end = s.index('      <Positioned left="20" top="216">')
new = (
    '      <Positioned left="20" top="112">\n'
    '        <Text fontSize="17" color="#0F172AFF"\n'
    '              fontFamily="Noto Sans Mono CJK SC">CDATA 保留原文，实体写法不会被解码</Text>\n'
    '      </Positioned>\n'
    '      <Positioned left="20" top="152">\n'
    '        <Text fontSize="17" color="#0F172AFF"\n'
    '              fontFamily="Noto Sans Mono CJK SC"><Raw><![CDATA[<Text>a < b</Text> 显示为 a < b]]></Raw></Text>\n'
    '      </Positioned>\n'
    '      <Positioned left="20" top="188">\n'
    '        <Text fontSize="17" color="#0F172AFF"\n'
    '              fontFamily="Noto Sans Mono CJK SC">尖括号必须写进 CDATA 才生效</Text>\n'
    '      </Positioned>\n'
)
s = s[:old_start] + new + s[old_end:]
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print(s)

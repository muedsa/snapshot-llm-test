"""A17 revision after the parent agent's entity confirmation.

Measured facts applied here (probe tmp/.../A17/entity-probe.png, request A17-REQ-0085):
  * `A &amp; B` renders the five literal characters `&amp;` -- the parser does NOT decode
    entities, so the handbook must not print entity-escaped code.
  * raw `&` inside <Raw><![CDATA[...]]></Raw> renders correctly.
Changes:
  * example-03: the whole example now contains no entity sequence at all -- the middle
    line shows the CDATA form that actually produces `<Text>` in the picture.
  * page 3: the "no entity decoding" bullet states the measured behaviour.
"""
import io

T = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17"

# ---- example-03 source ------------------------------------------------------
p = T + r"\src\example-03.snapshot"
s = io.open(p, encoding="utf-8").read()
old = """      <Positioned left="20" top="112">
        <Text fontSize="17" color="#0F172AFF"
              fontFamily="Noto Sans Mono CJK SC">裸写 A &lt; B &gt; C 不会还原成尖括号</Text>
      </Positioned>
      <Positioned left="20" top="152">
        <Text fontSize="17" color="#0F172AFF"
              fontFamily="Noto Sans Mono CJK SC"><Raw><![CDATA[<Raw><![CDATA[ A < B > C ]]>]]></Raw></Text>
      </Positioned>
      <Positioned left="20" top="188">
        <Text fontSize="17" color="#0F172AFF"
              fontFamily="Noto Sans Mono CJK SC"><Raw><![CDATA[CDATA 里能写 <Text> 这样的标签字样]]></Raw></Text>
      </Positioned>"""
new = """      <Positioned left="20" top="112">
        <Text fontSize="17" color="#0F172AFF"
              fontFamily="Noto Sans Mono CJK SC"><Raw><![CDATA[<Raw><![CDATA[ A < B > C ]]>]]></Raw></Text>
      </Positioned>
      <Positioned left="20" top="152">
        <Text fontSize="17" color="#0F172AFF"
              fontFamily="Noto Sans Mono CJK SC"><Raw><![CDATA[<Text>a < b</Text> 显示为 a < b]]></Raw></Text>
      </Positioned>
      <Positioned left="20" top="188">
        <Text fontSize="17" color="#0F172AFF"
              fontFamily="Noto Sans Mono CJK SC">尖括号必须写进 CDATA 才生效</Text>
      </Positioned>"""
assert old in s, "example-03 pattern not found"
s = s.replace(old, new)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("example-03 updated:", "&lt;" not in s and "&amp;" not in s)

# ---- handbook page 3 -------------------------------------------------------
p = T + r"\gen_handbook_final.py"
s = io.open(p, encoding="utf-8").read()
pairs = [
    ('("不解实体", "解析器不做 HTML 实体解码：实体写法会原样显示。"),',
     '("不解实体", "解析器不做实体解码：实体写法会按原文逐字画出，不会变成符号。"),'),
    ('p.d.text(fx, fy + fh + 78, "实体写法会照原样出现在图里。", 17, BODY)',
     'p.d.text(fx, fy + fh + 78, "实体写法会按原文逐字画出，不会变成符号。", 17, BODY)'),
    ('p.d.text(fx + 10, fy + 108, "实体写法不会还原", 13, "#0F172AFF", family=MONO)',
     'p.d.text(fx + 10, fy + 108, "实体写法不会还原", 13, "#0F172AFF", family=MONO)'),
]
for old, new in pairs:
    assert old in s, f"page 3 pattern not found: {old[:48]!r}"
    s = s.replace(old, new)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("gen_handbook_final page 3 updated")

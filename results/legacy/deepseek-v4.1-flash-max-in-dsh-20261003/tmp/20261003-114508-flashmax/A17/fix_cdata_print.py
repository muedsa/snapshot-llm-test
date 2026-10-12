"""Fix the A17 code printer: every printed token must be CDATA-wrapped.

The parser does not decode entities and does not accept raw `<` in a text node, so a
printed code line that contains `<` (which is all of them) has to be emitted as
`<Text ...><![CDATA[<Container width="200"/>></Text>]`-style CDATA. `escape=False` alone
is not enough -- that was exactly the `PARSE_ERROR Unexpected character '<' in TAG_NAME`
seen in A17-REQ-0087.

Also replaces the hand-written nested-CDATA demo in example-03: a literal `]]>` inside a
CDATA block closes it early, which is what produced the earlier RAWTEXT error.
"""
import io

T = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17"

# ---- 1. hbkit.code: wrap each token in CDATA when it needs it --------------
p = T + r"\hbkit.py"
s = io.open(p, encoding="utf-8").read()
old = """            _, segs, cont = item
            cx = x + 16 + (34 if cont else 0)
            for t, col in segs:
                d.text(round(cx, 2), cy, t, size, col, family=MONO, escape=False)
                cx += adv(t, size)"""
new = """            _, segs, cont = item
            cx = x + 16 + (34 if cont else 0)
            for t, col in segs:
                d.text(round(cx, 2), cy, cdata_if_needed(t), size, col, family=MONO,
                       escape=False)
                cx += adv(t, size)"""
assert old in s, "hbkit.code token loop not found"
s = s.replace(old, new)

helper = '''

def cdata_if_needed(s: str) -> str:
    """Wrap a printed-DSL token in CDATA unless it is plain text already.

    The service does not decode entities, so `&`/`<`/`>` must reach it verbatim *inside*
    CDATA: raw `<` in a text node is parsed as a tag and fails with TAG_NAME.
    """
    if "<" in s or ">" in s or "&" in s:
        assert "]]>" not in s, "token would close its own CDATA section"
        return "<![CDATA[" + s + "]]>"
    return s

'''
anchor = "\ndef cdata(text: str) -> str:"
assert anchor in s
s = s.replace(anchor, helper + "\ndef cdata(text: str) -> str:")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("hbkit.code now CDATA-wraps every printed token")

# ---- 2. example-03: drop the nested-CDATA line ----------------------------
p = T + r"\src\example-03.snapshot"
s = io.open(p, encoding="utf-8").read()
old = """              fontFamily="Noto Sans Mono CJK SC"><Raw><![CDATA[<Raw><![CDATA[ A < B > C ]]>]]></Raw></Text>"""
new = """              fontFamily="Noto Sans Mono CJK SC"><Raw><![CDATA[<Raw><![CDATA[ A < B ]]>]]></Raw></Text>"""
assert old in s
s = s.replace(old, new)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("example-03 nested-CDATA line simplified")

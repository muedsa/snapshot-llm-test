"""A11 probe: how can literal < > & be rendered without turning into visible entities?

The first page-1 render showed `A&lt;B&amp;C&gt;D`, i.e. the parser does NOT decode XML
entities in text nodes, so entity escaping is unusable for the invoice's SKU / literal
lines. This probe tests bare characters and CDATA.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MONO = "Noto Sans Mono CJK SC"


def doc(lines) -> str:
    p = ['<Snapshot background="#FFFFFFFF" type="png">',
         '<Container width="900" height="360">',
         '<Stack alignment="TOP_LEFT" fit="EXPAND">']
    y = 24
    for label, body in lines:
        p.append(f'<Positioned left="24" top="{y}"><Text fontSize="24" color="#0F172AFF" '
                 f'fontFamily="{MONO}">{label}</Text></Positioned>')
        p.append(f'<Positioned left="300" top="{y}">{body}</Positioned>')
        y += 56
    p += ['</Stack>', '</Container>', '</Snapshot>']
    return "\n".join(p) + "\n"


def main() -> None:
    variant = sys.argv[1]
    if variant == "bare":
        lines = [
            ("amp:", f'<Text fontSize="24" color="#1D4ED8FF" fontFamily="{MONO}">A &amp; B</Text>'),
            ("gt:", f'<Text fontSize="24" color="#1D4ED8FF" fontFamily="{MONO}">A &gt; B</Text>'),
            ("lt:", f'<Text fontSize="24" color="#1D4ED8FF" fontFamily="{MONO}">A &lt; B</Text>'),
        ]
    elif variant == "bare2":
        lines = [
            ("raw-amp:", f'<Text fontSize="24" color="#0E9F8FFF" fontFamily="{MONO}">A & B</Text>'),
            ("raw-gt:", f'<Text fontSize="24" color="#0E9F8FFF" fontFamily="{MONO}">A > B</Text>'),
            ("raw-both:", f'<Text fontSize="24" color="#0E9F8FFF" fontFamily="{MONO}">A & B > C</Text>'),
        ]
    elif variant == "bare3":
        lines = [
            ("raw-lt:", f'<Text fontSize="24" color="#D92D20FF" fontFamily="{MONO}">A < B</Text>'),
            ("raw-full:", f'<Text fontSize="24" color="#D92D20FF" fontFamily="{MONO}">A < B & C > D</Text>'),
            ("raw-sku:", f'<Text fontSize="24" color="#D92D20FF" fontFamily="{MONO}">A<B&C>D</Text>'),
        ]
    elif variant == "rawcdata":
        lines = [
            ("batch:", f'<Text fontSize="24" color="#0E9F8FFF" fontFamily="{MONO}">'
                       f'<Raw><![CDATA[批次：  A  07]]></Raw></Text>'),
            ("path:", f'<Text fontSize="24" color="#0E9F8FFF" fontFamily="{MONO}">'
                      f'<Raw><![CDATA[Path: C:\\work\\cards\\v2]]></Raw></Text>'),
            ("ltamp:", f'<Text fontSize="24" color="#0E9F8FFF" fontFamily="{MONO}">'
                       f'<Raw><![CDATA[A < B & C > D]]></Raw></Text>'),
        ]
    elif variant == "cdata":
        lines = [
            ("cdata:", f'<Text fontSize="24" color="#D97706FF" fontFamily="{MONO}"><![CDATA[A < B & C > D]]></Text>'),
        ]
    elif variant == "raw-bare":
        lines = [
            ("raw-amp:", f'<Text fontSize="24" fontFamily="{MONO}"><Raw>A &amp; B</Raw></Text>'),
            ("raw-lt:", f'<Text fontSize="24" fontFamily="{MONO}"><Raw>A &lt; B</Raw></Text>'),
            ("raw-space:", f'<Text fontSize="24" fontFamily="{MONO}"><Raw>批：  A  07</Raw></Text>'),
        ]
    else:
        lines = [("?", f'<Text fontSize="24">x</Text>')]
    out = os.path.join(HERE, f"probe-{variant}.snapshot")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc(lines))
    print("wrote", out)


if __name__ == "__main__":
    main()

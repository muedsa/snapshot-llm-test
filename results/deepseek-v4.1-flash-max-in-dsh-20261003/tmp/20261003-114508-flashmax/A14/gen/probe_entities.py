"""A14 · how does the parser handle < > & inside text?

K04 rendered literal "&lt;" so the escaping rule from dslkit is wrong for this service.
This probe puts six candidate spellings on one sheet; the answer decides how the card
generator emits the original title text.
"""
from __future__ import annotations

import os
import sys

TMP = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A14"
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from dslkit import Doc, MONO  # noqa: E402

ROWS = [
    ("html-entity", "A &lt; B &amp; C &gt; D"),
    ("numeric-entity", "A &#60; B &#38; C &#62; D"),
    ("fullwidth", "A ＜ B ＆ C ＞ D"),
    ("amp-verbatim", "A & B"),
    ("gt-verbatim", "A > B"),
    ("quote-verbatim", "A “ B ” C × D"),
]


def build() -> str:
    p = ['<Snapshot background="#FFFFFFFF" type="png">',
         '<Container width="1200" height="620">',
         '<Stack alignment="TOP_LEFT" fit="EXPAND">']
    for i, (key, s) in enumerate(ROWS):
        y = 24 + i * 100
        p.append(f'<Positioned left="24" top="{y}">'
                 f'<Text fontSize="20" color="#94A3B8" fontFamily="Noto Sans Mono CJK SC">'
                 f'{key}</Text></Positioned>')
        # the payload is injected verbatim - this file is deliberately not escaped
        p.append(f'<Positioned left="24" top="{y + 30}">'
                 f'<Text fontSize="52" color="#0F172A">{s}</Text></Positioned>')
    p += ['</Stack>', '</Container>', '</Snapshot>']
    return "\n".join(p) + "\n"


if __name__ == "__main__":
    path = os.path.join(TMP, "dsl", "probe.entities.v1.snapshot")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(build())
    print("written", path)

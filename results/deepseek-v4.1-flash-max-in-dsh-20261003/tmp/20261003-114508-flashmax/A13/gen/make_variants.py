"""A13 · direction-A refinement variants: how should the core express the stack?

Renders four 512x512 transparent candidates that differ only in the core group, so the
choice is made from real pixels rather than from a description.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from a13lib import Doc, TEAL, BLUE, AMBER, hexa, emit_mark, palette_color  # noqa: E402

TMP = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A13"

VARIANTS = {
    "v2a-noghost": dict(ghost=False, pal=palette_color(None)),
    "v2b-tealghost": dict(ghost=True, pal=palette_color(TEAL, 0x4D)),
    "v2c-blueghost": dict(ghost=True, pal=palette_color(BLUE, 0x52)),
    "v2d-amberhalo": dict(ghost=True, pal=palette_color(AMBER, 0x3D)),
}


def build(name: str) -> str:
    v = VARIANTS[name]
    d = Doc(512, 512, background="transparent")
    emit_mark(d, 256, 256, 384, v["pal"], ghost=v["ghost"])
    return d.finish()


def write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


if __name__ == "__main__":
    for name in VARIANTS:
        write(os.path.join(TMP, "dsl", f"symbol-color.{name}.snapshot"), build(name))
    print("variants written:", ", ".join(VARIANTS))

"""A13 · small-size legibility check.

Renders the chosen mark (direction A, no ghost) at real 32/48/64/96/128 px sizes through
the service, plus a true 32x32 icon, so the "recognisable at 32x32" requirement is judged
from pixels instead of from the 512 master.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from a13lib import Doc, PAPER, INK, SLATE, CARD, LINE, emit_mark, PAL_COLOR, CJK  # noqa: E402

TMP = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A13"


def thirty_two() -> str:
    d = Doc(32, 32, background="transparent")
    emit_mark(d, 16, 16, 384 / 512 * 32, PAL_COLOR, ghost=False)
    return d.finish()


def ladder() -> str:
    """A check sheet: the mark at five real sizes on the light brand background."""
    sizes = [32, 48, 64, 96, 128]
    gap, pad = 44, 40
    w = pad * 2 + sum(sizes) + gap * (len(sizes) - 1) + 136
    h = 260
    d = Doc(w, h, background=PAPER)
    d.box(0, 0, w, 74, INK)
    d.text(pad, 24, "叠光 Layerlight · 小尺寸检查", 22, "#F8FAFC")
    x = pad + 136
    base = 150
    for s in sizes:
        d.box(x - 12, base - s - 12, s + 24, s + 24, CARD, radius=10, border=f"1 SOLID {LINE}")
        emit_mark(d, x + s / 2, base - s / 2, 384 / 512 * s, PAL_COLOR, ghost=False)
        d.text(x - 12, base + 10, f"{s}px", 20, INK, w=s + 24, align="CENTER")
        x += s + gap
    d.text(pad, h - 46, "检查点：轮廓成立、两道透明间隔仍可辨", 18, "#475569")
    return d.finish()


def write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


if __name__ == "__main__":
    write(os.path.join(TMP, "dsl", "check.symbol-32.v1.snapshot"), thirty_two())
    write(os.path.join(TMP, "dsl", "check.size-ladder.v1.snapshot"), ladder())
    print("checks written")

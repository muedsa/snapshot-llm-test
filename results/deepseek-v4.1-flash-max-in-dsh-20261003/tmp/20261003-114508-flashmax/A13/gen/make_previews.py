"""A13 · generate the two candidate mark directions (512x512 transparent previews).

Direction A  "层窗 / pane-stack"    : concentric rounded-square panes, orthogonal.
Direction B  "聚光 / converge"      : shallow chevron layers converging on a core, diagonal.
Both are real DSL rendered by the service; the images are viewed and compared.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from a13lib import (Doc, INK, TEAL, BLUE, AMBER, hexa, rot_box, rot_bar,  # noqa: E402
                    emit_mark, PAL_COLOR)

TMP = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A13"


def preview_a() -> str:
    d = Doc(512, 512, background="transparent")
    emit_mark(d, 256, 256, 384, PAL_COLOR, ghost=True)
    return d.finish()


def preview_b() -> str:
    """Converging chevrons: three shallow V layers that funnel to a solid core.

    Components: 3 chevrons x 2 bars = 6 bars, plus the core -> but we group each
    chevron as one "layer" conceptually; only 5 drawn shapes.
    """
    d = Doc(512, 512, background="transparent")

    def chevron(apex_x, apex_y, back_x, dy, th, color):
        rot_bar(d, back_x, apex_y - dy, apex_x, apex_y, th, color)
        rot_bar(d, apex_x, apex_y, back_x, apex_y + dy, th, color)

    # outer layer (teal, transparent) -> mid layer (blue) -> front layer (ink)
    chevron(438, 256, 150, 172, 52, hexa(TEAL, 0xB3))
    chevron(398, 256, 172, 150, 52, hexa(BLUE, 0xCC))
    chevron(452, 256, 262, 108, 56, hexa(INK, 0xFF))

    # focus core: solid diamond inside the funnel
    rot_box(d, 214, 256, 84, 84, 45, color=hexa(AMBER, 0xFF), radius=16)
    return d.finish()


def write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


if __name__ == "__main__":
    write(os.path.join(TMP, "dsl", "preview-A.pane-stack.v1.snapshot"), preview_a())
    write(os.path.join(TMP, "dsl", "preview-B.converge.v1.snapshot"), preview_b())
    print("previews written")

"""Re-measure the mono advance against the shared calibration table.

The parent workstream reports `Noto Sans Mono CJK SC` = 0.5000 em/char, while my earlier
probe (tmp/.../A17/probe-adv.json) measured ~0.545-0.603. The difference matters: if the
real advance is smaller, every width estimate I made was conservative (text fits with room
to spare); if it is larger, some A17 blocks could be tight.

Method: render one 40-character mono line at 20 px, measure the ink span of the first and
last glyph with Pillow, and compare span/(n-1) with size*0.5 and size*0.603.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from dslkit import Doc  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MONO = "Noto Sans Mono CJK SC"
TEXT = "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"   # 40 H's


def main() -> None:
    d = Doc(1000, 200, background="#FFFFFFFF")
    d.box(0, 0, 1000, 200, "#FFFFFFFF")
    d.raw(f'<Positioned left="20" top="60"><Text fontSize="20" color="#000000FF" '
          f'fontFamily="{MONO}"><Raw><![CDATA[{TEXT}]]></Raw></Text></Positioned>')
    with open(os.path.join(HERE, "advance-check.snapshot"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(d.finish())
    print("wrote advance-check.snapshot")


if __name__ == "__main__":
    main()

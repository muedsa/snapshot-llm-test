#!/usr/bin/env python
"""A16 定稿局部放大：柱顶标签与网格线的关系、利润表、标注卡。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from PIL import Image

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
PREV = BASE / "tmp/run-20261011-01/A16/preview"
REGIONS = {
    "q4-tops": (900, 230, 1160, 400),
    "axis-zero": (60, 230, 460, 560),
    "profit-table": (56, 572, 760, 830),
    "callout": (772, 572, 1170, 830),
    "header": (40, 30, 1180, 135),
}


def main() -> None:
    png = BASE / (sys.argv[1] if len(sys.argv) > 1
                  else "tmp/run-20261011-01/A16/preview/corrected-report-v2.png")
    PREV.mkdir(parents=True, exist_ok=True)
    with Image.open(png) as s:
        s.load()
        im = s.convert("RGB")
    for name, box in REGIONS.items():
        c = im.crop(box)
        k = 3 if name in ("q4-tops", "axis-zero") else 2
        c.resize((c.width * k, c.height * k), Image.NEAREST).save(
            PREV / f"fixed-{name}-{k}x.png")
        print("->", (PREV / f"fixed-{name}-{k}x.png").as_posix(), c.size)


if __name__ == "__main__":
    main()
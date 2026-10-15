#!/usr/bin/env python
"""A16 原图放大裁切：把坐标轴、分组柱、利润卡与标注区放大到 2× 以便肉眼判读。"""
from __future__ import annotations

import os
from pathlib import Path

from PIL import Image

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
SRC = BASE / "tasks/A16-visual-data-forensics/inputs/flawed-report.png"
PREV = BASE / "tmp/run-20261011-01/A16/preview"

REGIONS = {
    "axis": (95, 265, 420, 600),
    "bars-q1q2": (200, 340, 620, 600),
    "bars-q3q4": (680, 160, 1090, 600),
    "profit-callout": (50, 640, 1230, 830),
    "header": (40, 25, 1240, 135),
    "legend": (850, 170, 1200, 220),
}


def main() -> None:
    PREV.mkdir(parents=True, exist_ok=True)
    with Image.open(SRC) as s:
        s.load()
        im = s.convert("RGB")
    for name, box in REGIONS.items():
        c = im.crop(box)
        c.resize((c.width * 2, c.height * 2), Image.NEAREST).save(
            PREV / f"flawed-{name}-2x.png")
        print("->", (PREV / f"flawed-{name}-2x.png").as_posix(), c.size)


if __name__ == "__main__":
    main()
"""A17 局部放大自检：把指定区域按整数倍放大成 PNG，供视觉工具逐块查看。

只做读取与重采样，不修改任何交付件；产物写 tmp/<run_id>/A17/preview/。
"""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A17"
PREV = SUITE_ROOT / "tmp" / RUN_ID / "A17" / "preview"

JOBS = [
    ("handbook-04", (360, 990, 850, 1300), 2, "hb4-illus"),
    ("handbook-04", (380, 1150, 830, 1290), 3, "hb4-glass"),
    ("example-04", (60, 20, 340, 110), 3, "ex4-glass"),
    ("example-04", (0, 0, 400, 240), 2, "ex4-full"),
    ("handbook-03", (380, 1090, 830, 1260), 3, "hb3-illus"),
]


def main() -> int:
    from PIL import Image
    PREV.mkdir(parents=True, exist_ok=True)
    for name, box, scale, tag in JOBS:
        im = Image.open(OUT / (name + ".png"))
        crop = im.crop(box)
        big = crop.resize((crop.width * scale, crop.height * scale), Image.NEAREST)
        p = PREV / (tag + ".png")
        big.save(p)
        print("%s -> %s %dx%d scale=%d" % (name, p.relative_to(SUITE_ROOT),
                                           big.width, big.height, scale))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

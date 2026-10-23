"""A07 旅行卡局部放大查看（生成 2x 裁剪图到 preview/）。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a07_io as IO  # noqa: E402

from PIL import Image  # noqa: E402

OUT = [
    ("top", (0, 0, 720, 300)),          # 页眉 + Q1 卡头与线路条
    ("q1-strip", (24, 190, 720, 300)),  # Q1 线路条
    ("q2-a", (0, 330, 720, 620)),       # Q2 卡头 + 普通旅程
    ("q2-b", (0, 600, 720, 860)),       # Q2 说明 + 无障碍旅程
    ("q3", (0, 840, 720, 1110)),        # Q3
    ("footer", (0, 1090, 720, 1280)),   # 页脚
]


def main() -> None:
    out, tmp = IO.dirs()
    src = out / "travel-card.png"
    im = Image.open(src).convert("RGB")
    print("src", src.relative_to(IO.ROOT), im.size)
    for name, box in OUT:
        c = im.crop(box)
        c = c.resize((c.width * 2, c.height * 2), Image.LANCZOS)
        dst = tmp / "preview" / f"cardv2-crop-{name}.png"
        c.save(dst)
        print("  ->", dst.relative_to(IO.ROOT), c.size)


if __name__ == "__main__":
    main()

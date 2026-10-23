"""局部放大查看：把预览 PNG 的指定矩形裁出来并放大，供实际看图核验。

用法：
  python -I tmp/<rid>/A08/gen/a08_crop.py v1 "共享通道入馆" 60 470 340 220
  python -I tmp/<rid>/A08/gen/a08_crop.py v1 x1 y1 w h [scale]

坐标按 1560×1080 画布像素；scale 默认 3。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
RID = os.environ.get("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")


def main() -> int:
    if len(sys.argv) < 6:
        print(__doc__)
        return 2
    version = sys.argv[1]
    label = sys.argv[2]
    x1, y1, w, h = (int(a) for a in sys.argv[3:7])
    scale = int(sys.argv[7]) if len(sys.argv) > 7 else 3
    src = HERE.parent / "preview" / f"{version}-wayfinding.png"
    if not src.exists():
        print(f"找不到 {src}")
        return 1
    img = Image.open(src).convert("RGB")
    box = (max(0, x1), max(0, y1), min(img.width, x1 + w), min(img.height, y1 + h))
    crop = img.crop(box)
    out = (HERE.parent / "preview" / f"{version}-crop-{label}.png")
    crop.resize((int(crop.width * scale), int(crop.height * scale)),
                Image.NEAREST).save(out, "PNG")
    print(f"{src.name} 尺寸 {img.size}")
    print(f"裁剪 {box}（{crop.width}x{crop.height}）×{scale} → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

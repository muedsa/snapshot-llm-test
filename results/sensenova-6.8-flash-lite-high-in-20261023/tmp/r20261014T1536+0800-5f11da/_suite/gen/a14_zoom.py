"""局部放大查看工具：把指定区域裁出并放大，用于确认小字号文字是否被裁。

用法：
  python -I a14_zoom.py --src <png> --box l,t,r,b [--scale 4] [--out <png>]
  python -I a14_zoom.py --cards --regions footer,label      # 全批拼接对比
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from PIL import Image

_LANCZOS = getattr(Image, "Resampling", Image).LANCZOS
BG = (226, 232, 240)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src")
    ap.add_argument("--box", help="l,t,r,b")
    ap.add_argument("--out")
    ap.add_argument("--scale", type=float, default=4)
    args = ap.parse_args()
    if not args.src:
        print(__doc__)
        return 2
    im = Image.open(args.src).convert("RGB")
    l, t, r, b = [int(v) for v in args.box.split(",")]
    cr = im.crop((l, t, r, b))
    cr = cr.resize((int(cr.width * args.scale), int(cr.height * args.scale)),
                   _LANCZOS)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        cr.save(args.out, format="PNG")
        print("->", args.out, cr.size)
    else:
        import sys
        sys.stdout.buffer.write(cr.tobytes())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

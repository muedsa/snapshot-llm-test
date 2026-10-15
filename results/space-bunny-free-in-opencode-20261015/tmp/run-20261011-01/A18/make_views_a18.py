#!/usr/bin/env python
"""A18 缩略与局部裁切：400px 宽缩略（题面要求）+ 三幕并排与逐幕放大。

启动基准：总任务根 (suite_root)。缩略只是观察手段，不替代原图；全部留在临时目录。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from PIL import Image

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
PREV = BASE / "tmp/run-20261011-01/A18/preview"


def main() -> None:
    src = BASE / (sys.argv[1] if len(sys.argv) > 1
                  else "outputs/run-20261011-01/A18/three-act-story.png")
    PREV.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as s:
        s.load()
        im = s.convert("RGB")
    W, H = im.size

    # 题面要求的 400px 宽缩略
    t = im.resize((400, round(H * 400 / W)), Image.LANCZOS)
    t.save(PREV / "thumb-400.png")
    # 再小的 200px，用来看极限情况下还剩多少信息
    t2 = im.resize((200, round(H * 200 / W)), Image.LANCZOS)
    t2.save(PREV / "thumb-200.png")

    # 逐幕裁切（2× 放大）
    for i, (x0, x1) in enumerate([(40, 524), (558, 1042), (1076, 1560)]):
        c = im.crop((x0, 104, x1, 960))
        c.resize((c.width * 2, c.height * 2), Image.LANCZOS).save(
            PREV / f"act{i+1}-2x.png")

    # 全图 60% 便于一屏比对
    k = 0.6
    im.resize((round(W * k), round(H * k)), Image.LANCZOS).save(PREV / "full-60pct.png")

    for p in ("thumb-400.png", "thumb-200.png", "act1-2x.png", "act2-2x.png",
              "act3-2x.png", "full-60pct.png"):
        print(p, Image.open(PREV / p).size)


if __name__ == "__main__":
    main()
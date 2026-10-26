# -*- coding: utf-8 -*-
"""A13 32×32 检查预览：预乘 alpha Lanczos 重采样 → 恢复未预乘，浅色底实际尺寸查看。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RUN_ID / "A13"
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "_suite"))

import PIL  # noqa: E402
from PIL import Image  # noqa: E402

print("PIL", PIL.__version__)

LIGHT = (248, 250, 252, 255)  # 浅色检查底


def make_thumb(src: Path, dst_thumb: Path, dst_view: Path, size: int = 32):
    im = Image.open(src).convert("RGBA")
    assert im.size == (512, 512), im.size
    # 1) 预乘
    premul = Image.new("RGBA", im.size)
    sp, dp = im.load(), premul.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, a = sp[x, y]
            dp[x, y] = (r * a // 255, g * a // 255, b * a // 255, a)
    # 2) Lanczos 缩到 size×size
    small = premul.resize((size, size), Image.LANCZOS)
    # 3) 恢复未预乘（alpha=0 处 RGB 置 0，不参与判断）
    un = Image.new("RGBA", (size, size))
    sp2, dp2 = small.load(), un.load()
    for y in range(size):
        for x in range(size):
            r, g, b, a = sp2[x, y]
            if a == 0:
                dp2[x, y] = (0, 0, 0, 0)
            elif a == 255:
                dp2[x, y] = (r, g, b, 255)
            else:
                dp2[x, y] = (min(255, r * 255 // a), min(255, g * 255 // a),
                             min(255, b * 255 // a), a)
    un.save(dst_thumb)
    # 4) 浅色底实际尺寸查看图（32px 内容 + 标注边框，便于在对话框中辨认）
    view = Image.new("RGBA", (size * 8 + 40, size * 8 + 40), LIGHT)
    view.paste(un, (20, 20), un)
    # 边框标出 32px 区域
    from PIL import ImageDraw  # noqa: PLC0415
    dr = ImageDraw.Draw(view)
    dr.rectangle([18, 18, 20 + size * 8 - 1, 20 + size * 8 - 1], outline=(148, 163, 184, 255))
    view.save(dst_view)
    # alpha 统计
    alphas = [un.getpixel((x, y))[3] for x in range(size) for y in range(size)]
    nz = [a for a in alphas if a > 0]
    print(f"{src.name}: thumb {size}px, alpha>0 px={len(nz)}, "
          f"alpha range=({min(nz) if nz else 0},{max(nz) if nz else 0})")


for name in ["preview-dir1-layers", "preview-dir2-ring"]:
    make_thumb(TMP / f"{name}.png", TMP / f"{name}-32.png", TMP / f"{name}-32-view.png")
print("done")

#!/usr/bin/env python
"""A15 并排对照与局部放大：把参考图与重建图并排放、并各出缩略与 2× 放大裁切。

启动基准：总任务根 (suite_root)。参考图仅用于观察比对，不嵌入交付图。
输出全部落在 tmp/run-20261011-01/A15/preview/。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from PIL import Image

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
REF = BASE / "tasks/A15-reference-reconstruction/inputs/reference.png"
PREV = BASE / "tmp/run-20261011-01/A15/preview"

REGIONS = {
    "sidebar": (0, 0, 260, 900),
    "header": (250, 10, 1420, 120),
    "kpi": (250, 125, 1400, 295),
    "chart": (250, 300, 1010, 600),
    "activity": (1020, 300, 1410, 600),
    "table": (250, 615, 1410, 855),
    "procard": (0, 735, 230, 890),
}


def main() -> None:
    rec = BASE / (sys.argv[1] if len(sys.argv) > 1
                  else "outputs/run-20261011-01/A15/reconstructed.png")
    PREV.mkdir(parents=True, exist_ok=True)
    with Image.open(REF) as s:
        s.load()
        a = s.convert("RGB")
    with Image.open(rec) as s:
        s.load()
        b = s.convert("RGB")
    W, H = a.size

    # ① 原尺寸并排（上参考 / 下重建），只缩到 70% 以便一屏内看清
    k = 0.70
    w2, h2 = int(W * k), int(H * k)
    sheet = Image.new("RGB", (w2, h2 * 2 + 12), (25, 25, 28))
    sheet.paste(a.resize((w2, h2), Image.LANCZOS), (0, 0))
    sheet.paste(b.resize((w2, h2), Image.LANCZOS), (0, h2 + 12))
    sheet.save(PREV / "compare-fullsize.png")

    # ② 缩略（25%），检查整体块面与色彩关系
    tw, th = int(W * 0.25), int(H * 0.25)
    th_sheet = Image.new("RGB", (tw, th * 2 + 8), (25, 25, 28))
    th_sheet.paste(a.resize((tw, th), Image.LANCZOS), (0, 0))
    th_sheet.paste(b.resize((tw, th), Image.LANCZOS), (0, th + 8))
    th_sheet.save(PREV / "compare-thumbnail-25pct.png")

    # ③ 逐区域 2× 并排放大（上参考 / 下重建）
    for name, box in REGIONS.items():
        ca, cb = a.crop(box), b.crop(box)
        w, h = ca.size
        s = Image.new("RGB", (w * 2, h * 2 * 2 + 8), (25, 25, 28))
        s.paste(ca.resize((w * 2, h * 2), Image.NEAREST), (0, 0))
        s.paste(cb.resize((w * 2, h * 2), Image.NEAREST), (0, h * 2 + 8))
        s.save(PREV / f"zoom-{name}-2x.png")

    print("->", PREV.as_posix())
    for p in sorted(PREV.glob("compare-*.png")):
        print("  ", p.name, Image.open(p).size)
    for p in sorted(PREV.glob("zoom-*.png")):
        print("  ", p.name, Image.open(p).size)


if __name__ == "__main__":
    main()
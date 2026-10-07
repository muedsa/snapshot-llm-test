# -*- coding: utf-8 -*-
"""A10 探针：测 ImageFiltered 输出边界如何随 sigma 扩张（供 composite-audit 引用）。"""
from __future__ import annotations

import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402

TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A10")
snapkit.configure("A10", os.path.join(ROOT, "outputs", "20261004-182918", "A10"), TMP)


def cell(x0, sigma, label):
    sub = D.el("Stack", {"fit": "EXPAND"}, [
        D.box(110, 70, 20, 20, color="#0F172AFF")])
    filtered = D.el("ImageFiltered", {"sigmaX": sigma, "sigmaY": sigma},
                    [D.el("Container", {"width": 240, "height": 160}, [sub])])
    tinted = D.el("ColorFiltered", {"color": "#F6B94A", "blendMode": "MULTIPLY"},
                  [filtered])
    node = D.el("Positioned", {"left": 0, "top": 0, "width": 240, "height": 160},
                [tinted])
    return [
        D.box(x0, 40, 240, 160, border="1 SOLID #000000FF"),
        node0 := D.el("Positioned", {"left": x0, "top": 40, "width": 240,
                                     "height": 160}, [tinted]),
        D.text_el(label, x=x0, y=10, w=240, h=18, size=13, color="#000000FF"),
        D.text_el("子树边界", x=x0, y=44, w=240, h=14, size=10, color="#000000FF"),
    ]


def main():
    kids = []
    for i, s in enumerate((0, 2, 6, 12)):
        kids += cell(i * 260, s, "sigma=%d" % s)
    dsl = D.snapshot([D.stack(kids, 1040, 240)], 1040, 240, bg="#FFFFFFFF")
    r = snapkit.render(dsl, "bounds-probe.png", "bounds-probe.snapshot", final=False)
    print("ok=", r.get("ok"), r.get("status"), r.get("image"), r.get("error"))
    p = os.path.join(TMP, "preview", "bounds-probe.png")
    im = Image.open(p).convert("RGB")

    def amber(x, y):
        px = im.getpixel((x, y))
        return abs(px[0] - 246) <= 3 and abs(px[1] - 185) <= 3 and abs(px[2] - 74) <= 5

    for i, s in enumerate((0, 2, 6, 12)):
        x0 = i * 260
        # 子树绝对范围 (x0+0, 40) - (x0+240, 200)
        xs = [x for x in range(x0 - 30, x0 + 280) if amber(x, 120)]
        ys = [y for y in range(0, 240) if amber(x0 + 120, y)]
        if not xs:
            print("sigma=%2d  no amber row (子树只有不透明方块)" % s)
            continue
        print("sigma=%2d  subtree=x[%d,%d] y[40,200]  amber x[%s,%s] y[%s,%s] "
              "=> left%+.0f right%+.0f top%+.0f bottom%+.0f"
              % (s, x0, x0 + 240, min(xs), max(xs), min(ys), max(ys),
                 min(xs) - x0, max(xs) - (x0 + 240), min(ys) - 40,
                 max(ys) - 200))


if __name__ == "__main__":
    main()
"""A18 自检视图：400px 宽缩略图 + 三个幕面板的局部放大图，供实际看图核验。

全部写到 tmp/<run_id>/A18/preview/，不覆盖已有文件。
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
SRC = SUITE_ROOT / "outputs" / RUN_ID / "A18" / "three-act-story.png"
OUT = SUITE_ROOT / "tmp" / RUN_ID / "A18" / "preview"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    from PIL import Image
    OUT.mkdir(parents=True, exist_ok=True)
    im = Image.open(SRC).convert("RGB")
    w, h = im.size
    assert (w, h) == (1600, 1000), (w, h)

    made = []
    # 1) 400px 宽缩略图：题面要求的第二查看尺度
    th = im.resize((400, int(400 * h / w)), Image.LANCZOS)
    p = OUT / "three-act-story-400w.png"
    th.save(p)
    made.append((str(p.relative_to(SUITE_ROOT)), th.size))

    # 2) 三个幕面板的 2× 放大（面板绝对坐标 x=40/560/1080, y=116, 480×836）
    for i, x in enumerate((40, 560, 1080), start=1):
        box = (x, 116, x + 480, 116 + 836)
        z = im.crop(box).resize((960, 1672), Image.LANCZOS)
        p = OUT / ("act%d-2x.png" % i)
        z.save(p)
        made.append((str(p.relative_to(SUITE_ROOT)), z.size))

    # 3) 幕一 vs 幕二的环带对比：并排裁同一高度带，便于直接比较间距
    box1 = (40 + 60, 116 + 300, 40 + 480 - 60, 116 + 780)
    box2 = (560 + 60, 116 + 300, 560 + 480 - 60, 116 + 780)
    a = im.crop(box1)
    b = im.crop(box2)
    cw, chh = a.size
    side = Image.new("RGB", (cw * 2 + 24, chh), (255, 255, 255))
    side.paste(a, (0, 0))
    side.paste(b, (cw + 24, 0))
    side = side.resize((int(side.width * 1.5), int(side.height * 1.5)), Image.LANCZOS)
    p = OUT / "act1-vs-act2-annulus.png"
    side.save(p)
    made.append((str(p.relative_to(SUITE_ROOT)), side.size))

    # 4) 幕三第三个簇的局部：核对扇形间距与颜色构成
    box3 = (1080 + 100, 116 + 560, 1080 + 400, 116 + 836)
    z = im.crop(box3).resize((900, 828), Image.LANCZOS)
    p = OUT / "act3-cluster3-2x.png"
    z.save(p)
    made.append((str(p.relative_to(SUITE_ROOT)), z.size))

    print(json.dumps({"source": str(SRC.relative_to(SUITE_ROOT)),
                      "source_size": [w, h],
                      "made": [{"path": a, "size": list(b)} for a, b in made]},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

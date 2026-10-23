"""A11 像素度量：按 JSON 清单逐块求墨迹列轮廓与紧致包围盒。

用途：比较等宽/比例字形宽度、判断双空格是否保留、量右对齐金额的小数点列位置、
以及为 text-map.json 求每处文字的实际 ink_box。

用法：SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a11_measure.py <spec.json>
spec.json 形如：
  {"image": "tmp/<rid>/A11/preview/probe4b-layout.png",
   "threshold": 190,
   "bands": [{"label": "B1", "x0": 246, "x1": 1160, "y0": 412, "y1": 450,
              "mode": "dark"}],
   "threshold": 190}
mode=dark：统计比 threshold 暗的像素（深色字/浅色底，默认）
mode=light：统计比 threshold 亮的像素（浅色字/深色底，例如 teal 上的白字）
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[4]
spec = json.loads(Path(sys.argv[1]).resolve().read_text(encoding="utf-8"))
img_path = Path(spec["image"])
if not img_path.is_absolute():
    img_path = ROOT / img_path
default_thr = spec.get("threshold", 190)

im_full = Image.open(img_path).convert("L")
results = []
for band in spec["bands"]:
    box = (int(band["x0"]), int(band["y0"]), int(band["x1"]), int(band["y1"]))
    mode = band.get("mode", "dark")
    thr = int(band.get("threshold", default_thr))
    im = im_full.crop(box)
    px = im.load()
    w, h = im.size
    cols, rows = [], []
    min_x, max_x, min_y, max_y = None, None, None, None
    for x in range(w):
        c = 0
        for y in range(h):
            v = px[x, y]
            on = v < thr if mode == "dark" else v > thr
            if on:
                c += 1
                if min_y is None or y < min_y:
                    min_y = y
                if max_y is None or y > max_y:
                    max_y = y
        cols.append(c)
        if c > 0:
            min_x = x if min_x is None else min_x
            max_x = x
    for y in range(h):
        rows.append(sum(1 for x in range(w) if (px[x, y] < thr if mode == "dark"
                                                else px[x, y] > thr)))
    blocks, x = [], 0
    while x < w:
        if cols[x] > 0:
            s = x
            while x < w and cols[x] > 0:
                x += 1
            blocks.append((s, x - 1))
        else:
            x += 1
    rec = {
        "label": band["label"], "box": list(box), "mode": mode,
        "dark_columns": sum(1 for c in cols if c > 0),
        "blocks": [{"x0": box[0] + a, "x1": box[0] + b, "width": b - a + 1}
                   for a, b in blocks],
        "gaps": [blocks[i + 1][0] - blocks[i][1] - 1
                 for i in range(len(blocks) - 1)],
        "ink_span": (blocks[-1][1] - blocks[0][0] + 1) if blocks else 0,
        "bbox": ([box[0] + min_x, box[1] + min_y, box[0] + max_x + 1, box[1] + max_y + 1]
                 if min_x is not None else None),
    }
    results.append(rec)
    print("%s  x=%d..%d y=%d..%d  [%s]  墨块 %d 个  bbox=%s"
          % (band["label"], box[0], box[2], box[1], box[3], mode, len(blocks),
             rec["bbox"]))
    if blocks:
        print("   块:", " ".join("%d(%d)" % (b["x0"], b["width"]) for b in rec["blocks"]))
        print("   间距:", rec["gaps"])

dest = img_path.with_suffix(".measure.json")
dest.write_text(json.dumps({"image": spec["image"], "threshold": default_thr,
                            "results": results}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8")
print("wrote", dest.relative_to(ROOT).as_posix())

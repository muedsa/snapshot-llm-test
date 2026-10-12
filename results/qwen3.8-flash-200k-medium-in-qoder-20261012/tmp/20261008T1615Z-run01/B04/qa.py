"""B04 QA 裁图：把成品图的局部放大存到 tmp 下（只用于看图，不进输出目录）。

用法（总任务根）：
  python tmp/<run_id>/B04/qa.py case-02 v03 60,500,1020,700,2
裁图框 x0,y0,x1,y1 为原图像素；scale 为放大倍数。输出 tmp/<run>/<B04>/<case>/qa/<version>-<n>.png。
"""
import os
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
tmp = root / "tmp" / rid / "B04"
out = root / "outputs" / rid / "B04"

case, version, box = sys.argv[1], sys.argv[2], sys.argv[3]
scale = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0
n = sys.argv[5] if len(sys.argv) > 5 else "crop"
x0, y0, x1, y1 = [int(v) for v in box.split(",")[:4]]

from PIL import Image  # noqa: E402
src = out / case / ("%s-preview.png" % version)
if not src.exists():
    src = out / case / ("%s.png" % version)
im = Image.open(src)
crop = im.crop((x0, y0, x1, y1))
if scale != 1.0:
    crop = crop.resize((int(crop.width * scale), int(crop.height * scale)), Image.LANCZOS)
dst = tmp / case / "qa" / ("%s-%s.png" % (version, n))
dst.parent.mkdir(parents=True, exist_ok=True)
crop.save(dst)
print("%s -> %s %sx%s" % (src.name, dst.relative_to(root).as_posix(),
                          crop.width, crop.height))

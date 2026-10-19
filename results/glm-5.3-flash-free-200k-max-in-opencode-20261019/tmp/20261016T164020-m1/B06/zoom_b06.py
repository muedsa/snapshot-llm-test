# -*- coding: utf-8 -*-
"""B06 放大切片：每件取 1–2 个密集区域原倍率裁剪，供逐件细看。"""
import os
import sys
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ.get("SNAPSHOT_RUN_ID", "20261016T164020-m1")
OUT = TASK_ROOT / "outputs" / RUN / "B06"
STEPS = TASK_ROOT / "tmp" / RUN / "B06" / "steps"
STEPS.mkdir(parents=True, exist_ok=True)

# case -> [(name, x0, y0, x1, y1, scale)]
zooms = {
    "case-01": [("a", 40, 810, 760, 1100, 1.4), ("b", 340, 220, 760, 560, 1.5)],
    "case-02": [("a", 20, 300, 720, 680, 1.5), ("b", 20, 1080, 720, 1280, 1.8)],
    "case-03": [("a", 90, 160, 480, 700, 1.5), ("b", 460, 220, 780, 700, 1.4)],
    "case-04": [("a", 40, 110, 1030, 300, 1.5), ("b", 300, 420, 1030, 610, 1.5)],
    "case-05": [("a", 24, 240, 410, 650, 1.5), ("b", 270, 240, 410, 660, 2.0)],
    "case-06": [("a", 20, 460, 820, 900, 1.3), ("b", 520, 620, 820, 790, 2.2)],
    "case-07": [("a", 40, 120, 980, 460, 1.4), ("b", 480, 450, 980, 760, 1.4)],
    "case-08": [("a", 24, 130, 400, 580, 1.8), ("b", 24, 800, 396, 960, 1.9)],
    "case-09": [("a", 640, 180, 1140, 500, 1.4), ("b", 60, 180, 660, 480, 1.4)],
    "case-10": [("a", 20, 480, 410, 820, 1.7), ("b", 20, 820, 410, 960, 1.7)],
}
made = []
for cs, zs in zooms.items():
    src = OUT / cs / "final.png"
    im = Image.open(src)
    for tag, x0, y0, x1, y1, sc in zs:
        crop = im.crop((x0, y0, min(x1, im.width), min(y1, im.height)))
        crop = crop.resize((int(crop.width * sc), int(crop.height * sc)),
                           Image.LANCZOS)
        p = STEPS / ("zoom-%s-%s.png" % (cs, tag))
        crop.save(p)
        made.append(str(p))
print("zooms:", len(made))
for m in made:
    print(m)

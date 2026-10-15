#!/usr/bin/env python
"""A15 卡片阴影探测：看参考图的白卡下方是否有极淡投影，以及参考图里的淡像素。"""
from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
OUTD = BASE / "tmp/run-20261011-01/A15/drafts"


def main() -> None:
    with Image.open(BASE / "tasks/A15-reference-reconstruction/inputs/reference.png") as s:
        s.load()
        ref = s.convert("RGB")
    with Image.open(BASE / "tmp/run-20261011-01/A15/preview/reconstructed-v2.png") as s:
        s.load()
        rec = s.convert("RGB")
    out = {}
    for tag, im in (("reference", ref), ("reconstructed", rec)):
        px = im.load()
        # KPI 卡 1 左右两侧：x 240..262 与 616..640，y 200..220
        out[tag] = {
            "left_of_card_x244_262": [f"#{px[x,210][0]:02X}{px[x,210][1]:02X}{px[x,210][2]:02X}"
                                      for x in range(240, 266)],
            "below_card_y282_296": [f"#{px[400,y][0]:02X}{px[400,y][1]:02X}{px[400,y][2]:02X}"
                                    for y in range(280, 300)],
            "above_card_y124_138": [f"#{px[400,y][0]:02X}{px[400,y][1]:02X}{px[400,y][2]:02X}"
                                    for y in range(122, 140)],
            "row190_ink_in_kpi": [x for x in range(275, 620)
                                  if sum(abs(px[x,190][k]-255) for k in range(3)) > 40][:12],
        }
    p = OUTD / "shadow-probe.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    for tag, v in out.items():
        print("==", tag)
        for k, val in v.items():
            print("  ", k, "=", val)


if __name__ == "__main__":
    main()
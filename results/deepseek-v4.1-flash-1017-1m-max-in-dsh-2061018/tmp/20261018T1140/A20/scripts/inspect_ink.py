"""Measure actual text ink inside each label card in the rendered PNG."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RUN / "A20"

png = sys.argv[1] if len(sys.argv) > 1 else "annotated-map-v004.png"
layout = json.loads((TMP / "layout-v004.json").read_text(encoding="utf-8"))
img = Image.open(TMP / "renders" / png).convert("RGB")
px = img.load()


def near(c, target, tol=45):
    return all(abs(c[i] - target[i]) <= tol for i in range(3))


BLUE = (29, 78, 216)
GOLD = (180, 83, 9)
DARK = (24, 38, 53)


def is_blue(c):
    return near(c, BLUE, 55) and c[2] - c[0] > 60


def is_gold(c):
    return near(c, GOLD, 55) and c[0] - c[2] > 60


def is_dark(c):
    return max(c) < 110 and near(c, DARK, 45)


def bbox(region, pred):
    l, t, r, b = region
    xs, ys = [], []
    for y in range(t, b):
        for x in range(l, r):
            if pred(px[x, y]):
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return [min(xs), min(ys), max(xs) + 1, max(ys) + 1]


rows = []
for mid, box in layout["boxes"].items():
    l, t, r, b = box
    # examine inside the card plus 2px to catch a spill over the border
    region = (int(l) + 1, int(t) + 1, int(r) - 1, int(b) - 1)
    name = bbox(region, is_dark)
    val = bbox((int(l) + 1, int(t) + 1, int(r) + 3, int(b) - 1),
               lambda c: is_blue(c) or is_gold(c))
    rows.append({"id": mid, "box": box, "name_ink": name, "value_ink": val})
    nm = "none" if name is None else f"x[{name[0]},{name[2]}] y[{name[1]},{name[3]}]"
    vm = "none" if val is None else f"x[{val[0]},{val[2]}] y[{val[1]},{val[3]}]"
    spill = ""
    if name and (name[0] < l or name[2] > r or name[1] < t or name[3] > b):
        spill += " NAME_SPILL"
    if val and (val[0] < l or val[2] > r or val[1] < t or val[3] > b):
        spill += " VALUE_SPILL"
    print(f"{mid} box=[{l:.0f},{t:.0f},{r:.0f},{b:.0f}] name {nm} | value {vm}{spill}")

print("spills:", [r["id"] for r in rows if any(
    ink is not None and (ink[0] < r["box"][0] or ink[1] < r["box"][1]
                         or ink[2] > r["box"][2] or ink[3] > r["box"][3])
    for ink in (r["name_ink"], r["value_ink"]))])
(TMP / "ink-inspect-v004.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

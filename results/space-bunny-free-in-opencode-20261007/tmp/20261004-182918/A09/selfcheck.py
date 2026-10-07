# -*- coding: utf-8 -*-
"""A09 delivery self-check on the delivered PNG + DSL + audit JSON."""
import json
import os
import re
from collections import Counter

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A09")
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A09")

png = os.path.join(OUT, "transform-atlas.png")
dsl = os.path.join(OUT, "transform-atlas.snapshot")
aud = os.path.join(OUT, "geometry-audit.json")

im = Image.open(png)
print("PNG size:", im.size, "mode:", im.mode, "format:", im.format)
print("PNG bytes:", os.path.getsize(png), " is real PNG:", open(png, "rb").read(8) == b"\x89PNG\r\n\x1a\n")

t = open(dsl, encoding="utf-8").read()
sizes = Counter(re.findall(r'fontSize="([\d.]+)"', t))
print("fontSize histogram:", dict(sorted(sizes.items(), key=lambda kv: float(kv[0]))))
small = [s for s in sizes if float(s) < 20]
print("font sizes below 20:", small)
print("text elements:", t.count("<Text "))
print("Transform elements:", t.count("<Transform "))
print("Stack elements:", t.count("<Stack "))
print("Positioned elements:", t.count("<Positioned "))
print("Image elements (must be 0):", t.count("<Image "))
print("clipBehavior=NONE count:", t.count('clipBehavior="NONE"'))

a = json.load(open(aud, encoding="utf-8"))
print("audit specimens:", len(a["specimens"]))
cells = [(s["cell_rect"][0], s["cell_rect"][1], s["cell_rect"][2], s["cell_rect"][3])
         for s in a["specimens"]]
print("unique cell sizes:", set((c[2], c[3]) for c in cells))
xs = sorted(set(c[0] for c in cells))
ys = sorted(set(c[1] for c in cells))
print("cell x positions:", xs, "-> gaps", [xs[i + 1] - xs[i] for i in range(len(xs) - 1)])
print("cell y positions:", ys, "-> gaps", [ys[i + 1] - ys[i] for i in range(len(ys) - 1)])
grid_w = xs[-1] + 300 - xs[0]
grid_h = ys[-1] + 250 - ys[0]
print("grid box:", grid_w, "x", grid_h, "left margin", xs[0], "right margin", 1600 - (xs[-1] + 300))
print("grid centred horizontally:", xs[0] == 1600 - (xs[-1] + 300))
# pivot must be the cell centre
ok = all(s["pivot_in_cell"] == [s["cell_rect"][0] + 150, s["cell_rect"][1] + 125]
         for s in a["specimens"])
print("pivot == cell centre for all specimens:", ok)
# stamp child 1:1
ok2 = all(s["stamp_child_rect"][2:] == [120, 120] for s in a["specimens"])
print("stamp child is 120x120 local pixels (1:1):", ok2)
# clearances
cl = [s["clearance_to_cell_border"] for s in a["specimens"]]
print("min clearance to cell border:", min(min(c.values()) for c in cl))
# transform nodes carry the full composite matrix
mm = re.findall(r'<Transform matrix="([^"]+)" origin="\(0,0\)" alignment="TOP_LEFT">', t)
print("Transform nodes with origin/alignment:", len(mm))
bad = []
for s, mstr in zip(a["specimens"], mm):
    want = "(" + ",".join(repr(round(v, 4)) if abs(v - round(v, 4)) > 1e-9 else "%.4f" % v
                          for v in s["matrix_column_major_4x4"]) + ")"
    nums = [float(x) for x in mstr.strip("()").split(",")]
    ref = s["matrix_column_major_4x4"]
    okm = len(nums) == 16 and all(abs(u - v) < 1e-3 for u, v in zip(nums, ref))
    if not okm:
        bad.append(s["id"])
print("DSL matrix == audit matrix for every specimen:", not bad, bad)
# orders / determinants
for s in a["specimens"]:
    print("  %s %-18s det=%+.0f  local_bbox=%s" % (s["id"], s["short_name"],
                                                   s["determinant"], s["final_local_bbox"]))
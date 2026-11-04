# -*- coding: utf-8 -*-
"""A15: refined reference measurement."""
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
TASK = "A15"
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
img = np.array(Image.open(SUITE_ROOT / "tasks" / "A15-reference-reconstruction" / "inputs"
                          / "reference.png").convert("RGB")).astype(int)

def col(x, y):
    return tuple(int(v) for v in img[y, x])

def hspan(y, x0=240, x1=1420, target=(255, 255, 255), tol=4, minw=40):
    runs, inrun, start = [], False, 0
    for x in range(x0, x1):
        ok = all(abs(int(img[y, x][i]) - target[i]) <= tol for i in range(3))
        if ok and not inrun:
            start, inrun = x, True
        elif not ok and inrun:
            runs.append((start, x - 1)); inrun = False
    if inrun:
        runs.append((start, x1 - 1))
    return [r for r in runs if r[1] - r[0] >= minw]

def vspan(x, y0=60, y1=890, target=(255, 255, 255), tol=4, minh=25):
    runs, inrun, start = [], False, 0
    for y in range(y0, y1):
        ok = all(abs(int(img[y, x][i]) - target[i]) <= tol for i in range(3))
        if ok and not inrun:
            start, inrun = y, True
        elif not ok and inrun:
            runs.append((start, y - 1)); inrun = False
    if inrun:
        runs.append((start, y1 - 1))
    return [r for r in runs if r[1] - r[0] >= minh]

print("y=150 (above KPI text):", hspan(150))
print("y=160:", hspan(160))
print("y=340 (chart title row):", hspan(340))
print("y=640 (table card):", hspan(640))
print("y=660:", hspan(660))
print("x=1050 (activity card):", vspan(1050))
print("x=1350 (right cards):", vspan(1350))
print("x=270 (left edge inside):", vspan(270))
print("x=1390:", vspan(1390))

BLUE = (37, 99, 235)
def bar_top(cx, y0=380, y1=560):
    for y in range(y0, y1):
        if all(abs(int(img[y, cx][i]) - BLUE[i]) <= 30 for i in range(3)):
            return y
    return None

centers = [383, 484, 585, 686, 787, 888]
print("bar tops:", [(c, bar_top(c)) for c in centers])
print("bar bottom:", [max(y for y in range(380, 560)
                          if all(abs(int(img[y, c][i]) - BLUE[i]) <= 30 for i in range(3)))
                      for c in centers])

# gridline rows: sample x=950 (right of bars) for the light grey lines
rows = []
for y in range(395, 550):
    c = col(950, y)
    if c != (255, 255, 255) and sum(c) > 620 and sum(c) < 745:
        rows.append((y, c))
print("gridline rows near x=950:", rows[:12])

# KPI card vertical bounds at x=600 (card 1 right part, no text)
print("KPI card vspan x=600:", vspan(600, 100, 320))
# table card bounds
print("table vspan x=1350:", vspan(1350, 600, 880))
# status pill colour samples
for y, x in ((740, 1100), (780, 1100), (820, 1100)):
    print("pill", y, x, col(x, y))
# nav selected pill
print("nav pill bg", col(100, 138), "sidebar bg", col(100, 300))
print("export button", col(1290, 66))
print("footer text row y=862 sample", col(300, 862))

# -*- coding: utf-8 -*-
"""A15: measure reference anchors by pixel scanning."""
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
REF = SUITE_ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"

img = np.array(Image.open(REF).convert("RGB")).astype(int)
H, W, _ = img.shape
print("ref size", W, H)

def col(x, y):
    return tuple(img[y, x])

print("sidebar", col(100, 400), "main", col(1200, 700), "card", col(400, 200))

# sidebar right edge: scan row 400 for the transition from dark to light
row = img[400]
edge = None
for x in range(200, 320):
    if row[x].sum() > 600 and row[x - 1].sum() < 400:
        edge = x
        break
print("sidebar right edge:", edge)

# main background vs card white: find card rows by scanning column x=300
def hspan(y, x0=240, x1=1400, target=(255, 255, 255), tol=6):
    runs = []
    inrun = False
    for x in range(x0, x1):
        c = img[y, x]
        ok = all(abs(int(c[i]) - target[i]) <= tol for i in range(3))
        if ok and not inrun:
            start, inrun = x, True
        elif not ok and inrun:
            runs.append((start, x - 1)); inrun = False
    if inrun:
        runs.append((start, x1 - 1))
    return [r for r in runs if r[1] - r[0] > 40]

def vspan(x, y0=100, y1=880, target=(255, 255, 255), tol=6):
    runs, inrun = [], False
    for y in range(y0, y1):
        c = img[y, x]
        ok = all(abs(int(c[i]) - target[i]) <= tol for i in range(3))
        if ok and not inrun:
            start, inrun = y, True
        elif not ok and inrun:
            runs.append((start, y - 1)); inrun = False
    if inrun:
        runs.append((start, y1 - 1))
    return [r for r in runs if r[1] - r[0] > 30]

print("white runs at y=200 (KPI row):", hspan(200))
print("white runs at y=450 (chart/activity):", hspan(450))
print("white runs at y=700 (table):", hspan(700))
print("white runs at x=300:", vspan(300))
print("white runs at x=1100:", vspan(1100))

# chart zero line: find the darkest horizontal gridline near the bottom of the chart
card_top, card_bottom = 310, 592
for y in range(500, 580):
    seg = img[y, 340:970]
    dark = np.sum(seg.sum(axis=1) < 700)
    if dark > 300:
        print("strong line at y", y, "count", dark)

# bars: scan row just above the axis for blue pixels
BLUE = (37, 99, 235)
for y in (500, 470):
    xs = [x for x in range(330, 990) if all(abs(int(img[y, x][i]) - BLUE[i]) <= 25 for i in range(3))]
    if xs:
        groups, cur = [], [xs[0]]
        for x in xs[1:]:
            if x - cur[-1] <= 2:
                cur.append(x)
            else:
                groups.append((cur[0], cur[-1])); cur = [x]
        groups.append((cur[0], cur[-1]))
        print(f"blue groups at y={y}:", groups)

# status pills
for y in (740, 780, 820):
    for x in (1080,):
        print("pill px", y, col(x, y))

# -*- coding: utf-8 -*-
"""Pixel-verify case-10's rain bars on the ACTUAL rendered PNG (C2).

The generator asserts bar_h == mm/max_mm*PLOT_H, but that only proves the DSL
is self-consistent -- it says nothing about whether the service drew those
rects. So this reads the PNG, finds each bar's top edge by scanning down its
centre column, and checks three things against chart_geom():

  1. every bar's measured height matches the intended height (+/- 1px),
  2. measured heights are proportional to rain_mm (the real C2 criterion),
  3. the Thursday bar is the only orange one, and its top is exactly PLOT_Y.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image

import case10

PNG = os.path.join(case10.OUT, "case-10-v2.png")
AXIS_Y = int(case10.PLOT_Y + case10.PLOT_H)


def close(c1, c2, tol=40):
    return all(abs(a - b) <= tol for a, b in zip(c1[:3], c2[:3]))


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


im = Image.open(PNG).convert("RGB")
px = im.load()
print("png size", im.size)

geom = case10.chart_geom()
worst = 0.0
worst_rel = 0.0
print("\n  day   mm  want_h  meas_h   d    want_top  meas_top  color")
for b in geom:
    cx = int(round(b["cx"]))
    want = rgb(b["color"])
    y = AXIS_Y - 1
    while y > int(case10.PLOT_Y) - 40 and close(px[cx, y], want):
        y -= 1
    meas_top = y + 1
    meas_h = AXIS_Y - meas_top
    worst = max(worst, abs(meas_h - b["h"]))
    print("  %s  %2d  %6.2f  %6d  %5.2f  %8.2f  %8d  %s"
          % (b["day"], b["mm"], b["h"], meas_h, abs(meas_h - b["h"]),
             b["y"], meas_top, "#F28C1A" if b["color"] == case10.PEAK_COLOR
             else "#28C7D8"))

print("\nmax |measured - intended| height error: %.2f px" % worst)
assert worst <= 1.5, "bar height does not match the intended geometry"

# ratio check on the measured pixels (C2)
measured = {}
for b in geom:
    cx = int(round(b["cx"]))
    want = rgb(b["color"])
    y = AXIS_Y - 1
    while y > int(case10.PLOT_Y) - 40 and close(px[cx, y], want):
        y -= 1
    measured[b["mm"]] = AXIS_Y - (y + 1)

ref_mm, ref_h = max(measured.items(), key=lambda kv: kv[0])
print("\nratio check vs %dmm (measured heights):" % ref_mm)
for mm in sorted(measured):
    want = mm / float(ref_mm)
    got = measured[mm] / float(ref_h)
    print("  %2dmm  want %.4f  measured %.4f  d %.4f"
          % (mm, want, got, abs(want - got)))
    assert abs(want - got) <= 0.02, "measured bars not proportional to rain_mm"

# the Thursday bar must be the only orange one and must top out at PLOT_Y
peak_bars = [b for b in geom if b["color"] == case10.PEAK_COLOR]
assert len(peak_bars) == 1, "expected exactly one highlighted bar"
pb = peak_bars[0]
assert int(round(pb["y"])) == int(case10.PLOT_Y), "peak bar must fill the plot"
assert int(round(pb["h"])) == int(case10.PLOT_H)
print("\npeak bar %s tops out at y=%d (PLOT_Y=%d) and is the only orange bar"
      % (pb["day"], int(round(pb["y"])), case10.PLOT_Y))
print("ALL PIXEL CHECKS PASS")

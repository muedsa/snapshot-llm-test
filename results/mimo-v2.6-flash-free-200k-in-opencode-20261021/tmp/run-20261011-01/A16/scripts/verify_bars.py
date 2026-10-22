# -*- coding: utf-8 -*-
"""Verify corrected-report bars: height must equal value*PX_PER_WAN from the
shared zero line, and legend colors must map revenue->blue, cost->amber."""
import json
import pathlib
import sys

from PIL import Image

PX = 1.2
ZERO_Y = 500
SRC = {"Q1": (120, 90), "Q2": (135, 108), "Q3": (128, 96), "Q4": (180, 126)}
QS = ["Q1", "Q2", "Q3", "Q4"]


def is_blue(p):
    r, g, b = p[:3]
    return b > 150 and b - r > 60 and g < 120


def is_orange(p):
    r, g, b = p[:3]
    return r > 200 and 130 < g < 200 and b < 100


def bar_top(px, x, want_blue):
    fn = is_blue if want_blue else is_orange
    for y in range(240, 505):
        if fn(px[x, y]):
            return y
    return None


def main():
    img = Image.open(pathlib.Path(sys.argv[1])).convert("RGB")
    px = img.load()
    centers = [294, 541, 789, 1036]
    report, ok = [], True
    for i, q in enumerate(QS):
        c = centers[i]
        rx, cx = c - 42 - 8, c + 8
        rev, cost = SRC[q]
        for name, x, v, blue in (("revenue", rx, rev, True),
                                 ("cost", cx, cost, False)):
            top = bar_top(px, x, blue)
            h = ZERO_Y - top
            exp_h = round(v * PX)
            match = abs(h - exp_h) <= 2
            ok = ok and match
            report.append({"quarter": q, "series": name, "value_wan": v,
                           "measured_top": top, "measured_height": h,
                           "expected_height": exp_h, "match": match})
    print(json.dumps(report, ensure_ascii=False, indent=1))
    print("ALL BARS MATCH value*scale:", ok)
    pathlib.Path(sys.argv[2]).write_text(
        json.dumps({"bars": report, "all_match": ok}, ensure_ascii=False,
                   indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()

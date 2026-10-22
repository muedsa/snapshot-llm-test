# -*- coding: utf-8 -*-
"""A16 flawed-report.png forensic probe.

Measures the actual bar rectangles (blue/orange) per quarter, the y-axis
gridlines/labels, and the legend swatch colors, so every finding in
findings.json is backed by pixel evidence rather than assumption.

Usage: python probe_flawed.py <flawed.png> <out.json>
"""
import json
import pathlib
import sys

from PIL import Image


def classify(p):
    r, g, b = p[:3]
    if b > 150 and b - r > 60 and g < 120:
        return "blue"
    if r > 180 and g > 100 and b < 120 and r - b > 80:
        return "orange"
    return None


def col_runs(px, x, ya, yb, want):
    runs, s = [], None
    for y in range(ya, yb + 1):
        c = classify(px[x, y])
        if c == want and s is None:
            s = y
        elif c != want and s is not None:
            runs.append((s, y - 1))
            s = None
    if s is not None:
        runs.append((s, yb))
    return [r for r in runs if r[1] - r[0] > 8]


def main():
    img = Image.open(pathlib.Path(sys.argv[1])).convert("RGB")
    px = img.load()
    W, H = img.size
    # scan across the plot area for bar columns; collect contiguous runs
    out = {"size": [W, H], "bars": {}}

    # vertical scan lines every 2px across plot area x=200..1200, y=270..580
    for want, key in (("blue", "blue"), ("orange", "orange")):
        cols = {}
        for x in range(200, 1210, 2):
            rs = col_runs(px, x, 260, 585, want)
            if rs:
                # take the tallest run in this column
                top, bot = max(rs, key=lambda r: r[1] - r[0])
                cols[x] = (top, bot)
        # group contiguous columns into bars
        bars, cur = [], None
        for x in sorted(cols):
            if cur and x - cur["x1"] <= 4 and abs(cols[x][0] - cur["top"]) <= 6:
                cur["x1"] = x
                cur["top"] = min(cur["top"], cols[x][0])
                cur["bot"] = max(cur["bot"], cols[x][1])
            else:
                if cur:
                    bars.append(cur)
                cur = {"x0": x, "x1": x, "top": cols[x][0], "bot": cols[x][1]}
        if cur:
            bars.append(cur)
        out[key] = [{"x0": b["x0"], "x1": b["x1"], "top": b["top"],
                     "bot": b["bot"], "h": b["bot"] - b["top"] + 1}
                    for b in bars if b["x1"] - b["x0"] > 20]

    # gridline / axis label detection: find light horizontal lines in plot
    grid = []
    for y in range(250, 600):
        cnt = 0
        for x in range(250, 1150, 5):
            r, g, b = px[x, y][:3]
            if 200 < r < 245 and 200 < g < 245 and 200 < b < 250 and abs(r-g) < 12:
                cnt += 1
        if cnt > 150:
            grid.append(y)
    out["gridlines_y"] = grid

    # legend swatch sampling (approx from visible: two squares near top-right)
    out["legend_samples"] = {}
    for name, (lx, ly) in {"legend_left_sw": (940, 197),
                           "legend_right_sw": (1105, 197)}.items():
        out["legend_samples"][name] = list(px[lx, ly])

    # baseline: bottom of bars (shared zero-line in a truncated axis)
    allbot = [b["bot"] for b in out["blue"]] + [b["bot"] for b in out["orange"]]
    alltop_min = [b["top"] for b in out["blue"]] + [b["top"] for b in out["orange"]]
    out["bar_bottom_mode"] = max(set(allbot), key=allbot.count)
    out["bar_top_min"] = min(alltop_min)

    p = pathlib.Path(sys.argv[2])
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("probe ->", p.as_posix())
    print("blue bars:", out["blue"])
    print("orange bars:", out["orange"])
    print("gridlines_y:", out["gridlines_y"])
    print("legend:", out["legend_samples"])
    print("bar_bottom_mode:", out["bar_bottom_mode"])


if __name__ == "__main__":
    main()

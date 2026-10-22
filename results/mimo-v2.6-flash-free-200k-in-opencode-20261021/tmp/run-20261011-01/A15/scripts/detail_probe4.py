# -*- coding: utf-8 -*-
"""A15 detail probe v4: gridline x-extents (excluding label glyphs),
bar geometry + corner radius."""
import json
import pathlib
from PIL import Image

ROOT = pathlib.Path(".")
REF = ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
OUT = ROOT / "tmp" / "run-20261011-01" / "A15"
img = Image.open(REF).convert("RGB")
px = img.load()


def lum(p):
    return (p[0] * 299 + p[1] * 587 + p[2] * 114) // 1000


R = {}

# gridline rows: longest run of gridline-ish color (200<=lum<=244) so
# label-glyph AA fragments can't skew the extent
gl = {}
for y in (405, 441, 477, 513, 549):
    runs, s = [], None
    for x in range(270, 1000):
        ok = 200 <= lum(px[x, y]) <= 244
        if ok and s is None:
            s = x
        elif not ok and s is not None:
            runs.append((s, x - 1))
            s = None
    if s is not None:
        runs.append((s, 999))
    best = max(runs, key=lambda r: r[1] - r[0]) if runs else None
    gl[str(y)] = [best[0], best[1], best[1] - best[0] + 1] if best else None
R["gridline_x_by_row"] = gl

# gridline vertical thickness at x500
for y0 in (405, 441, 477, 513, 549):
    col = [y for y in range(y0 - 3, y0 + 4) if 200 <= lum(px[500, y]) <= 244]
    R.setdefault("gridline_thickness", {})[str(y0)] = col

# bars: exact boxes (blue mask), top rows width profile for radius
BLUE = lambda p: p[2] - p[0] > 100 and p[2] > 180
bars = []
for i in range(6):
    x0 = 340 + i * 101
    xs, ys = [], []
    for y in range(400, 555):
        for x in range(x0, x0 + 90):
            if BLUE(px[x, y]):
                xs.append(x)
                ys.append(y)
    box = [min(xs), min(ys), max(xs), max(ys)]
    # top-corner profile: first blue x per row (first 10 rows)
    prof = {}
    for dy in range(1, 11):
        y = box[1] + dy
        row = [x for x in range(box[0] - 4, box[2] + 5) if BLUE(px[x, y])]
        prof[str(dy)] = row[0] - box[0] if row else None
    # bottom-corner profile: last rows
    prof_b = {}
    for back in range(1, 9):
        y = box[3] - back + 1
        row = [x for x in range(box[0] - 4, box[2] + 5) if BLUE(px[x, y])]
        prof_b[str(back)] = row[0] - box[0] if row else None
    bars.append({"box": box, "top_dx": prof, "bot_dx": prof_b})
R["bars"] = bars

# month label glyph boxes (all six, now correct window y558..577)
months = {}
for i, m in enumerate(("Apr", "May", "Jun", "Jul", "Aug", "Sep")):
    cx = (357 + 410) // 2 + i * 101
    xs, ys = [], []
    for y in range(556, 578):
        for x in range(cx - 55, cx + 56):
            if lum(px[x, y]) < 160:
                xs.append(x)
                ys.append(y)
    months[m] = [min(xs), min(ys), max(xs), max(ys)] if xs else None
R["month_glyphs"] = months

# y-label glyph boxes re-measure (lum<160, correct windows)
yl = {}
for v, gy in ((120, 405), (90, 441), (60, 477), (30, 513), (0, 549)):
    xs, ys = [], []
    for y in range(gy - 12, gy + 12):
        for x in range(270, 330):
            if lum(px[x, y]) < 160:
                xs.append(x)
                ys.append(y)
    yl[str(v)] = [min(xs), min(ys), max(xs), max(ys)] if xs else None
R["y_label_glyphs"] = yl

(OUT / "detail-measured-v4.json").write_text(
    json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(R, ensure_ascii=False, indent=1))

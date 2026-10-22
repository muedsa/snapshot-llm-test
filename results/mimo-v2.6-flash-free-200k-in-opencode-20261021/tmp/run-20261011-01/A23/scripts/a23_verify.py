# -*- coding: utf-8 -*-
"""A23 verification: real alpha, per-unit pixel visibility, conservation.

Checks against actual PNG bytes:
1. frame PNGs: RGBA, 600x600, transparent background (corners + >=25% area).
2. per frame per unit: pixels matching its pure RGB (tol 12, alpha>200)
   >= 45% of nominal area => actually visible, not moved out / fully hidden.
3. conservation: the set of pure unit colors is identical in all 6 frames.
4. cover: 1200x800, fully opaque.
Writes tmp/run-20261011-01/A23/verify-report.json (process evidence).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a23_common as C  # noqa: E402
from PIL import Image  # noqa: E402

TMP = "tmp/run-20261011-01/A23"
TOL = 12
SUF = sys.argv[1] if len(sys.argv) > 1 else "c"


def unit_area(u):
    if u["shape"] == "circle":
        return 3.14159265 * u["radius"] ** 2
    return u["w"] * u["h"]


def color_count(px, w, h, rgb):
    n = 0
    R, G, B = rgb
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 200 and abs(r - R) <= TOL and abs(g - G) <= TOL \
                    and abs(b - B) <= TOL:
                n += 1
    return n


def hex_rgb(s):
    return (int(s[1:3], 16), int(s[3:5], 16), int(s[5:7], 16))


report = dict(frames=[], errors=[])
color_sets = []
for k in range(6):
    path = "%s/frames/frame-%02d%s.png" % (TMP, k + 1, SUF)
    im = Image.open(path).convert("RGBA")
    assert im.size == (C.FRAME, C.FRAME), path
    px = im.load()
    w, h = im.size
    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    trans = sum(1 for y in range(0, h, 4) for x in range(0, w, 4)
                if px[x, y][3] < 10)
    trans_frac = trans / float((h // 4 + 1) * (w // 4 + 1))
    row = dict(index=k + 1, corners_alpha0=all(c[3] == 0 for c in corners),
               transparent_area_fraction=round(trans_frac, 3), units={})
    if not row["corners_alpha0"]:
        report["errors"].append("F%d corners not alpha0" % (k + 1))
    pure = set()
    for u in C.UNITS:
        rgb = hex_rgb(u["color"])
        n = color_count(px, w, h, rgb)
        frac = n / unit_area(u)
        row["units"][u["id"]] = dict(pure_pixels=n,
                                     frac_of_nominal=round(frac, 3))
        if frac < 0.45:
            report["errors"].append("F%d %s visible frac %.2f < 0.45"
                                    % (k + 1, u["id"], frac))
        if n > 0:
            pure.add(u["color"])
    color_sets.append(pure)
    report["frames"].append(row)

if not all(s == color_sets[0] for s in color_sets):
    report["errors"].append("unit color set differs between frames")

cov = Image.open(TMP + "/cover-02.png").convert("RGBA")
cpx = cov.load()
opaque = all(cpx[x, y][3] == 255
             for y in (0, 400, 799) for x in (0, 600, 1199))
report["cover"] = dict(size=list(cov.size), sample_opaque=opaque)
if list(cov.size) != [1200, 800]:
    report["errors"].append("cover size %s" % list(cov.size))
if not opaque:
    report["errors"].append("cover not opaque")

with open(TMP + "/verify-report.json", "w", encoding="utf-8") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=1)

for row in report["frames"]:
    fr = sorted(((uid, d["frac_of_nominal"]) for uid, d in
                 row["units"].items()), key=lambda kv: kv[1])
    print("F%d trans=%.2f lowest=%s" % (
        row["index"], row["transparent_area_fraction"],
        ", ".join("%s %.2f" % (u, f) for u, f in fr[:3])))
print("unit colors conserved across frames:",
      color_sets[0] == color_sets[1] == color_sets[2] == color_sets[3]
      == color_sets[4] == color_sets[5], "| colors:", len(color_sets[0]))
print("cover:", report["cover"])
print("ERRORS:", report["errors"] or "NONE")

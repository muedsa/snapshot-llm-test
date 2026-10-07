# -*- coding: utf-8 -*-
"""A09 pixel verification: measure the rendered PNG and compare it with the
geometry computed for geometry-audit.json (tolerance +-1.5 px).

Method (also written into the audit file):
  * for every subject colour build a mask of pixels within a small RGB distance
    (25) of the pure stamp colour; the anti-aliased fringe of the shape is
    inside the mask, while the semi-transparent grey before-outline (~90 away)
    and the coloured badge chips (>=57 away, indigo/blue being the closest pair)
    are outside it;
  * the mask is unioned inside the cell window: the grey before-outline crosses
    some transformed subjects and would otherwise split them into pieces;
  * the mask's outer boundary is the visual extent of that shape and is compared
    with the analytically transformed corners of inputs/stamp.json;
  * the dot centre is measured as the luminance-weighted centroid of the dark
    pixels (#111111 and its blends only) and compared with the analytically
    transformed centre;
  * +-1.5 px covers the rasteriser's edge rounding plus the one-pixel blend zone
    (the grey before-outline drawn on top removes about one pixel of the
    subject's own edge, which is inside that tolerance).
"""
import json
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A09")

PNG = sys.argv[1]
AUDIT = sys.argv[2]
OUTJSON = sys.argv[3] if len(sys.argv) > 3 else os.path.join(TMP, "pixel-verification.json")
TOL = 1.5
DIST = 25

audit = json.load(open(AUDIT, encoding="utf-8"))
im = Image.open(PNG).convert("RGB")
IW, IH = im.size
px = im.load()
print("image size", IW, IH)


def hexrgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def build_mask(pred, x0, y0, x1, y1):
    x0, y0 = max(0, int(x0)), max(0, int(y0))
    x1, y1 = min(IW, int(x1) + 1), min(IH, int(y1) + 1)
    m = bytearray((x1 - x0) * (y1 - y0))
    for y in range(y0, y1):
        row = (y - y0) * (x1 - x0)
        for x in range(x0, x1):
            if pred(px[x, y]):
                m[row + x - x0] = 1
    return m, x0, y0, x1, y1


def mask_union(m, x0, y0, x1, y1):
    """Union of every set pixel: return (bbox, xs, ys, count)."""
    w = x1 - x0
    xs, ys = [], []
    for i, v in enumerate(m):
        if v:
            xs.append((i % w) + x0)
            ys.append((i // w) + y0)
    if not xs:
        return None, [], [], 0
    return [min(xs), min(ys), max(xs) + 1, max(ys) + 1], xs, ys, len(xs)


def is_dark(c):
    """#111111 and its anti-aliased blends only (near-neutral and dark)."""
    lum = 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    return lum <= 100 and (max(c) - min(c)) <= 18


report = {"tolerance_px": TOL, "colour_distance_threshold": DIST,
          "png": os.path.relpath(PNG, ROOT), "canvas": [IW, IH], "specimens": []}
worst, fails = 0.0, []
for sp in audit["specimens"]:
    ex, ey, ew, eh = sp["cell_rect"]
    pad = 6
    win = (ex - pad, ey - pad, ex + ew + pad, ey + eh + pad)
    entry = {"id": sp["id"], "shapes": [], "dot": {},
             "expected_final_canvas_bbox": sp["final_canvas_bbox"]}
    for rect in sp["rectangles"]:
        target = hexrgb(rect["color"])

        def pred(c, t_=target):
            return ((c[0] - t_[0]) ** 2 + (c[1] - t_[1]) ** 2
                    + (c[2] - t_[2]) ** 2) ** 0.5 <= DIST

        exp = rect["canvas_bbox_after"]
        m, x0, y0, x1, y1 = build_mask(pred, *win)
        got, _xs, _ys, n = mask_union(m, x0, y0, x1, y1)
        if got is None:
            fails.append("%s rect%d: no pixels" % (sp["id"], rect["index"]))
            entry["shapes"].append({"index": rect["index"], "found": False})
            continue
                # true shape area after the affine (not the axis-aligned bbox area)
        exp_area = (rect["local_xywh"][2] * rect["local_xywh"][3]
                    * abs(sp["determinant"]))
        d = {"index": rect["index"], "color": rect["color"],
             "expected_bbox": exp, "measured_bbox": got, "pixel_count": n,
             "expected_area": round(exp_area, 1),
             "area_ratio": round(n / exp_area, 3),
             "delta": [round(got[0] - exp[0], 2), round(got[1] - exp[1], 2),
                       round(got[2] - (exp[0] + exp[2]), 2),
                       round(got[3] - (exp[1] + exp[3]), 2)]}
        d["max_abs_delta"] = round(max(abs(v) for v in d["delta"]), 2)
        worst = max(worst, d["max_abs_delta"])
        if d["max_abs_delta"] > TOL:
            fails.append("%s rect%d delta %s" % (sp["id"], rect["index"], d["delta"]))
        if not (0.88 <= d["area_ratio"] <= 1.0):
            fails.append("%s rect%d area ratio %.3f" % (sp["id"], rect["index"],
                                                        d["area_ratio"]))
        entry["shapes"].append(d)

    m, x0, y0, x1, y1 = build_mask(is_dark, *win)
    _g, xs, ys, ndark = mask_union(m, x0, y0, x1, y1)
    expc = sp["dot"]["canvas_center_after"]
    if not xs:
        fails.append("%s dot: no dark pixels" % sp["id"])
    else:
        sw = sx = sy = 0.0
        for x, y in zip(xs, ys):
            c = px[x, y]
            lum = 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
            ww = 101.0 - lum
            sx += x * ww
            sy += y * ww
            sw += ww
        cx, cy = sx / sw, sy / sw
        dd = {"expected_center": expc,
              "measured_centroid": [round(cx, 2), round(cy, 2)],
              "delta": [round(cx - expc[0], 2), round(cy - expc[1], 2)],
              "pixel_count": ndark}
        dd["max_abs_delta"] = round(max(abs(v) for v in dd["delta"]), 2)
        worst = max(worst, dd["max_abs_delta"])
        if dd["max_abs_delta"] > TOL:
            fails.append("%s dot delta %s" % (sp["id"], dd["delta"]))
        entry["dot"] = dd
    report["specimens"].append(entry)

report["worst_abs_delta_px"] = round(worst, 2)
report["failures"] = fails
report["verdict"] = "PASS" if not fails else "FAIL"
with open(OUTJSON, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=2)
print("worst |delta| = %.2f px, failures = %d, verdict = %s"
      % (worst, len(fails), report["verdict"]))
for f in fails:
    print("FAIL:", f)
print("report ->", OUTJSON)
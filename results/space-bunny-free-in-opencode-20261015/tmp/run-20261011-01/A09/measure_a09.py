#!/usr/bin/env python
"""A09 pixel check: measure each transform's rectangles/dot from the rendered PNG.

Two criteria are recorded:
  strict  - pixels exactly equal to the fill colour (solid core); edges are
            naturally inset by ~0.5px because of anti-aliasing.
  blended - a pixel is accepted when it can be written as the fill colour blended
            with white, i.e. a single coverage alpha in [0,1] satisfies all three
            channels within a small spread. This restores the half-covered edge
            pixels that anti-aliasing removes and is the primary +/-1.5px criterion.
Search window: for each element only the region within 12px of its predicted
bounding box (clipped to the cell) is sampled, so helper lines, neighbouring
elements and neighbouring cells cannot pollute the measurement.
"""
from __future__ import annotations

import importlib.util
import json
import math
import os
import sys
from pathlib import Path

from PIL import Image

spec = importlib.util.spec_from_file_location("b09", "tmp/run-20261011-01/A09/build_a09.py")
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)

TOL = 1.5
ALPHA_SPREAD = 0.12
ALPHA_MIN = 0.04          # exclude pure white background (alpha=0); bias <= 0.04px
FRAME_MARGIN = 3.0        # rotated-frame search margin; anti-aliased edges extend <=1px
BG = 255.0


def rgb_of(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def blend_alpha(p, c):
    """Return coverage alpha if p can be written as c blended with white, else None."""
    alphas = []
    for ch in range(3):
        denom = BG - c[ch]
        if abs(denom) < 1e-6:
            if abs(p[ch] - c[ch]) > 2:
                return None
            alphas.append(1.0)
        else:
            alphas.append((BG - p[ch]) / denom)
    if min(alphas) < ALPHA_MIN or max(alphas) > 1.0:
        return None
    if max(alphas) - min(alphas) > ALPHA_SPREAD:
        return None
    return alphas


def uv_box(pts, ccx, ccy, uu, vv):
    if not pts:
        return None
    s = [(p[0] - ccx) * uu[0] + (p[1] - ccy) * uu[1] for p in pts]
    t = [(p[0] - ccx) * vv[0] + (p[1] - ccy) * vv[1] for p in pts]
    return (min(s), min(t), max(s), max(t))


def axis_bbox(box, uu, vv, ccx, ccy, margin=14.0):
    """Project a (u,v) box given relative to (ccx,ccy) back to canvas coordinates."""
    xs, ys = [], []
    for u in (box[0], box[2]):
        for v in (box[1], box[3]):
            xs.append(ccx + u * uu[0] + v * vv[0])
            ys.append(ccy + u * uu[1] + v * vv[1])
    return (min(xs) - margin, min(ys) - margin, max(xs) + margin, max(ys) + margin)


def scan(im, win, color, uu, vv, ccx, ccy, ubox, vbox, circle=None):
    """Return (exact-colour pixels, exact-or-blended pixels) inside the tight bounds.

    The canvas window is only a fast pre-clip; every candidate pixel must also
    satisfy ubox/vbox in the rotated frame (and, when circle is given, lie inside
    that radius) so neighbouring elements and helper lines cannot pollute the extent.
    """
    px = im.load()
    strict, matched = [], []
    x0 = max(0, int(win[0]))
    y0 = max(0, int(win[1]))
    x1 = min(im.width, int(win[2]) + 1)
    y1 = min(im.height, int(win[3]) + 1)
    c2 = None if circle is None else circle * circle
    for yy in range(y0, y1):
        for xx in range(x0, x1):
            p = (xx + 0.5, yy + 0.5)
            du = (p[0] - ccx) * uu[0] + (p[1] - ccy) * uu[1]
            dv = (p[0] - ccx) * vv[0] + (p[1] - ccy) * vv[1]
            if not (ubox[0] <= du <= ubox[1] and vbox[0] <= dv <= vbox[1]):
                continue
            if c2 is not None and du * du + dv * dv > c2:
                continue
            c = px[xx, yy]
            if c == color:
                strict.append(p)
                matched.append(p)
                continue
            if blend_alpha(c, color) is not None:
                matched.append(p)
    return strict, matched


def measure(png_path, audit_path):
    im = Image.open(png_path).convert("RGB")
    audit = json.loads(Path(audit_path).read_text(encoding="utf-8"))
    root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    stamp = json.loads((root / "tasks/A09-transform-atlas/inputs/stamp.json").read_text(encoding="utf-8"))
    dot_rgb = rgb_of(stamp["dot"]["color"])

    rows, worst = [], 0.0
    for rec in audit["geometry"]:
        tid = rec["id"]
        tinfo = next(t for t in audit["transforms"] if t["id"] == tid)
        ccx, ccy = tinfo["cell_center_px"]
        cm = tinfo["matrix_column_major_4x4_dsl"]
        # 列主序线性部分：col0 = 局部 x 轴的像，col1 = 局部 y 轴的像
        uu_raw = (cm[0], cm[1])
        vv_raw = (cm[4], cm[5])
        nu = math.hypot(*uu_raw) or 1.0
        nv = math.hypot(*vv_raw) or 1.0
        uu = (uu_raw[0] / nu, uu_raw[1] / nu)
        vv = (vv_raw[0] / nv, vv_raw[1] / nv)

        rec_rows = []
        for r in rec["rectangles"]:
            corners = r["canvas_corners_tl_tr_br_bl"]
            ps = [((c[0] - ccx) * uu[0] + (c[1] - ccy) * uu[1],
                   (c[0] - ccx) * vv[0] + (c[1] - ccy) * vv[1]) for c in corners]
            pred = (min(p[0] for p in ps), min(p[1] for p in ps),
                    max(p[0] for p in ps), max(p[1] for p in ps))
            win = axis_bbox(pred, uu, vv, ccx, ccy, margin=FRAME_MARGIN)
            ub = (pred[0] - FRAME_MARGIN, pred[2] + FRAME_MARGIN)
            vb = (pred[1] - FRAME_MARGIN, pred[3] + FRAME_MARGIN)
            strict, blended = scan(im, win, rgb_of(r["color"]), uu, vv, ccx, ccy, ub, vb)
            row = {"color": r["color"], "predicted_uv": [round(v, 3) for v in pred],
                   "search_window_px": [round(v, 1) for v in win],
                   "search_window_uv": {"u": [round(v, 2) for v in ub],
                                        "v": [round(v, 2) for v in vb]}}
            for mode, pts in (("blended", blended), ("strict", strict)):
                meas = uv_box(pts, ccx, ccy, uu, vv)
                if meas is None:
                    row[mode] = None
                    continue
                err = [meas[i] - pred[i] for i in range(4)]
                e = max(abs(v) for v in err)
                row[mode] = {"measured_uv": [round(v, 3) for v in meas],
                             "error_uv": [round(v, 3) for v in err],
                             "max_abs_error_px": round(e, 3), "pixels": len(pts)}
                if mode == "blended":
                    worst = max(worst, e)
            row["passed"] = bool(row.get("blended") and row["blended"]["max_abs_error_px"] <= TOL)
            rec_rows.append(row)

        dc = rec["dot"]["canvas_center"]
        rad = max(rec["dot"]["radii"]["semi_axis_u"], rec["dot"]["radii"]["semi_axis_v"])
        dbox = (-rad - 3, -rad - 3, rad + 3, rad + 3)
        win = axis_bbox(dbox, uu, vv, dc[0], dc[1], margin=FRAME_MARGIN)
        ub = (dbox[0] - FRAME_MARGIN, dbox[2] + FRAME_MARGIN)
        vb = (dbox[1] - FRAME_MARGIN, dbox[3] + FRAME_MARGIN)
        strict, blended = scan(im, win, dot_rgb, uu, vv, dc[0], dc[1], ub, vb,
                               circle=rad + FRAME_MARGIN)
        drow = {"predicted_center_px": dc, "predicted_radius_px": round(rad, 3),
                "search_window_px": [round(v, 1) for v in win],
                "search_window_uv": {"u": [round(v, 2) for v in ub],
                                     "v": [round(v, 2) for v in vb]}}
        for mode, pts in (("blended", blended), ("strict", strict)):
            meas = uv_box(pts, dc[0], dc[1], uu, vv)
            if meas is None:
                drow[mode] = None
                continue
            ctr = ((meas[0] + meas[2]) / 2, (meas[1] + meas[3]) / 2)
            r = ((meas[2] - meas[0]) / 2 + (meas[3] - meas[1]) / 2) / 2
            drow[mode] = {"measured_center_uv": [round(v, 3) for v in ctr],
                          "center_error_px": round(max(abs(ctr[0]), abs(ctr[1])), 3),
                          "measured_radius_px": round(r, 3), "pixels": len(pts)}
            if mode == "blended":
                worst = max(worst, drow[mode]["center_error_px"])
        drow["passed"] = bool(drow.get("blended") and drow["blended"]["center_error_px"] <= TOL)

        rows.append({"id": tid, "cell_box_px": tinfo["cell_box_px"],
                     "subject_center_px": [ccx, ccy],
                     "matrix_dsl_string": tinfo["matrix_dsl_string"],
                     "final_bounding_box_px": rec["final_bounding_box_px"],
                     "rectangles": rec_rows, "dot": drow,
                     "passed": all(x["passed"] for x in rec_rows) and drow["passed"]})
    return rows, worst


def main():
    png = sys.argv[1] if len(sys.argv) > 1 else "tmp/run-20261011-01/A09/preview/a09-v3.png"
    audit = "tmp/run-20261011-01/A09/drafts/geometry-audit-raw.json"
    rows, worst = measure(png, audit)
    for r in rows:
        b = max(rr["blended"]["max_abs_error_px"] for rr in r["rectangles"])
        s = max(rr["strict"]["max_abs_error_px"] for rr in r["rectangles"])
        print(f'{r["id"]} blended {b:5.2f} | strict {s:5.2f} | '
              f'dot {r["dot"]["blended"]["center_error_px"]:5.2f} | '
              f'{"PASS" if r["passed"] else "FAIL"}')
    print("WORST blended", round(worst, 3), "tol", TOL)
    Path("tmp/run-20261011-01/A09/measure.json").write_text(
        json.dumps({"tolerance_px": TOL, "alpha_spread": ALPHA_SPREAD,
                    "worst_blended_error_px": round(worst, 3), "image": png, "rows": rows},
                   ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

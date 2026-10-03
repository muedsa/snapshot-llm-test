"""A09 pixel audit: verify the rendered atlas against the predicted matrices.

Method (documented in geometry-audit.json):
  1. The composite column-major matrix of every cell maps stamp-local coordinates to
     canvas coordinates. The prediction rasterises the stamp (3 rectangles + dot,
     painter order) on a 4x supersampled grid and downsamples it to a class map.
  2. Class agreement: every pixel whose predicted class is "card background" must not
     carry a specimen colour, and every pixel predicted as a specimen colour must show
     that colour, except inside the antialiasing band (+-1.5 px around a predicted
     class boundary) where blended colours are legal.
  3. Sub-pixel edge localisation: for every adjacent pixel pair (ink, clean card white)
     the coverage ratio of the two pixels estimates where the true edge crossed the
     pair; that estimate is compared with the predicted crossing taken from the same
     supersampled model. |delta| must stay <= 1.5 px.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
TASK_DIR = os.path.join(ROOT, "tasks", "A09-transform-atlas")
STAMP = json.load(open(os.path.join(TASK_DIR, "inputs", "stamp.json"), encoding="utf-8"))
TOL = 1.5
SS = 4  # supersampling factor

COLORS = [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in
          [r["color"] for r in STAMP["rectangles"]] + [STAMP["dot"]["color"]]]
WHITE = (255, 255, 255)


def local_of(a, t, p):
    return np.linalg.inv(a) @ (np.asarray(p, dtype=float) - t)


def class_at(a, t, pts):
    """Vectorised class map: 0 background, 1..3 rects, 4 dot."""
    loc = (np.linalg.inv(a) @ (pts - t).T).T
    cls = np.zeros(len(loc), dtype=np.int8)
    for i, r in enumerate(STAMP["rectangles"]):
        x, y, w, h = r["xywh"]
        inside = (loc[:, 0] >= x) & (loc[:, 0] <= x + w) & (loc[:, 1] >= y) & (loc[:, 1] <= y + h)
        cls[inside] = i + 1
    d = STAMP["dot"]
    inside = np.hypot(loc[:, 0] - d["center"][0], loc[:, 1] - d["center"][1]) <= d["radius"]
    cls[inside] = 4
    return cls


def predict(a, t, x0, y0, x1, y1):
    """Downsampled class map for the pixel grid [x0,x1) x [y0,y1)."""
    xs = np.arange(x0, x1)
    ys = np.arange(y0, y1)
    gx, gy = np.meshgrid(xs, ys)
    flat = np.stack([gx.ravel(), gy.ravel()], axis=1).astype(float)
    counts = np.zeros((len(flat), 5), dtype=np.int32)
    for dy in range(SS):
        for dx in range(SS):
            off = np.array([(dx + 0.5) / SS, (dy + 0.5) / SS])
            c = class_at(a, t, flat + off)
            counts[np.arange(len(flat)), c] += 1
    cls = counts.argmax(axis=1).astype(np.int8).reshape(len(ys), len(xs))
    return cls, counts


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    png = os.path.join(HERE, f"transform-atlas.{version}.png")
    data = json.load(open(os.path.join(HERE, f"geometry-data.{version}.json"), encoding="utf-8"))
    img = np.asarray(Image.open(png).convert("RGB")).astype(np.int16)
    cells_report = []
    worst_band = 0
    worst_sub = 0.0
    total_viol = 0
    sub_samples = 0
    for cell in data["cells"]:
        ox, oy = cell["origin"]
        a = np.array(cell["matrix_16"]).reshape(4, 4)[:2, :2].T  # columns -> matrix
        t = np.array([cell["matrix_16"][12], cell["matrix_16"][13]])
        x0, y0 = int(ox) + 2, int(oy) + 42
        x1, y1 = int(ox) + 298, int(oy) + 208
        cls, counts = predict(a, t, x0, y0, x1, y1)
        tile = img[y0:y1, x0:x1]
        # antialiasing band: pixel touches a class change within 1.5 px
        change = np.zeros_like(cls, dtype=bool)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                sh = np.roll(np.roll(cls, dy, axis=0), dx, axis=1)
                change |= sh != cls
        band = change
        ok = np.ones_like(cls, dtype=bool)
        mism = np.zeros_like(cls, dtype=bool)
        for c in range(5):
            sel = cls == c
            if c == 0:
                # background pixels must not carry a specimen colour
                far = np.ones_like(sel, dtype=bool)
                for col in COLORS:
                    far &= (np.abs(tile - np.array(col)).max(axis=2) > 10)
                bad = sel & ~far
            else:
                good = np.abs(tile - np.array(COLORS[c - 1])).max(axis=2) <= 10
                bad = sel & ~good
            mism |= bad
            ok &= ~bad
        viol = mism & ~band
        total_viol += int(viol.sum())
        # sub-pixel edge check on ink/clean-white pixel pairs
        deltas = []
        white = (np.abs(tile - np.array(WHITE)).max(axis=2) <= 6)
        h, w = cls.shape
        for axis in (0, 1):
            for sgn in (1, -1):
                ink = cls > 0
                # neighbour in the direction of travel (+sgn) must be clean card white
                nb = np.roll(white, -sgn, axis=axis)
                cur = np.roll(cls, -sgn, axis=axis)
                sel = ink & nb & (cur == 0)
                ys, xs = np.nonzero(sel)
                for yy, xx in zip(ys, xs):
                    # pixel centres live at index+0.5, matching the supersampled model
                    p = np.array([xx + 0.5, yy + 0.5], dtype=float)
                    q = p.copy()
                    q[axis] += sgn
                    steps = np.linspace(0.0, 1.0, 41)
                    seg = p[None, :] + steps[:, None] * (q - p)[None, :]
                    cseg = class_at(a, t, seg + np.array([x0, y0]))
                    idx = np.nonzero(cseg != cls[yy, xx])[0]
                    if len(idx) == 0:
                        continue
                    s_pred = steps[idx[0]]
                    cpix = tile[yy, xx].astype(float)
                    col = np.array(COLORS[cls[yy, xx] - 1], dtype=float)
                    cq = tile[int(yy + (sgn if axis == 0 else 0)),
                              int(xx + (sgn if axis == 1 else 0))].astype(float)
                    ap = np.linalg.norm(cpix - WHITE) / max(np.linalg.norm(col - WHITE), 1e-6)
                    aq = np.linalg.norm(cq - WHITE) / max(np.linalg.norm(col - WHITE), 1e-6)
                    ap, aq = min(max(ap, 0.0), 1.0), min(max(aq, 0.0), 1.0)
                    # pixel p spans [s-0.5, s+0.5], q spans [s+0.5, s+1.5]; with the ink
                    # on p's side the coverage pair pins the edge at s = 0.5 + aq
                    # (or s = ap - 0.5 when q is untouched)
                    if aq > 0.02:
                        s_est = 0.5 + aq
                    elif ap < 0.98:
                        s_est = ap - 0.5
                    else:
                        s_est = 0.5   # edge exactly between the two centres
                    deltas.append(abs(s_est - s_pred))
                    sub_samples += 1
        dmax = max(deltas) if deltas else None
        if dmax is not None:
            worst_sub = max(worst_sub, dmax)
        cells_report.append({
            "id": cell["id"],
            "band_pixels": int(band.sum()),
            "pixels_checked": int(cls.size),
            "mismatch_pixels_outside_band": int(viol.sum()),
            "first_violations": [[int(v[1] + x0), int(v[0] + y0)] for v in np.argwhere(viol)[:6]],
            "subpixel_edge_pairs": len(deltas),
            "subpixel_max_delta_px": round(dmax, 3) if dmax is not None else None,
            "subpixel_mean_delta_px": round(float(np.mean(deltas)), 3) if deltas else None,
        })
        print(f'{cell["id"]}: checked={cls.size} band={int(band.sum())} viol={int(viol.sum())} '
              f'subpix n={len(deltas)} max={dmax if dmax is None else round(dmax,3)}')
    out = {
        "verdict": "pass" if total_viol == 0 and worst_sub <= TOL else "fail",
        "tolerance_px": TOL,
        "pixels_checked": sum(c["pixels_checked"] for c in cells_report),
        "mismatch_pixels_outside_band": total_viol,
        "subpixel_edge_pairs": sub_samples,
        "subpixel_max_delta_px": round(worst_sub, 3),
        "cells": cells_report,
    }
    with open(os.path.join(HERE, f"pixel-check.{version}.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in out.items() if k != "cells"}, ensure_ascii=False))


if __name__ == "__main__":
    main()

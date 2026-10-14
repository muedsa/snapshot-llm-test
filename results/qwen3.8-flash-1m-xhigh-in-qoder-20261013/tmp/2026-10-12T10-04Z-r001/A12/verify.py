"""A12 verification against the four rendered PNGs.

gen.py's layout estimator is deliberately conservative, so the model alone cannot prove
that nothing wrapped, clipped or crossed a border. This reads the returned PNGs and, for
every recorded text box, measures where ink that differs from that box's own background
actually sits — other text boxes, and the decoration rects that do not contain the box,
are excluded from the search.

Run: python tmp/<run_id>/A12/verify.py --ver v003
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
OUT_DIR = ROOT / "outputs" / RUN / "A12"
TMP_DIR = ROOT / "tmp" / RUN / "A12"

CANVAS = {"mobile": (360, 800), "tablet": (768, 1024),
          "desktop": (1440, 900), "stage": (1920, 1080)}
MARGIN = {"mobile": 16, "tablet": 32, "desktop": 32, "stage": 32}
INK_DIFF = 70          # a pixel counts as ink when it is this far from its background


def rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.int16)


def fill(mask, x0, y0, x1, y1, value):
    mask[max(0, y0):min(mask.shape[0], y1), max(0, x0):min(mask.shape[1], x1)] = value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ver", required=True)
    a = ap.parse_args()

    cmap = json.loads((OUT_DIR / "content-map.json").read_text(encoding="utf-8"))
    segs = cmap["segments"]
    report = {}

    for bp, (W, H) in CANVAS.items():
        im = Image.open(TMP_DIR / f"{a.ver}-{bp}.png")
        im.load()
        assert im.size == (W, H), (bp, im.size)
        arr = np.asarray(im.convert("RGB"), dtype=np.int16)
        m = MARGIN[bp]

        diff = np.abs(arr - rgb("#F6F3EC")).max(axis=2)
        ys, xs = np.nonzero(diff > 26)
        gbox = {"min_x": int(xs.min()), "max_x": int(xs.max()),
                "min_y": int(ys.min()), "max_y": int(ys.max())}
        margin_ok = bool(gbox["min_x"] >= m - 1 and gbox["max_x"] <= W - m + 1
                         and gbox["min_y"] >= m - 1 and gbox["max_y"] <= H - m + 1)

        mine = [x for x in segs if x["canvas"] == bp]
        textmask = np.zeros((H, W), dtype=bool)
        for o in mine:
            x0, y0, w, h = o["text_box_px"]
            fill(textmask, int(x0) - 1, int(y0) - 1, int(x0 + w) + 1, int(y0 + h) + 1, True)
        rects = cmap.get("decoration_rects", {}).get(bp, [])

        problems, measured = [], []
        for o in mine:
            x0, y0, w, h = o["text_box_px"]
            size = o["font_size_px"]
            bx0, bx1 = max(0, int(x0)), min(W, int(x0 + w))
            by0, by1 = max(0, int(y0)), min(H, int(y0 + h))
            if bx1 <= bx0 or by1 <= by0:
                problems.append(f"degenerate-box {o['field']}")
                continue
            # a decoration rect that contains this box is its own surface: exclude it from
            # the noise mask but clip the search to it, so a band edge is not read as ink
            decor = np.zeros((H, W), dtype=bool)
            cx0, cy0, cx1, cy1 = 0, 0, W, H
            for dx, dy, dw, dh in rects:
                dx, dy, dw, dh = int(dx), int(dy), int(dw), int(dh)
                if (dx - 1 <= bx0 and dy - 1 <= by0
                        and dx + dw + 1 >= bx1 and dy + dh + 1 >= by1):
                    if (dx - cx0) * (dy - cy0) * (cx1 - dx - dw) * (cy1 - dy - dh) <                             (cx1 - cx0) * (cy1 - cy0):
                        cx0, cy0, cx1, cy1 = dx, dy, dx + dw, dy + dh
                    continue
                fill(decor, dx - 2, dy - 2, dx + dw + 2, dy + dh + 2, True)

            region = arr[by0:by1, bx0:bx1].reshape(-1, 3)
            vals, cnt = np.unique(region // 8 * 8, axis=0, return_counts=True)
            bg = vals[cnt.argmax()].astype(np.int16)
            # the box's own footprint must stay visible; only other boxes are masked out
            allow = np.zeros((H, W), dtype=bool)
            fill(allow, bx0, by0, bx1, by1, True)
            own = (np.abs(arr - bg).max(axis=2) > INK_DIFF) & ~decor \
                & (~textmask | allow)
            fill(own, 0, 0, max(0, min(bx0 - 3, cx0 + 2)), H, False)
            fill(own, min(int(x0 + w) + 4, cx1 - 1), 0, W, H, False)
            fill(own, 0, 0, W, max(0, min(int(y0) - 3, cy0 + 2)), False)
            fill(own, 0, min(int(y0 + h) + int(size * 1.4), cy1 - 1), W, H, False)
            ys2, xs2 = np.nonzero(own)
            if len(ys2) == 0:
                problems.append(f"no-ink {o['field']} at ({x0:.0f},{y0:.0f})")
                continue
            ink = {"field": o["field"], "box": [x0, y0, w, h],
                   "ink_x": [int(xs2.min()), int(xs2.max())],
                   "ink_y": [int(ys2.min()), int(ys2.max())],
                   "model_lines": o["wrapped_lines"]}
            ink["overflow_right_px"] = max(0, ink["ink_x"][1] - int(x0 + w))
            ink["below_box_px"] = max(0, ink["ink_y"][1] - int(y0 + h))
            # ink below the box is only a wrapped line if it looks like glyphs: a band
            # edge or a background change paints every column, text does not
            below = own[int(y0 + h) + 2:, bx0:bx1]
            rows_b = np.nonzero(below.any(axis=1))[0]
            cover = float(below[rows_b].mean()) if len(rows_b) else 0.0
            ink["below_box_ink_coverage"] = round(cover, 3)
            ink["below_box_rows"] = int(len(rows_b))
            text_like = len(rows_b) >= 3 and cover < 0.75
            if ink["overflow_right_px"] > 3:
                problems.append(f"right-overflow {o['field']} by "
                                f"{ink['overflow_right_px']}px")
            if ink["below_box_px"] > size * 0.45 and text_like:
                problems.append(f"extra-wrap {o['field']} model={o['wrapped_lines']} "
                                f"below_box={ink['below_box_px']}px")
            measured.append(ink)

        report[bp] = {"canvas": [W, H], "safe_margin_px": m, "content_bbox": gbox,
                      "within_safe_margin": margin_ok,
                      "boxes_checked": len(measured), "boxes_expected": len(mine),
                      "worst_right_overflow_px": max(
                          [x["overflow_right_px"] for x in measured] or [0]),
                      "worst_below_box_px": round(max(
                          [x["below_box_px"] for x in measured] or [0]), 1),
                      "problems": problems}

    cmap["rendered_verification"] = {
        "ver": a.ver,
        "method": "对每个文字盒取其自身背景主色，在返回 PNG 上找偏离该背景 >70 的墨迹；"
                  "其他文字盒与不含本盒的装饰矩形被排除；比较墨迹右缘/下缘与声明盒",
        "canvases": report}
    (OUT_DIR / "content-map.json").write_text(
        json.dumps(cmap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (TMP_DIR / f"{a.ver}-verify.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""Pixel-level audit helpers for A21.

Both audits diff the final PNG against a *text-free* render of the identical
composition (same background, same brand mark, same cards/chips/rules).  The
difference is exactly the glyph coverage, so:

  * ink_audit    -> proves every string's real ink bounding box is inside its
                    declared text box and that nothing spills into the annulus;
  * contrast_audit -> reads the background tone that the service actually
                    composited under the glyphs (gradient, alpha plates, panels,
                    chip fills and the light beam all included) and computes the
                    WCAG 2.1 contrast ratio for the declared text colour.
"""
import json
import os
from collections import Counter

from PIL import Image

import brandkit as B

DIFF_TOL = 8          # sum-RGB distance that counts as "the text changed a pixel"
INK_TOL_PX = 6        # anti-aliasing fringe tolerance in px around a declared
                      # core-ink box. The probe renders are measured at a
                      # 200/255 grayscale threshold, so they record core ink
                      # only, while the rasteriser adds a soft fringe of up to
                      # ~5px at 26-108px type. Real defects (soft wrap, clipping,
                      # collision) move ink by tens of px and are still caught,
                      # and pair_collisions() below checks overlap directly.


def _modal(pixels):
    c = Counter(pixels)
    top = c.most_common(1)[0]
    return top[0], top[1]


def load(path):
    im = Image.open(path).convert("RGB")
    return im, im.load()


def _diff_boxes(png, png_notext, texts, pad=12):
    """Per-text glyph coverage, measured on the diff between the final PNG and a
    text-free render of the identical composition.

    Every changed pixel is attributed to the *nearest* declared ink box (Cheby-
    shev distance, 0 when inside). That keeps neighbouring lines of one title
    from contaminating each other while still catching real overflow: a pixel
    that belongs to text A but sits outside A's box shows up as escape, and a
    pixel that belongs to no text box at all is reported as unattributed.
    """
    im, px = load(png)
    im2, px2 = load(png_notext)
    assert im.size == im2.size, (im.size, im2.size)
    w, h = im.size
    boxes = []
    for t in texts:
        boxes.append([int(round(v)) for v in t["ink"]])
    acc = [{"xs0": -1, "ys0": -1, "xs1": -1, "ys1": -1, "inside": 0,
            "escape": 0} for _ in texts]
    unattributed = 0
    for yy in range(h):
        for xx in range(w):
            a = px[xx, yy]
            b = px2[xx, yy]
            if (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])) <= DIFF_TOL:
                continue
            best, bestd = -1, 10 ** 9
            for i, (bx0, by0, bx1, by1) in enumerate(boxes):
                dx = max(bx0 - xx, 0, xx - bx1)
                dy = max(by0 - yy, 0, yy - by1)
                d = dx if dx > dy else dy
                if d < bestd:
                    best, bestd = i, d
            if best < 0 or bestd > pad:
                unattributed += 1
                continue
            bx0, by0, bx1, by1 = boxes[best]
            r = acc[best]
            if (bx0 - INK_TOL_PX <= xx <= bx1 + INK_TOL_PX and
                    by0 - INK_TOL_PX <= yy <= by1 + INK_TOL_PX):
                r["inside"] += 1
                if r["xs0"] < 0 or xx < r["xs0"]:
                    r["xs0"] = xx
                if r["ys0"] < 0 or yy < r["ys0"]:
                    r["ys0"] = yy
                if xx > r["xs1"]:
                    r["xs1"] = xx
                if yy > r["ys1"]:
                    r["ys1"] = yy
            else:
                r["escape"] += 1
    out = []
    for t, r in zip(texts, acc):
        out.append({"declared_rect": t["rect"], "declared_ink": t["ink"],
                    "measured_ink": ([r["xs0"], r["ys0"], r["xs1"], r["ys1"]]
                                     if r["xs0"] >= 0 else None),
                    "ink_px": r["inside"], "escape_px": r["escape"]})
    return out, im, px, im2, px2, unattributed


def ink_audit(png, png_notext, texts, pad=12, verbose=True):
    boxes, im, px, im2, px2, unattributed = _diff_boxes(png, png_notext, texts, pad)
    rows = []
    bad = 0
    for t, m in zip(texts, boxes):
        xs0, ys0, xs1, ys1 = (m["measured_ink"] + [None] * 4)[:4]
        x, y, w, h = [int(round(v)) for v in t["rect"]]
        ix0, iy0, ix1, iy1 = [int(round(v)) for v in t["ink"]]
        ok = (m["ink_px"] > 0 and m["escape_px"] == 0 and
              xs0 >= x - 2 and xs1 <= x + w + 2 and
              ys0 >= y - 2 and ys1 <= y + h + 2 and
              xs0 >= ix0 - INK_TOL_PX and xs1 <= ix1 + INK_TOL_PX and
              ys0 >= iy0 - INK_TOL_PX and ys1 <= iy1 + INK_TOL_PX)
        wdiff = abs((xs1 - xs0 + 1) - (ix1 - ix0 + 1)) if xs0 >= 0 else None
        hdiff = abs((ys1 - ys0 + 1) - (iy1 - iy0 + 1)) if xs0 >= 0 else None
        rows.append({"id": t["id"], "role": t["role"], "text": t["text"],
                     "fontSize": t["fontSize"],
                     "fontStyle": t["fontStyle"],
                     "letterSpacing": t["letterSpacing"],
                     "declared_rect": t["rect"], "declared_ink": t["ink"],
                     "measured_ink": m["measured_ink"],
                     "glyph_px": m["ink_px"], "escape_px": m["escape_px"],
                     "ink_w_delta": wdiff, "ink_h_delta": hdiff,
                     "inside_declared_box": ok})
        if not ok:
            bad += 1
        if verbose:
            print("%-20s %-32s size=%-5s declared_ink=%s measured=%s "
                  "dw=%s dh=%s esc=%d %s" %
                  (t["id"], t["text"][:30], t["fontSize"], t["ink"],
                   m["measured_ink"], wdiff, hdiff, m["escape_px"],
                   "OK" if ok else "*** OUT OF BOX ***"))
    return {"png": os.path.basename(png),
            "method": "diff against a text-free render of the identical "
                      "composition; diff_tolerance_sum_rgb=%d; every changed "
                      "pixel is attributed to the nearest declared ink box"
                      % DIFF_TOL,
            "annulus_pad_px": pad,
            "unattributed_changed_px": unattributed,
            "elements": len(rows), "violations": bad, "rows": rows}


def contrast_audit(png, png_notext, texts, verbose=True, threshold=4.5):
    im, px = load(png)
    im2, px2 = load(png_notext)
    rows = []
    worst = 99.0
    for t in texts:
        x, y, w, h = [int(round(v)) for v in t["rect"]]
        ix0, iy0, ix1, iy1 = [int(round(v)) for v in t["ink"]]
        glyphs = []
        bgs = []
        for yy in range(max(0, iy0 - 12), min(im.height, iy1 + 13)):
            for xx in range(x, min(im.width, x + w)):
                a, b = px[xx, yy], px2[xx, yy]
                if sum(abs(a[i] - b[i]) for i in range(3)) > DIFF_TOL:
                    glyphs.append(a)
                else:
                    bgs.append(b)
        bg, _ = _modal(bgs) if bgs else (None, 0)
        fg, fg_n = _modal(glyphs) if glyphs else (None, 0)
        declared = B.hex2rgb(t["color"])
        ratio = B.contrast(declared, bg) if bg else None
        ink_ratio = B.contrast(fg, bg) if (fg and bg) else None
        rows.append({"id": t["id"], "role": t["role"], "text": t["text"],
                     "fontSize": t["fontSize"], "text_color": t["color"],
                     "declared_text_rgb": list(declared),
                     "composited_background_rgb": list(bg) if bg else None,
                     "background_source": "sampled from the text-free render of "
                                          "the same composition, i.e. the exact "
                                          "composited result of bg gradient + "
                                          "alpha plates + panel + beam + chip "
                                          "fill that sits under the glyphs",
                     "background_samples_px": len(bgs),
                     "measured_glyph_rgb": list(fg) if fg else None,
                     "glyph_px": fg_n,
                     "contrast_declared_color_vs_composited_background": ratio,
                     "contrast_measured_glyph_vs_composited_background": ink_ratio,
                     "wcag_threshold": threshold,
                     "pass": bool(ratio is not None and ratio >= threshold)})
        if ratio is not None:
            worst = min(worst, ratio)
        if verbose:
            print("%-20s %-28s %s on %s = %s:1 %s" %
                  (t["id"], t["text"][:26], t["color"], bg, ratio,
                   "OK" if (ratio and ratio >= threshold) else "*** FAIL ***"))
    return {"png": os.path.basename(png), "worst_contrast": round(worst, 2),
            "threshold": threshold,
            "all_pass": all(r["pass"] for r in rows),
            "elements": len(rows), "rows": rows}


def pair_collisions(rows, verbose=True):
    """No two measured ink boxes may overlap - this is the direct proof that no
    string collides with another string (the round-02 long-title question)."""
    hits = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = rows[i].get("measured_ink"), rows[j].get("measured_ink")
            if not a or not b:
                continue
            ox = min(a[2], b[2]) - max(a[0], b[0]) + 1
            oy = min(a[3], b[3]) - max(a[1], b[1]) + 1
            if ox > 0 and oy > 0:
                hits.append({"a": rows[i]["id"], "b": rows[j]["id"],
                             "overlap_px": [ox, oy]})
    if verbose:
        print("measured-ink collisions between text elements:", len(hits),
              hits if hits else "")
    return hits


def min_fontsize(texts):
    return min(t["fontSize"] for t in texts)


def check_safe_areas(png, safe, tol=10):
    """A reserved extension band must contain no content at all."""
    im, px = load(png)
    out = []
    for name, (x0, y0, x1, y1) in safe.items():
        pixels = [px[xx, yy] for yy in range(y0, y1) for xx in range(x0, x1)]
        c, _ = _modal(pixels)
        dirty = sum(1 for p in pixels
                    if sum(abs(p[i] - c[i]) for i in range(3)) > tol)
        out.append({"band": name, "rect": [x0, y0, x1 - x0, y1 - y0],
                    "modal_background_rgb": list(c),
                    "pixels_differing_from_background": dirty,
                    "empty": dirty == 0})
    for o in out:
        print("safe-band %-14s %s non_bg_px=%d %s" %
              (o["band"], o["rect"], o["pixels_differing_from_background"],
               "OK" if o["empty"] else "*** NOT EMPTY ***"))
    return out


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
    print("wrote", os.path.basename(path))
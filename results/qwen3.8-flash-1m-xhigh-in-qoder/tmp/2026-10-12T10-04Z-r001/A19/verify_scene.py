"""A19 - measure the delivered PNGs and prove the scene is what scene-data claims.

Grid (1600x1600): every one of the 64 cells is inspected - the painted body's bounding
box gives its size, its fill ratio and centre hole give the shape, its nearest palette
colour gives the colour, and the ID label is checked to sit outside the body. The
aggregates (16 per colour, 16 per shape, all 16 combinations, three sizes per colour and
per shape, >=3 colours and >=3 shapes per row) are then recomputed from the pixels.

Occlusion (800x800): the two versions are decoded to 8-bit non-premultiplied RGBA and
compared channel by channel; every hidden object's own footprint is checked to be the
occluder colour, so "nothing leaks" is measured rather than asserted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A19"
sys.path.insert(0, str(TMP))

COL = {"blue": (43, 91, 215), "orange": (224, 145, 59), "green": (31, 138, 95),
       "violet": (122, 79, 211)}
OCC = (22, 35, 58)
PANEL_BG = (255, 255, 255)
CELL = 200


def label4(mask):
    seen = np.zeros(mask.shape, dtype=bool)
    out = []
    H, W = mask.shape
    for y0, x0 in zip(*[a.tolist() for a in np.nonzero(mask)]):
        if seen[y0, x0]:
            continue
        q = deque([(y0, x0)])
        seen[y0, x0] = True
        minx = maxx = x0
        miny = maxy = y0
        n = 0
        while q:
            y, x = q.popleft()
            n += 1
            minx, maxx = min(minx, x), max(maxx, x)
            miny, maxy = min(miny, y), max(maxy, y)
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        out.append({"n": n, "bbox": [minx, miny, maxx + 1, maxy + 1]})
    return out


def rgba(path):
    """8-bit, non-premultiplied RGBA straight from the decoder."""
    im = Image.open(path)
    im = im.convert("RGBA")
    return np.asarray(im).astype(np.uint8), im.size, im.mode


def main(ver):
    scene = json.loads((TMP / f"{ver}-scene.json").read_text(encoding="utf-8"))
    objects = scene["objects"]
    img = np.asarray(Image.open(TMP / f"{ver}-grid-scene.png").convert("RGB")).astype(int)
    problems, measured = [], []

    painted = (np.abs(img - np.array(PANEL_BG)).sum(axis=2) > 90)
    for o in objects:
        r, c = o["row"] - 1, o["col"] - 1
        win = np.zeros_like(painted)
        win[r * CELL + 3:(r + 1) * CELL - 3, c * CELL + 3:(c + 1) * CELL - 3] = True
        body = np.zeros_like(painted)
        for name, rgb in COL.items():
            body |= (np.abs(img - np.array(rgb)).sum(axis=2) < 120)
        body &= win
        comps = [k for k in label4(body) if k["n"] > 400]
        if not comps:
            problems.append(f"{o['id']}: no painted body found")
            continue
        k = max(comps, key=lambda z: z["n"])
        x0, y0, x1, y1 = k["bbox"]
        w, h = x1 - x0, y1 - y0
        ratio = k["n"] / float(w * h)
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        shape = classify_shape(img, body, k)
        pix = img[y0 + 2:y1 - 2, x0 + 2:x1 - 2].reshape(-1, 3)
        keep = pix[np.abs(pix.astype(int) - np.array(PANEL_BG)).sum(axis=1) > 90]
        med = np.median(keep, axis=0) if len(keep) else np.array([0, 0, 0])
        colour = min(COL.items(),
                     key=lambda t: int(np.abs(med - np.array(t[1])).sum()))[0]
        m = {"id": o["id"], "measured_bbox": [x0, y0, x1, y1],
             "measured_size_px": [w, h], "measured_centre": [round(cx, 1), round(cy, 1)],
             "measured_colour": colour, "measured_shape": shape,
             "fill_ratio": round(ratio, 3),
             "plan_size_px": o["size_px"], "plan_shape": o["shape"],
             "plan_colour": o["colour"], "plan_centre": o["centre"],
             "plan_subject_box": o["subject_box"],
             "centre_error_px": round(math.dist((cx, cy), o["centre"]), 2)}
        measured.append(m)
        if abs(w - o["size_px"]) > 2 or abs(h - o["size_px"]) > 2:
            problems.append(f"{o['id']}: size {w}x{h} vs plan {o['size_px']}")
        if shape != o["shape"]:
            problems.append(f"{o['id']}: shape reads {shape}, plan {o['shape']}")
        if colour != o["colour"]:
            problems.append(f"{o['id']}: colour reads {colour}, plan {o['colour']}")
        if m["centre_error_px"] > 3:
            problems.append(f"{o['id']}: centre off by {m['centre_error_px']}")
        lb = o["id_label_box"]
        if not (lb[1] >= o["subject_box"][3] - 1):
            problems.append(f"{o['id']}: label box overlaps the subject")

    agg = aggregate(measured)
    checks = {
        "64_bodies_found": len(measured) == 64,
        "colour_counts": agg["colour"], "shape_counts": agg["shape"],
        "size_counts": agg["size"],
        "combinations_present": len(agg["combos"]),
        "sizes_per_colour": agg["sizes_per_colour"],
        "sizes_per_shape": agg["sizes_per_shape"],
        "rows_min_colours": agg["row_min_colours"],
        "rows_min_shapes": agg["row_min_shapes"],
        "no_body_crosses_cell": agg["all_inside_cell"],
        "measured_matches_plan": not problems,
    }
    for k, v in (("colour_counts", agg["colour"]), ("shape_counts", agg["shape"])):
        if sorted(v.values()) != [16, 16, 16, 16]:
            problems.append(f"measured {k} = {v}")
    if len(agg["combos"]) != 16:
        problems.append(f"measured combinations = {len(agg['combos'])}")
    if agg["row_min_colours"] < 3 or agg["row_min_shapes"] < 3:
        problems.append("a row has fewer than 3 colours or shapes")

    # ---- occlusion
    occ = json.loads((TMP / f"{ver}-occlusion.json").read_text(encoding="utf-8"))
    pa = TMP / f"{ver}-occlusion.png"
    pb = TMP / f"{ver}-occlusion-alternative.png"
    A, sa, modea = rgba(pa)
    B, sb, modeb = rgba(pb)
    diff = np.abs(A.astype(int) - B.astype(int))
    differing = int((diff.max(axis=2) > 0).sum())
    sha = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (pa, pb)}
    arr_hash = {p.name: hashlib.sha256(np.asarray(rgba(p)[0]).tobytes()).hexdigest()
                for p in (pa, pb)}
    l, t, r, b = occ["occluder_box"]
    leak = []
    for key in ("hidden_A", "hidden_B"):
        for hid in occ[key]:
            oid, colour, shape, size, (cx, cy) = hid["id"], hid["colour"], hid["shape"], \
                hid["size_px"], hid["centre"]
            x0, y0 = int(cx - size / 2), int(cy - size / 2)
            x1, y1 = int(cx + size / 2), int(cy + size / 2)
            reg = A[y0 + 3:y1 - 3, x0 + 3:x1 - 3, :3].astype(int)
            not_occ = int((np.abs(reg - np.array(OCC)).sum(axis=2) > 40).sum())
            if not_occ:
                leak.append({"hidden": oid, "pixels_outside_occluder_colour": not_occ})
    occl_check = {
        "same_size": list(sa) == list(sb),
        "different_pixels": differing,
        "max_channel_difference": int(diff.max()),
        "decoder": f"Pillow {Image.__version__ if hasattr(Image, '__version__') else ''}"
                   "/PIL, convert('RGBA') 8-bit non-premultiplied",
        "file_sha256": sha, "pixel_array_sha256": arr_hash,
        "hidden_footprints_fully_covered": not leak,
        "hidden_leak_detail": leak,
        "passed": sa == sb and differing == 0 and not leak,
    }
    rep = {"version": ver, "grid": {"problems": problems, "checks": checks,
                                    "measured_objects": measured},
           "occlusion": occl_check}
    (TMP / f"{ver}-verify.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"grid_checks": {k: v for k, v in checks.items()
                                      if k != "measured_objects"},
                      "grid_problems": problems[:10],
                      "occlusion": {k: v for k, v in occl_check.items()
                                    if k != "file_sha256"}},
                     ensure_ascii=False, indent=1))


def classify_shape(img, body, comp):
    """Shape from three measurable facts, not from a single pixel.

    fill ratio separates circle (pi/4) from square (1.0); a 5x5 occupancy probe at each
    bounding-box corner separates square (filled) from rounded-square (radius is a
    quarter of the side, so the corner is empty); a ring is the only silhouette whose
    own centre is background.
    """
    x0, y0, x1, y1 = comp["bbox"]
    w, h = x1 - x0, y1 - y0
    ratio = comp["n"] / float(w * h)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    if int(np.abs(img[cy, cx] - np.array(PANEL_BG)).sum()) < 60:
        return "ring"
    q = max(2, min(5, w // 8))
    occ = []
    for (px, py) in ((x0, y0), (x0, y1 - q), (x1 - q, y0), (x1 - q, y1 - q)):
        win = body[py:py + q, px:px + q]
        occ.append(float(win.mean()))
    corner = sum(occ) / 4.0
    if corner > 0.7 and ratio > 0.93:
        return "square"
    if ratio > 0.85:
        return "rounded-square"
    return "circle"


def aggregate(measured):
    from collections import defaultdict
    col, shp, siz = defaultdict(int), defaultdict(int), defaultdict(int)
    combos, spc, sps = set(), defaultdict(set), defaultdict(set)
    rows_c, rows_s = defaultdict(set), defaultdict(set)
    inside = True
    for m in measured:
        col[m["measured_colour"]] += 1
        shp[m["measured_shape"]] += 1
        siz[m["measured_size_px"][0]] += 1
        combos.add((m["measured_colour"], m["measured_shape"]))
        spc[m["measured_colour"]].add(m["measured_size_px"][0])
        sps[m["measured_shape"]].add(m["measured_size_px"][0])
        n = int(m["id"][1:])
        rows_c[(n - 1) // 8 + 1].add(m["measured_colour"])
        rows_s[(n - 1) // 8 + 1].add(m["measured_shape"])
        x0, y0, x1, y1 = m["measured_bbox"]
        r, c = (n - 1) // 8, (n - 1) % 8
        if not (c * CELL <= x0 and x1 <= (c + 1) * CELL and r * CELL <= y0
                and y1 <= (r + 1) * CELL):
            inside = False
    return {"colour": dict(col), "shape": dict(shp), "size": dict(siz),
            "combos": sorted(combos),
            "sizes_per_colour": {k: sorted(v) for k, v in spc.items()},
            "sizes_per_shape": {k: sorted(v) for k, v in sps.items()},
            "row_min_colours": min(len(v) for v in rows_c.values()),
            "row_min_shapes": min(len(v) for v in rows_s.values()),
            "all_inside_cell": inside}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ver", default="v001")
    a = ap.parse_args()
    main(a.ver)

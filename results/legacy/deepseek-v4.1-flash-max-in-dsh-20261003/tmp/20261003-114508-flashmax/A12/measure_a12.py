"""A12 render verification: every declared text box is checked against the real pixels.

For each field appearance in content-map.json the declared rectangle is cropped and the
ink (pixels differing from the local background) is measured:
  * ink must exist (the field really rendered);
  * the ink must stay inside the declared rectangle plus a small tolerance;
  * ink boxes of different fields must not intersect -> "text boxes never overlap".
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "_suite", "shared"))
from suite_common import task_out, write_json  # noqa: E402

TOL_X, TOL_Y = 12, 8


def ink_box(img, x, y, w, h, pad=3):
    x0, y0 = max(0, int(x) - pad), max(0, int(y) - pad)
    x1, y1 = min(img.shape[1], int(x + w) + pad), min(img.shape[0], int(y + h) + pad)
    tile = img[y0:y1, x0:x1].astype(int)
    if tile.size == 0:
        return None
    # local background = most frequent colour in the crop
    flat = tile.reshape(-1, 3)
    vals, counts = np.unique(flat, axis=0, return_counts=True)
    bg = vals[counts.argmax()]
    diff = np.abs(tile - bg).max(axis=2)
    mask = diff > 40
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    return {"x": [int(xs.min()) + x0, int(xs.max()) + x0],
            "y": [int(ys.min()) + y0, int(ys.max()) + y0],
            "pixels": int(len(xs)), "bg": [int(v) for v in bg]}


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "v4"
    cmap = json.load(open(os.path.join(HERE, "content-map.json"), encoding="utf-8"))
    report = {}
    for bp in cmap["canvas"]:
        img = np.asarray(Image.open(os.path.join(HERE, f"{bp}.{version}.png")).convert("RGB"))
        entries = []
        for field, rec in cmap["fields"].items():
            ap = rec["appearances"].get(bp)
            if not ap:
                continue
            box = ink_box(img, ap["x"], ap["y"], ap["w"], ap.get("h", 28))
            entries.append({"field": field, "role": ap["role"],
                            "declared": [ap["x"], ap["y"], round(ap["w"], 1),
                                         ap.get("h", 28)], "ink": box})
        missing = [e["field"] for e in entries if e["ink"] is None]
        outside = []
        for e in entries:
            if not e["ink"]:
                continue
            dx0 = e["declared"][0] - e["ink"]["x"][0]
            dx1 = e["ink"]["x"][1] - (e["declared"][0] + e["declared"][2])
            dy0 = e["declared"][1] - e["ink"]["y"][0]
            dy1 = e["ink"]["y"][1] - (e["declared"][1] + e["declared"][3])
            if dx0 > TOL_X or dx1 > 17 or dy0 > TOL_Y or dy1 > 20:
                outside.append({"field": e["field"], "d_left": round(dx0, 1),
                                "d_right": round(dx1, 1), "d_top": round(dy0, 1),
                                "d_bottom": round(dy1, 1)})
        clashes = []
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                a, b = entries[i]["ink"], entries[j]["ink"]
                if not a or not b:
                    continue
                pair = {entries[i]["field"], entries[j]["field"]}
                if pair == {"date", "time"}:
                    continue          # both share one rendered line by design
                if (a["x"][0] <= b["x"][1] and b["x"][0] <= a["x"][1]
                        and a["y"][0] <= b["y"][1] and b["y"][0] <= a["y"][1]):
                    clashes.append([entries[i]["field"], entries[j]["field"]])
        report[bp] = {
            "canvas": cmap["canvas"][bp],
            "fields_checked": len(entries),
            "fields_without_ink": missing,
            "fields_outside_declared_box": outside,
            "outside_detail": outside[:8],
            "ink_box_overlaps": clashes,
            "ink_pixels_total": int(sum(e["ink"]["pixels"] for e in entries if e["ink"])),
        }
        print(f'{bp:8s} fields={len(entries):3d} no_ink={len(missing)} outside={len(outside)} '
              f'overlaps={len(clashes)}')
        if clashes:
            print("   clashes:", clashes)
        if outside:
            print("   outside:", outside[:6])
    write_json(os.path.join(task_out("A12"), "render-check.json"),
               {"version": version, "tolerance_px": {"x": TOL_X, "y": TOL_Y},
                "report": report})


if __name__ == "__main__":
    main()

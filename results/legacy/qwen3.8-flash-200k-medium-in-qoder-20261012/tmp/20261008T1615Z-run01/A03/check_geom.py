"""A03 self-check: measure rendered geometry from the real PNG instead of trusting the DSL.

Run from suite root:
  python tmp/<run_id>/A03/check_geom.py --img outputs/<run_id>/A03/system-pulse.png
Writes a JSON report next to the image (or --out) and prints a compact table.
"""
import argparse
import json
import os
from pathlib import Path

from PIL import Image

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
ap = argparse.ArgumentParser()
ap.add_argument("--img", required=True)
ap.add_argument("--out", default=None)
ap.add_argument("--margin", type=int, default=32)
a = ap.parse_args()

img = Image.open(a.img).convert("RGB")
W, H = img.size
px = img.load()


def hx(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def bbox(color, region=None, tol=8):
    """Bounding box of pixels within `tol` of `color`; region = (x0,y0,x1,y1)."""
    c = hx(color)
    x0, y0, x1, y1 = region or (0, 0, W, H)
    minx = miny = 10 ** 9
    maxx = maxy = -1
    for y in range(y0, min(y1, H)):
        for x in range(x0, min(x1, W)):
            p = px[x, y]
            if abs(p[0] - c[0]) <= tol and abs(p[1] - c[1]) <= tol and abs(p[2] - c[2]) <= tol:
                if x < minx:
                    minx = x
                if x > maxx:
                    maxx = x
                if y < miny:
                    miny = y
                if y > maxy:
                    maxy = y
    if maxx < 0:
        return None
    return {"x": minx, "y": miny, "w": maxx - minx + 1, "h": maxy - miny + 1}


def outside_ring(color, margin, tol=8):
    """Count non-background pixels inside the outer `margin` ring."""
    c = hx(color)
    bad = []
    for y in range(H):
        for x in range(W):
            if not (x < margin or y < margin or x >= W - margin or y >= H - margin):
                continue
            p = px[x, y]
            if max(abs(p[0] - c[0]), abs(p[1] - c[1]), abs(p[2] - c[2])) > tol:
                bad.append((x, y))
    return {"count": len(bad), "first": bad[:5]}


rep = {"image": str(Path(a.img).relative_to(root)) if Path(a.img).is_absolute() else a.img,
       "canvas": {"w": W, "h": H},
       "safe_margin_ring_offbackground": outside_ring("#0B1220", a.margin)}
rep["title_ink_bbox"] = bbox("#FFFFFF", (0, 0, 900, 130))
rep["live_pill"] = bbox("#34D399", (900, 0, W, 120))
rep["metric_card_border"] = bbox("#33456A", (0, 120, W, 330))
rep["blur_card_border"] = bbox("#4A5F86")
rep["strip_blue_full"] = bbox("#38BDF8", (200, 380, W, 520))
rep["review_text"] = bbox("#FFFFFF", (900, 600, W, H))
rep["bars_blue"] = bbox("#38BDF8", (150, 500, W, H))
print(json.dumps(rep, indent=1, ensure_ascii=False))
out = Path(a.out or (str(Path(a.img).with_suffix("")) + "-geom.json"))
out.write_text(json.dumps({"path_base": "suite_root", **rep}, indent=1,
                          ensure_ascii=False), encoding="utf-8")
print(f"wrote {out}")

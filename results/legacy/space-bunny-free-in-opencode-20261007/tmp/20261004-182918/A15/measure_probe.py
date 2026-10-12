"""Measure the A15 calibration probe: ink bbox vs declared box origin, per probe."""
import json
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "A15")
PNG = os.path.join(TMP, "probes", "probe-v00.png")
META = os.path.join(TMP, "probe-meta.json")
OUT = os.path.join(TMP, "probe-measurements.json")

im = Image.open(PNG).convert("RGB")
px = im.load()
W, H = im.size
meta = json.load(open(META, encoding="utf-8"))


def rgb(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def ink(x0, x1, y0, y1, bg=(255, 255, 255), tol=18):
    minx = miny = maxx = maxy = None
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            if sum(abs(px[x, y][i] - bg[i]) for i in range(3)) > tol:
                minx = x if minx is None else min(minx, x)
                maxx = x if maxx is None else max(maxx, x)
                miny = y if miny is None else min(miny, y)
                maxy = y if maxy is None else max(maxy, y)
    if minx is None:
        return None
    return {"bbox": [minx, miny, maxx, maxy], "w": maxx - minx + 1, "h": maxy - miny + 1}


rows = []
for m in meta:
    bx, by, bw, bh = m["box"]
    col = rgb(m["color"])
    # white background rows: light text on white still fine; dark text on white fine.
    # For near-white text (FFFFFFFF) probe areas were placed on white -> invisible;
    # those keys are skipped by caller.
    if m["color"].upper() in ("#FFFFFFFF",):
        rows.append({**m, "ink": None, "skip": "white-on-white"})
        continue
    r = ink(bx - 2, bx + bw + 2, by - 2, by + bh + 2, (255, 255, 255), 18)
    if r is None:
        rows.append({**m, "ink": None})
        continue
    rows.append({**m, "ink": r,
                 "dx_left": r["bbox"][0] - bx,
                 "dy_top": r["bbox"][1] - by,
                 "ink_w": r["w"], "ink_h": r["h"]})

json.dump(rows, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("%-12s %-34s %-4s %-4s %5s %5s %5s %5s" % ("key", "text", "size", "font", "dxL", "dyT", "inkW", "inkH"))
for r in rows:
    if r["ink"] is None:
        print("%-12s %-34s %-4s %-4s  (skipped)" % (r["key"], r["text"][:32], r["size"],
                                                    r["font"].split()[-1]))
        continue
    print("%-12s %-34s %-4s %-4s %5d %5d %5d %5d" % (
        r["key"], r["text"][:32], r["size"], r["font"].split()[-1],
        r["dx_left"], r["dy_top"], r["ink_w"], r["ink_h"]))
print("\nwrote", OUT)

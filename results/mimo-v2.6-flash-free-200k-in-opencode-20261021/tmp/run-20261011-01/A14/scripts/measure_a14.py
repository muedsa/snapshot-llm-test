# -*- coding: utf-8 -*-
"""Pixel measurement of the A14 wall render (real numbers for card-results.json).

For every card declared in layout-vN.json:
  - per-field ink measurement inside the declared box (+6px search window)
    * visible: ink pixel count >= 30
    * overflow: ink touches the outer 2px ring of the search window
  - actual_box: union bbox of all text ink inside the card region
  - card containment: actual_box must be inside declared card box (+2 AA tol)

Wall level: PNG size must be exactly 1440x1800; global ink bbox vs the
60px safe margin (background gradient excluded via brightness threshold).

Usage: measure_a14.py <wall.png> <layout.json> [tag]
Writes tmp/run-20261011-01/A14/measured-<tag>.json
"""
import json
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(".")
OUT = ROOT / "tmp" / "run-20261011-01" / "A14"
BRIGHT = 80          # background/card fill luminance stays below this
EXPAND = 6           # search window beyond declared box
TOL = 6              # overflow trigger: ink beyond box + TOL

wall_path = pathlib.Path(sys.argv[1])
layout = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
tag = sys.argv[3] if len(sys.argv) > 3 else "v"

img = Image.open(wall_path).convert("RGB")
W, H = img.size
px = img.load()


def is_ink(x, y):
    r, g, b = px[x, y]
    return (r * 299 + g * 587 + b * 114) // 1000 > BRIGHT


def measure_box(bx1, by1, bx2, by2):
    x1, y1 = max(0, bx1 - EXPAND), max(0, by1 - EXPAND)
    x2, y2 = min(W - 1, bx2 + EXPAND), min(H - 1, by2 + EXPAND)
    xs, ys, n = [], [], 0
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if is_ink(x, y):
                xs.append(x)
                ys.append(y)
                n += 1
    if n == 0:
        return {"ink_count": 0, "visible": False, "overflow": False,
                "ink_bbox": None}
    # overflow: any ink in the outer 2px ring of the search window
    ring = set()
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if (x < x1 + 2 or x > x2 - 2 or y < y1 + 2 or y > y2 - 2):
                if is_ink(x, y):
                    ring.add((x, y))
    return {"ink_count": n, "visible": n >= 30, "overflow": len(ring) > 0,
            "ink_bbox": [min(xs), min(ys), max(xs), max(ys)]}


results = {
    "wall": {"png": str(wall_path).replace("\\", "/"), "size": [W, H],
             "expected_size": [1440, 1800],
             "size_ok": [W, H] == [1440, 1800]},
    "cards": [],
    "failures": [],
}

# global ink bbox (safe margin check)
gxs, gys = [], []
for y in range(0, H, 2):
    for x in range(0, W, 2):
        if is_ink(x, y):
            gxs.append(x)
            gys.append(y)
gbox = [min(gxs), min(gys), max(gxs), max(gys)]
results["wall"]["global_ink_bbox_step2"] = gbox
results["wall"]["safe_margin_ok"] = (gbox[0] >= 58 and gbox[1] >= 58 and
                                     gbox[2] <= W - 59 and
                                     gbox[3] <= H - 59)

FIELDS = ["time_box", "speaker_box", "id_pill_box", "status_pill_box"]


def measure_title_lines(rec, cid):
    """Band analysis for stacked title lines.

    Individual +/-6 windows of adjacent lines overlap (line step 35px <
    box height 37px + 12), which yields false overflow -- same window-bleed
    gotcha as A12. Instead: profile ink rows over the whole title region
    (first box top -6 .. last box bottom +6), group into bands (gap >= 3px
    separates lines), then check:
      * band count == expected line count (more => service soft-wrapped)
      * first band top >= first box top -2, last band bottom <= last box bottom +2
      * every band horizontal extent <= box width +4 (no side overflow)
    """
    boxes = rec["title_line_boxes"]
    n = len(boxes)
    x1 = boxes[0][0] - 6
    x2 = boxes[0][2] + 6
    y1 = boxes[0][1] - 6
    y2 = boxes[-1][3] + 6
    rows = []
    for y in range(y1, y2 + 1):
        cnt = 0
        xs = []
        for x in range(x1, x2 + 1):
            if is_ink(x, y):
                cnt += 1
                xs.append(x)
        rows.append((y, cnt, xs))
    bands = []
    cur = None
    last_ink_y = None
    for y, cnt, xs in rows:
        if cnt > 0:
            if cur is None:
                cur = {"y1": y, "y2": y, "x1": min(xs), "x2": max(xs), "n": cnt}
            else:
                if last_ink_y is not None and y - last_ink_y >= 3:
                    bands.append(cur)
                    cur = {"y1": y, "y2": y, "x1": min(xs), "x2": max(xs),
                           "n": cnt}
                else:
                    cur["y2"] = y
                    cur["x1"] = min(cur["x1"], min(xs))
                    cur["x2"] = max(cur["x2"], max(xs))
                    cur["n"] += cnt
            last_ink_y = y
    if cur:
        bands.append(cur)
    per = [{"band": b, "visible": b["n"] >= 30, "overflow": False}
           for b in bands]
    probs = []
    if len(bands) != n:
        probs.append(f"{cid}.title expected {n} line bands, found "
                     f"{len(bands)} (soft-wrap or missing line)")
    if bands:
        if bands[0]["y1"] < boxes[0][1] - 2:
            probs.append(f"{cid}.title first line ink starts at y={bands[0]['y1']} "
                         f"above box top {boxes[0][1]}")
        if bands[-1]["y2"] > boxes[-1][3] + 2:
            probs.append(f"{cid}.title last line ink ends at y={bands[-1]['y2']} "
                         f"below box bottom {boxes[-1][3]}")
        bw = boxes[0][2] - boxes[0][0]
        for i, b in enumerate(bands):
            if b["x2"] - b["x1"] + 1 > bw + 4:
                probs.append(f"{cid}.title band[{i}] width "
                             f"{b['x2'] - b['x1'] + 1} > box width {bw} + 4")
        for i, b in enumerate(bands):
            if b["n"] < 30:
                probs.append(f"{cid}.title band[{i}] too few ink pixels "
                             f"({b['n']}) -- not visible")
    return per, probs


for rec in layout["cards"]:
    cid = rec["id"]
    cx1, cy1, cx2, cy2 = rec["declared_box"]
    fields = {}
    tbands, tprobs = measure_title_lines(rec, cid)
    fields["title_line_boxes"] = tbands
    results["failures"] += tprobs
    for fname in FIELDS:
        boxes = [rec[fname]]
        per = []
        for i, b in enumerate(boxes):
            m = measure_box(*b)
            per.append(m)
            if not m["visible"]:
                results["failures"].append(f"{cid}.{fname}[{i}] not visible "
                                           f"(ink={m['ink_count']})")
            if m["overflow"]:
                results["failures"].append(f"{cid}.{fname}[{i}] overflow "
                                           f"(ink beyond box+{TOL})")
        fields[fname] = per
    # card text ink union (within card region only)
    xs, ys = [], []
    for y in range(cy1, cy2 + 1):
        for x in range(cx1, cx2 + 1):
            if is_ink(x, y):
                xs.append(x)
                ys.append(y)
    actual = [min(xs), min(ys), max(xs), max(ys)] if xs else None
    contained = (actual is not None and
                 actual[0] >= cx1 - 2 and actual[1] >= cy1 - 2 and
                 actual[2] <= cx2 + 2 and actual[3] <= cy2 + 2)
    if not contained:
        results["failures"].append(f"{cid} text ink escapes card box: "
                                   f"{actual} vs {rec['declared_box']}")
    all_visible = all(all(p["visible"] for p in per) for per in fields.values())
    any_overflow = any(p["overflow"] for per in fields.values() for p in per)
    results["cards"].append({
        "id": cid,
        "fields": fields,
        "actual_box": actual,
        "card_box": rec["declared_box"],
        "contained": contained,
        "visible_all_fields": all_visible,
        "any_overflow": any_overflow,
        "title_font_size": rec["title_font_size"],
        "title_line_count": rec["title_line_count"],
        "title_truncated": rec["title_truncated"],
        "warnings": rec["warnings"],
    })

results["all_visible"] = all(c["visible_all_fields"] for c in results["cards"])
results["any_overflow"] = any(c["any_overflow"] for c in results["cards"])
results["no_failures"] = len(results["failures"]) == 0

out = OUT / f"measured-{tag}.json"
out.write_text(json.dumps(results, ensure_ascii=False, indent=2),
               encoding="utf-8")
print(f"size_ok={results['wall']['size_ok']} "
      f"safe_margin_ok={results['wall']['safe_margin_ok']} "
      f"all_visible={results['all_visible']} "
      f"any_overflow={results['any_overflow']} "
      f"failures={len(results['failures'])}")
for f in results["failures"]:
    print("  FAIL:", f)
print("->", out)

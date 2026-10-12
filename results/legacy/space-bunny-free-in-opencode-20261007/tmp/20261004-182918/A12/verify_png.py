"""A12 delivery verification: measure the real ink of every content field in the
delivered PNGs and compare it with the width the generator intended to draw.

This is the check that catches silent truncation: if a Text box is narrower than
its string, the service wraps the line and clips the overflow with no error, so
the rendered ink comes out SHORTER than the generator's own measurement. Comparing
measured ink against expected ink per field turns that invisible failure into a
hard pass/fail.
"""
from __future__ import annotations

import json
import os

import numpy as np
from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A12")
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A12")

# Matching an exact RGB loses ~1 anti-aliased pixel at each end of a run, so the
# rendered ink measures 2-3 px shorter than the grey-background probe. A genuine
# wrap-and-clip loses a whole word (tens of px), so a 4 px floor cleanly separates
# "rasterisation edge" from "content lost".
EDGE_PX = 4

with open(os.path.join(OUT, "content-map.json"), encoding="utf-8") as fh:
    CM = json.load(fh)

EXPECT_SIZE = {"mobile": (360, 800), "tablet": (768, 1024),
               "desktop": (1440, 900), "stage": (1920, 1080)}


def parse_hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def match_mask(sub, hexcolor, tol=46):
    """Isolate glyph pixels of one text colour.

    The canvas holds many elements of similar brightness (the ghost index and the
    corner ticks share the same accent at 20% alpha), so a plain brightness
    threshold gives false 'ink wider than expected' readings. Matching the exact
    RGB keeps each measurement to its own text run.
    """
    t = np.array(parse_hex(hexcolor))
    return np.abs(sub - t).sum(axis=2) < tol


report = {"canvases": [], "failures": [], "checks": 0,
          "edge_tolerance_px": EDGE_PX}
for cv in CM["canvases"]:
    name = cv["canvas"]
    im = Image.open(os.path.join(OUT, cv["png"])).convert("RGB")
    a = np.array(im).astype(int)
    entry = {"canvas": name, "png": cv["png"], "size": list(im.size),
             "expected_size": list(EXPECT_SIZE[name]), "fields": [], "ok": True}
    if im.size != EXPECT_SIZE[name]:
        entry["ok"] = False
        report["failures"].append("%s: size %s != %s"
                                   % (name, im.size, EXPECT_SIZE[name]))
    for f in cv["content_fields"]:
        box, ink = f["box"], f["ink_extent"]
        y0 = max(0, int(ink["y0"]) - 3)
        y1 = min(a.shape[0], int(ink["y1"]) + 4)
        x0 = max(0, int(box["x"]) - 4)
        x1 = min(a.shape[1], int(box["x"] + box["w"]) + 8)
        sub = a[y0:y1, x0:x1]
        cols = np.where(match_mask(sub, f["text_color"]).any(axis=0))[0]
        rec = {"field": f["field"], "drawn": f["drawn_text"],
               "font_size": f["font_size"],
               "expected_ink_px": f["expected_ink_px"], "box_w": box["w"]}
        if len(cols) == 0:
            rec.update({"status": "NO_INK", "rendered_ink_px": 0})
            entry["ok"] = False
            report["failures"].append("%s %s: no ink of colour %s in %s"
                                       % (name, f["field"], f["text_color"], box))
        else:
            got = int(cols.max() - cols.min() + 1)
            exp = f["expected_ink_px"]
            rec["rendered_ink_px"] = got
            rec["rendered_left"] = x0 + int(cols.min())
            rec["expected_left"] = ink["x0"]
            rec["left_delta"] = round(rec["rendered_left"] - rec["expected_left"], 2)
            rec["ink_delta"] = got - exp
            if got < exp - EDGE_PX:
                rec["status"] = "CLIPPED_OR_WRAPPED"
                entry["ok"] = False
                report["failures"].append(
                    "%s %s: rendered ink %d px < expected %d px (drawn %r)"
                    % (name, f["field"], got, exp, f["drawn_text"]))
            else:
                rec["status"] = "OK"
        entry["fields"].append(rec)
        report["checks"] += 1
    entry["field_count"] = len(entry["fields"])
    report["canvases"].append(entry)

for cv in CM["canvases"]:
    name, W, H = cv["canvas"], cv["width"], cv["height"]
    m = cv["safe_margin_px"]
    worst = {"left": 1e9, "right": 1e9, "top": 1e9, "bottom": 1e9}
    for f in cv["content_fields"]:
        b = f["box"]
        worst["left"] = min(worst["left"], b["x"])
        worst["right"] = min(worst["right"], W - (b["x"] + b["w"]))
        worst["top"] = min(worst["top"], b["y"])
        worst["bottom"] = min(worst["bottom"], H - (b["y"] + b["h"]))
    ok = (min(worst["left"], worst["right"]) >= m - 0.5 and
          min(worst["top"], worst["bottom"]) >= m - 0.5)
    cv["measured_margins_px"] = {k: round(v, 1) for k, v in worst.items()}
    cv["margins_ok"] = ok
    if not ok:
        report["failures"].append("%s: safe margin violated %s (required %d)"
                                   % (name, cv["measured_margins_px"], m))

for cv in CM["canvases"]:
    bad = [f for f in next(c for c in report["canvases"]
                           if c["canvas"] == cv["canvas"])["fields"]
           if f["status"] != "OK"]
    print("%-8s size=%-10s margins_ok=%-5s %s  fields=%d  problems=%d"
          % (cv["canvas"], "%dx%d" % (cv["width"], cv["height"]),
             cv["margins_ok"], cv["measured_margins_px"],
             len(cv["content_fields"]), len(bad)))
    for f in bad:
        print("    !!", f)

report["all_ok"] = not report["failures"]
with open(os.path.join(TMP, "verify-png.json"), "w", encoding="utf-8") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=2)
CM["verification"] = {
    "method": "per-field ink measurement on the delivered PNGs: each content field "
              "is isolated by its exact RGB and its rendered ink width is compared "
              "with the width measured from the service in probe_metrics.py",
    "edge_tolerance_px": EDGE_PX,
    "detail_log": "tmp/20261004-182918/A12/verify-png.json",
    "fields_checked": report["checks"],
    "failures": report["failures"],
    "all_ok": report["all_ok"],
    "canvas_sizes_ok": all(c["size"] == c["expected_size"]
                           for c in report["canvases"]),
}
with open(os.path.join(OUT, "content-map.json"), "w", encoding="utf-8") as fh:
    json.dump(CM, fh, ensure_ascii=False, indent=2)
print("\nchecks=%d failures=%d all_ok=%s"
      % (report["checks"], len(report["failures"]), report["all_ok"]))
for f in report["failures"]:
    print("  FAIL:", f)
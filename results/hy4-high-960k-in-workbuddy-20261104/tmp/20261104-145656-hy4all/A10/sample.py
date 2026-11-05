#!/usr/bin/env python3
"""A10 pixel sampling: read the real service PNG at the two (180,100) sample
points and fill in composite-audit.json samples[] with actual RGB/alpha/errors.
"""
import json, os, sys
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
import suite
from PIL import Image

TASK = "A10"
OUT = suite.out_dir(TASK)
AUD = OUT / "composite-audit.json"
PNG = OUT / "compositing-lab.png"

audit = json.loads(AUD.read_text(encoding="utf-8"))
im = Image.open(PNG).convert("RGBA")
assert im.size == (1440, 1100), im.size
px = im.load()

for s in audit["samples"]:
    x, y = s["canvas_pixel"]
    r, g, b, a = px[x, y]
    actual = [r, g, b]
    errs = [abs(actual[i] - s["rounded_rgb"][i]) for i in range(3)]
    s["actual_rgb"] = actual
    s["actual_alpha"] = a
    s["channel_errors"] = errs
    s["max_channel_error"] = max(errs)
    s["alpha_is_255"] = (a == 255)
    s["passed"] = (a == 255) and all(e <= s["tolerance_per_channel"] for e in errs)
    s["pending_reason"] = None
    print("panel %d sample (%d,%d): rounded=%s actual=%s alpha=%d errors=%s passed=%s" %
          (s["panel"], x, y, s["rounded_rgb"], actual, a, errs, s["passed"]))

AUD.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("all samples passed:", all(s["passed"] for s in audit["samples"]))

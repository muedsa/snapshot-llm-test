#!/usr/bin/env python3
"""A23 smoke test: transparent RGBA canvas + rotated coloured polygons + 8-digit alpha.
Verifies Snapshot background=transparent, ClipPath vertex-rotation geometry, and alpha.
Process evidence only (not a final deliverable)."""
import math, os, subprocess, sys, struct
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas
import suite

TASK = "A23"
smoke = suite.tmp_dir(TASK, "_smoke")


def rot(points, cx, cy, deg):
    a = math.radians(deg)
    co, si = math.cos(a), math.sin(a)
    return [(cx + x * co - y * si, cy + x * si + y * co) for x, y in points]


def diamond(w, h):
    return [(0, -h / 2), (w / 2, 0), (0, h / 2), (-w / 2, 0)]


c = Canvas(600, 600, "transparent")
# rotated diamonds (clockwise degrees) with fixed RGBA colours
c.poly(rot(diamond(120, 180), 180, 180, 30), "#2563EBFF")
c.poly(rot(diamond(120, 180), 420, 180, -20), "#F59E0BCC")
c.poly(rot(diamond(120, 180), 300, 410, 75), "#10B981E6")
c.rect(60, 460, 190, 90, "#E11D48FF", radius=12)
c.circle(500, 470, 55, "#7C3AEDB3")

dsl = c.render()
snap = smoke / "test.snapshot"
snap.write_text(dsl, encoding="utf-8")
print("DSL bytes:", len(dsl.encode("utf-8")))

png = smoke / "test.png"
cmd = [sys.executable, str(Path(TOOLS) / "render.py"),
       "--dsl", str(snap), "--out", str(png), "--task", TASK,
       "--label", "smoke-transparent", "--logdir", str(smoke),
       "--suite-root", str(suite.ROOT), "--retries", "1"]
p = subprocess.run(cmd, capture_output=True, text=True)
print("render stdout:", (p.stdout or "").strip()[-600:])
print("render stderr:", (p.stderr or "").strip()[-300:])

if not png.exists():
    print("SMOKE FAIL: no PNG")
    sys.exit(1)
raw = png.read_bytes()
print("PNG sig:", raw[:8], "bytes:", len(raw))
w, h = struct.unpack(">II", raw[16:24])
print("IHDR: w=%d h=%d bitdepth=%d colortype=%d" % (w, h, raw[24], raw[25]))

from PIL import Image
im = Image.open(png)
print("PIL mode:", im.mode, "size:", im.size)
rgba = im.convert("RGBA")
px = list(rgba.getdata())
n = len(px)
a0 = sum(1 for r, g, b, a in px if a == 0)
a255 = sum(1 for r, g, b, a in px if a == 255)
amid = n - a0 - a255
print("alpha hist: a=0 -> %d (%.1f%%), 0<a<255 -> %d (%.1f%%), a=255 -> %d (%.1f%%)" % (
    a0, a0 * 100 / n, amid, amid * 100 / n, a255, a255 * 100 / n))
print("corner alphas:", [rgba.getpixel(p)[3] for p in [(0, 0), (599, 0), (0, 599), (599, 599), (300, 300)]])
ok = (raw[:8] == b"\x89PNG\r\n\x1a\n" and w == 600 and h == 600 and raw[25] == 6
      and a0 > 0 and a255 > 0 and amid > 0 and rgba.getpixel((0, 0))[3] == 0)
print("SMOKE", "PASS" if ok else "FAIL")

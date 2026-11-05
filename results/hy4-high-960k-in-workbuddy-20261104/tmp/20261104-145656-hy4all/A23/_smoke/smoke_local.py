#!/usr/bin/env python3
"""Smoke: local-bounding-box ClipPath (small Container) rotating polygons, plus /ready probe."""
import math, os, struct, subprocess, sys, time, urllib.request
from pathlib import Path

TOOLS = os.environ["TOOLS"]; RID = os.environ["SNAPSHOT_RUN_ID"]
LD = Path("tmp") / RID / "A23" / "_smoke"

for path in ("/health", "/ready"):
    try:
        with urllib.request.urlopen("https://open-snapshot.muedsa.com" + path, timeout=10) as r:
            print(path, r.status, r.read(120).decode("utf-8", "replace").strip())
    except Exception as e:
        print(path, "ERR", repr(e)[:160])


def geom(w, h):
    return [(0, -h / 2), (w / 2, 0), (0, h / 2), (-w / 2, 0)]


def rot(pts, cx, cy, deg):
    a = math.radians(deg); co, si = math.cos(a), math.sin(a)
    return [(cx + x * co - y * si, cy + x * si + y * co) for x, y in pts]


def local_unit(pts, color):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    w, h = x1 - x0, y1 - y0
    d = "M%.2f %.2f " % (pts[0][0] - x0, pts[0][1] - y0) + \
        " ".join("L%.2f %.2f" % (p[0] - x0, p[1] - y0) for p in pts[1:]) + " Z"
    return ('<Positioned left="%.2f" top="%.2f" width="%.2f" height="%.2f">'
            '<ClipPath path="%s" clipBehavior="ANTI_ALIAS">'
            '<Container width="%.2f" height="%.2f" color="%s" />'
            '</ClipPath></Positioned>' % (x0, y0, w, h, d, w, h, color))


items = [
    local_unit(rot(geom(60, 140), 170, 170, 30), "#2563EBFF"),
    local_unit(rot(geom(60, 140), 420, 180, -25), "#F59E0BCC"),
    local_unit(rot(geom(60, 140), 300, 420, 75), "#10B981E6"),
]
dsl = ('<Snapshot background="transparent" type="png">\n'
       '<Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">\n'
       '<Container width="600" height="600" />\n' + "\n".join(items) + '\n</Stack>\n</Snapshot>\n')
f = LD / "smoke_local.snapshot"; f.write_text(dsl, encoding="utf-8")
out = LD / "smoke_local.png"
cmd = [sys.executable, str(Path(TOOLS) / "render.py"), "--dsl", str(f), "--out", str(out),
       "--task", "A23", "--label", "smoke-local", "--logdir", str(LD),
       "--suite-root", os.environ["SNAPSHOT_TASK_ROOT"], "--retries", "0"]
t = time.time()
p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
print("render %.1fs rc=%s %s" % (time.time() - t, p.returncode, p.stdout.strip()[-240:]))
if out.exists():
    raw = out.read_bytes()
    print("sig", raw[:8], "colortype", raw[25], "bytes", len(raw))
    from PIL import Image
    im = Image.open(out).convert("RGBA")
    a0 = sum(1 for px in im.getdata() if px[3] == 0)
    print("alpha=0 pixels", a0, "of", im.width * im.height)

# -*- coding: utf-8 -*-
"""Zone-wise diff analysis for probe/example-04 + status check of variant
requests; also fix handbook variant removal (skip CDATA code lines)."""
import json
import pathlib
from PIL import Image, ImageChops

TMP = pathlib.Path("tmp/run-20261011-01/A17")

# 1) request statuses of the variant renders
print("== variant request statuses")
log = TMP / "requests.jsonl"
for line in log.read_text(encoding="utf-8").splitlines():
    try:
        rec = json.loads(line)
    except Exception:
        continue
    if str(rec.get("id", "")).startswith("A17-nobf") or str(
            rec.get("id", "")).startswith("A17-exp"):
        print(f"  {rec['id']}: status={rec.get('status')} ok={rec.get('ok')} "
              f"err={rec.get('error')}")

ZONES = {
    "probe": {
        "zeros (text, before)": (0, 0, 1200, 60),
        "cjk (text, before)": (0, 60, 1200, 118),
        "row (container)": (20, 100, 460, 200),
        "center (container)": (500, 100, 940, 200),
        "rich (text)": (30, 195, 510, 290),
        "stripes2 (container)": (510, 195, 940, 290),
        "panel itself": (550, 212, 750, 268),
        "M line (text, after)": (0, 295, 1200, 360),
    },
    "example-04": {
        "stripes (container)": (0, 0, 400, 84),
        "solid purple (after filter)": (0, 84, 400, 160),
        "blurred purple (ImageFiltered)": (160, 84, 400, 160),
        "opacity bar (after)": (0, 160, 400, 240),
    },
}

for name, zones in ZONES.items():
    src = TMP / "scripts" / f"{name}.png" if name == "probe" else TMP / "gen" / f"{name}.png"
    a = Image.open(src).convert("RGB")
    b = Image.open(TMP / "variants" / f"{name}-nobf.png").convert("RGB")
    diff = ImageChops.difference(a, b)
    px = diff.load()
    W, H = a.size
    print(f"\n== {name} zone diffs (points with max-channel diff > 4)")
    for zname, (x0, y0, x1, y1) in zones.items():
        n = 0
        mx = 0
        for y in range(max(0, y0), min(H, y1), 2):
            for x in range(max(0, x0), min(W, x1), 2):
                d = max(px[x, y])
                if d > 4:
                    n += 1
                    mx = max(mx, d)
        print(f"  {zname}: points={n} maxdiff={mx}")

"""Crop-zoom helper: rebuild a DSL so a canvas region renders enlarged for visual QA.

Run from suite root. Usage:
  python tmp/<run_id>/_suite/scripts/zoom.py --in tmp/<run_id>/A01/v05.snapshot \
      --out tmp/<run_id>/A01/zoom-table.snapshot --x 40 --y 660 --w 780 --h 320
"""
import argparse
import os
import re
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="src", required=True)
ap.add_argument("--out", dest="dst", required=True)
ap.add_argument("--x", type=float, required=True)
ap.add_argument("--y", type=float, required=True)
ap.add_argument("--w", type=float, required=True)
ap.add_argument("--h", type=float, required=True)
ap.add_argument("--scale", type=float, default=2.0)
ap.add_argument("--canvas", default="1600x1000")
a = ap.parse_args()

CW, CH = [float(v) for v in a.canvas.split("x")]
dsl = Path(a.src).read_text(encoding="utf-8")
inner = re.search(r"<Snapshot[^>]*>(.*)</Snapshot>", dsl, re.S).group(1).strip()
g = a.scale
# NOTE: a Transform scale matrix drops rounded/coloured Containers on this
# renderer, so magnification must come from the generator's own SCALE factor.
if g != 1.0:
    raise SystemExit("zoom.py only crops; magnify via the generator SCALE env")
out = (
    f'<Snapshot background="#060B18" type="png">'
    f'<Container width="{a.w:g}" height="{a.h:g}">'
    f'<ClipRect><Stack alignment="TOP_LEFT" clipBehavior="NONE">'
    f'<Positioned left="{-a.x:g}" top="{-a.y:g}" width="{CW:g}" height="{CH:g}">'
    f'{inner}</Positioned></Stack></ClipRect></Container></Snapshot>'
)
Path(a.dst).write_text(out, encoding="utf-8")
print(f"{a.dst} region=({a.x},{a.y},{a.w}x{a.h}) scale={g}")

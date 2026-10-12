"""A10 exploratory probe: dump the raw pixel profiles the audit windows must be fitted to.

Kept as process evidence: the first check_a10.py run failed three of its own windows
(the ④ card edge is measured along the same axis the stripes oscillate on, the ⑥ radial
profile walked out of the dark rectangle, the ⑤ halo does not decay like a step edge).
"""
import json
import math
import os
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TEMP = ROOT / "tmp" / RID / "A10"
plan = json.loads((TEMP / "plan_a10.json").read_text(encoding="utf-8"))
im = Image.open(TEMP / "preview" / "v05.png").convert("RGB")
px = im.load()
CELL = {c["number"]: c for c in plan["cells"]}


def prof(label, pts, ch=2):
    print(label, " ".join(f"{a:g}:{px[int(round(a)), int(round(b))][ch]}" for a, b in pts))


# ⑤ halo above the filter box (content-local x=135, box top edge at canvas y=669)
a5 = CELL["⑤"]["area_origin"]
top = a5[1] + plan["shapes"]["content_box"]["xywh_in_area"][1]
prof("c5_halo_above (canvas y : B, box top=669)", [(755, y) for y in range(629, 676)])
prof("c5_halo_left (canvas x : B, box left=620)", [(x, 733) for x in range(596, 626)])

# ④ card top edge: mean R over a whole number of stripe periods, profiled along y
a4 = CELL["④"]["area_origin"]
col = list(range(64, 257))
rows = []
for y in range(10, 81):
    vals = [px[a4[0] + x, a4[1] + y][0] for x in col]
    rows.append((y, sum(vals) / len(vals)))
print("c4_top_edge_profile (area y : mean R over x 64..256)")
print(" ".join(f"{y:g}:{v:.1f}" for y, v in rows))

# ⑥ radial profile at 220 deg from the clip circle centre
a6 = CELL["⑥"]["area_origin"]
ctr = plan["filters"]["circle"]["center_area"]
ccx, ccy = a6[0] + ctr[0], a6[1] + ctr[1]
th = math.radians(220)
prof("c6_arc_220 (r : B)", [(ccx + r * math.cos(th), ccy + r * math.sin(th))
                            for r in range(86, 113)])
prof("c6_arc_220 (r : G)", [(ccx + r * math.cos(th), ccy + r * math.sin(th))
                            for r in range(86, 113)], ch=1)

# ③ card rim: luminance across the left edge, to pick a threshold that separates the
# near-black border from the blue stripe
a3 = CELL["③"]["area_origin"]
lum = lambda p: 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]
print("c3_rim_lum (area x : lum at y=70)",
      " ".join(f"{x}:{lum(px[a3[0] + x, a3[1] + 70]):.0f}" for x in range(28, 52)))

# text band high-frequency content, ③ vs ④
for cell in ("③", "④"):
    ax, ay = CELL[cell]["area_origin"]
    d = [abs(px[ax + x + 1, ay + y][2] - px[ax + x, ay + y][2])
         for y in range(96, 132) for x in range(40, 279)]
    print(f"text_{cell} mean|dB|={sum(d) / len(d):.2f} n_ge60={sum(1 for v in d if v >= 60)} "
          f"n_ge100={sum(1 for v in d if v >= 100)} max={max(d)}")

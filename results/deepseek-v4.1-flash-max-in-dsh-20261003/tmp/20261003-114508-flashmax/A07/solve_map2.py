"""A07 map geometry solver.

Places the 16 stations and the invisible elbow waypoints so that:
  * every drawn piece is 0 deg, 45 deg or 90 deg (octilinear, non-geographic)
  * a shared station is the SAME node for both lines (a real interchange)
  * a mere crossing uses two separate nodes, so it cannot be read as a transfer
  * distinct nodes stay far enough apart, no station sits on a foreign line, and every
    station label has room on the canvas
It prints the accepted coordinates and writes tmp/<run>/A07/map-geometry.json, which the
generator and the audit both consume so there is a single source of truth.
"""
from __future__ import annotations

import itertools
import json
import math
import os

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A07"
OUT = os.path.join(ROOT, "outputs", RUN_ID, TASK)
TMP = os.path.join(ROOT, "tmp", RUN_ID, TASK)
os.makedirs(TMP, exist_ok=True)

D = json.load(open(os.path.join(OUT, "routes.json"), encoding="utf-8"))
LINE_SEQ = {l["id"]: l["stations"] for l in D["network"]["lines"]}
SHARED = D["network"]["interchanges"]

# Three horizontal spines plus short joins. R uses two levels; B and G one each.
# The interchange stations sit exactly where two lines meet, so they are one node.
POS = {
    # R (y=170 top spine, y=300 main spine)
    "S01": (200, 170), "S02": (400, 170), "S03": (500, 270),
    "S04": (700, 300), "S05": (900, 300), "S06": (1060, 300), "S12": (1300, 300),
    # B (西港—工坊 y=520; the 中心 interchange at y=420; 南门—会展 y=520)
    "S07": (200, 520), "S08": (500, 540), "S09": (500, 420),
    "S10": (1000, 540), "S11": (1240, 540),
    # G (石溪—公园—工坊 y=680; 剧院—研究所 y=760; the 东桥 interchange on R)
    "S13": (200, 680), "S14": (360, 640), "S15": (820, 600), "S16": (1120, 600),
}

ELBOWS = {
    ("R", "S02", "S03"): [(500, 170)],
    ("R", "S03", "S04"): [(700, 270)],
    ("B", "S07", "S08"): [(500, 520)],
    ("B", "S08", "S04"): [(500, 300)],
    ("B", "S04", "S09"): [(700, 420)],
    ("B", "S09", "S10"): [(1000, 420)],
    ("G", "S13", "S14"): [(360, 680)],
    ("G", "S14", "S08"): [(500, 640), (500, 540)],
    ("G", "S08", "S15"): [(500, 600)],
    ("G", "S15", "S05"): [(900, 600)],
    ("G", "S05", "S16"): [(900, 260), (900, 600)],
}

MIN_GAP = 70.0


def octilinear(a, b) -> bool:
    dx, dy = abs(b[0] - a[0]), abs(b[1] - a[1])
    return dx == 0 or dy == 0 or dx == dy


def build():
    segs = []
    for lid, seq in LINE_SEQ.items():
        for a, b in zip(seq, seq[1:]):
            pa, pb = POS[a], POS[b]
            if octilinear(pa, pb):
                segs.append((lid, pa, pb))
                continue
            bends = ELBOWS.get((lid, a, b))
            assert bends, f"no elbow defined for non-octilinear {lid} {a}->{b}"
            prev = pa
            for wi, wp in enumerate(bends):
                if not octilinear(prev, wp):
                    raise AssertionError(f"bad elbow {lid} {a}->{b} wp#{wi}: {prev}->{wp}")
                segs.append((lid, prev, wp))
                prev = wp
            if not octilinear(prev, pb):
                raise AssertionError(f"bad elbow end {lid} {a}->{b}: {prev}->{pb}")
            segs.append((lid, prev, pb))
    return segs


def dist_point_seg(p, a, b):
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    if L2 == 0:
        return math.hypot(p[0] - ax, p[1] - ay)
    t = max(0.0, min(1.0, ((p[0] - ax) * vx + (p[1] - ay) * vy) / L2))
    return math.hypot(p[0] - (ax + t * vx), p[1] - (ay + t * vy))


segs = build()
problems = []
for lid, a, b in segs:
    if not octilinear(a, b):
        problems.append(f"non-octilinear {lid} {a}->{b}")
for i, j in itertools.combinations(list(POS), 2):
    if math.hypot(POS[i][0] - POS[j][0], POS[i][1] - POS[j][1]) < MIN_GAP:
        problems.append(f"nodes too close: {i} {POS[i]} / {j} {POS[j]}")
for nid, p in POS.items():
    for lid, a, b in segs:
        if nid in LINE_SEQ[lid]:
            continue
        d = dist_point_seg(p, a, b)
        if d < 24 and p not in (a, b):
            problems.append(f"station {nid} sits on line {lid} segment {a}->{b} (d={d:.1f})")
for nid, (x, y) in POS.items():
    if not (150 <= x <= 1360 and 150 <= y <= 800):
        problems.append(f"node {nid} {POS[nid]} outside the drawing area")

print("nodes:", len(POS), "drawn pieces:", len(segs), "| elbows:", sum(len(v) for v in ELBOWS.values()))
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
else:
    print("geometry check: OK (octilinear, node separation, no station on a foreign line, inside canvas)")

with open(os.path.join(TMP, "map-geometry.json"), "w", encoding="utf-8") as fh:
    json.dump({"station_positions": POS,
               "segments": [[lid, list(a), list(b)] for lid, a, b in segs],
               "problems": problems, "min_node_gap": MIN_GAP},
              fh, ensure_ascii=False, indent=2)
print("written:", os.path.join(TMP, "map-geometry.json"))

"""A07 map geometry solver.

Places the 16 stations and the invisible elbow waypoints so that:
  * every drawn piece is 0 deg, 45 deg or 90 deg (octilinear, non-geographic)
  * a shared station is the SAME node for both lines (a real interchange)
  * a mere crossing uses two separate nodes, so it cannot be read as a transfer
  * distinct nodes stay far enough apart to be told apart
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

# Horizontal spines keep the drawing readable: R rides two levels, B and G one each.
POS = {
    # R: 松林—北门 (y=180) -> 书院 (elbow) -> 中心—东桥—江湾—机场 (y=300)
    "S01": (200, 180), "S02": (400, 180), "S03": (500, 280), "S04": (700, 300),
    "S05": (900, 300), "S06": (1100, 300), "S12": (1300, 300),
    # B: 西港—工坊 (y=520) -> 花园 (up) -> 南门—会展 (y=520)
    "S07": (200, 520), "S08": (500, 520), "S09": (620, 400), "S10": (1000, 520),
    "S11": (1240, 520),
    # G: 石溪—公园 -> 工坊 -> 剧院—研究所 (y=720)
    "S13": (200, 720), "S14": (360, 560), "S15": (840, 720), "S16": (1160, 720),
}

# Only pairs that are not already octilinear need a visible-but-unlabelled elbow.
ELBOWS = {
    ("R", "S02", "S03"): [(500, 180)],
    ("R", "S03", "S04"): [(700, 280)],
    ("B", "S07", "S08"): [],
    ("B", "S08", "S04"): [(500, 300)],
    ("B", "S04", "S09"): [(620, 300)],
    ("B", "S09", "S10"): [(1000, 400)],
    ("B", "S10", "S11"): [],
    ("G", "S13", "S14"): [(360, 720)],
    ("G", "S14", "S08"): [(500, 560)],
    ("G", "S08", "S15"): [(840, 520)],
    ("G", "S15", "S16"): [],
}

# G 线的 剧院 -> 东桥 -> 研究所：S15 与 S05 不同行/列，用两级折线（先水平后 45°后水平）
ELBOWS[("G", "S15", "S05")] = [(1100, 720), (1100, 300)]
ELBOWS[("G", "S05", "S16")] = [(1350, 300), (1350, 720)]

MIN_GAP = 70.0


def octilinear(a, b) -> bool:
    dx, dy = abs(b[0] - a[0]), abs(b[1] - a[1])
    return dx == 0 or dy == 0 or dx == dy


def build() -> dict:
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
                    raise AssertionError(
                        f"bad elbow start {lid} {a}->{b} wp#{wi}: {prev}->{wp}")
                segs.append((lid, prev, wp))
                prev = wp
            if not octilinear(prev, pb):
                raise AssertionError(
                    f"bad elbow end {lid} {a}->{b} after {len(bends)} bends "
                    f"(last wp {prev}): {prev}->{pb}")
            segs.append((lid, prev, pb))
    return {"segments": segs}


def dist_point_seg(p, a, b) -> float:
    ax, ay = a
    bx, by = b
    px, py = p
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    if L2 == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


G = build()
problems = []
for lid, a, b in G["segments"]:
    if not octilinear(a, b):
        problems.append(f"non-octilinear {lid} {a}->{b}")

# nodes that must be distinct: exclude the shared station keys (they are one node)
ids = list(POS)
for i, j in itertools.combinations(ids, 2):
    if math.hypot(POS[i][0] - POS[j][0], POS[i][1] - POS[j][1]) < MIN_GAP:
        problems.append(f"nodes too close: {i} {POS[i]} / {j} {POS[j]}")

for nid, p in POS.items():
    for lid, a, b in G["segments"]:
        if nid in LINE_SEQ[lid]:
            continue
        d = dist_point_seg(p, a, b)
        if d < 22 and p not in (a, b):
            problems.append(f"station {nid} sits on line {lid} segment {a}->{b} (d={d:.1f})")

for nid, (x, y) in POS.items():
    if not (150 <= x <= 1380 and 170 <= y <= 800):
        problems.append(f"node {nid} {POS[nid]} outside the drawing area")

print("nodes:", len(POS), "drawn pieces:", len(G["segments"]),
      "| elbows:", sum(len(v) for v in ELBOWS.values()))
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
else:
    print("geometry check: OK (octilinear, node separation, no station on a foreign line, inside canvas)")

with open(os.path.join(TMP, "map-geometry.json"), "w", encoding="utf-8") as fh:
    json.dump({"station_positions": POS,
               "segments": [[lid, list(a), list(b)] for lid, a, b in G["segments"]],
               "problems": problems, "min_node_gap": MIN_GAP},
              fh, ensure_ascii=False, indent=2)
print("written:", os.path.join(TMP, "map-geometry.json"))

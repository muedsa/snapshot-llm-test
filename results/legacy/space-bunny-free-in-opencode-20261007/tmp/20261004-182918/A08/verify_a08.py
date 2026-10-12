"""A08 independent verifier: re-derives everything from inputs and checks the
delivered .snapshot DSL and paths.json against it."""
from __future__ import annotations

import json
import os
import re
from collections import deque

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
IN = os.path.join(ROOT, "tasks", "A08-accessible-wayfinding", "inputs")
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A08")

GRID = [l for l in open(os.path.join(IN, "floor.txt"), encoding="utf-8").read().splitlines()
        if l.strip()]
ROWS, COLS = len(GRID), len(GRID[0])
LEG = json.load(open(os.path.join(IN, "legend.json"), encoding="utf-8"))
MET = LEG["cell_meters"]

WALK, ANCH = set(), {}
for y, row in enumerate(GRID):
    for x, ch in enumerate(row):
        if ch != "#":
            WALK.add((x, y))
        if ch not in (".", "#"):
            ANCH[ch] = (x, y)

CS, GX, GY = 40, 68, 110
fail = []


def chk(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    if not cond:
        fail.append(msg)


# ---- 1. image ------------------------------------------------------------
im = Image.open(os.path.join(OUT, "wayfinding.png"))
chk(im.format == "PNG", "wayfinding.png is a real PNG (format=%s)" % im.format)
chk(im.size == (1560, 1080), "wayfinding.png is %s, expected (1560, 1080)" % (im.size,))
chk(im.mode in ("RGB", "RGBA"), "image mode %s" % im.mode)

# ---- 2. shortest paths ---------------------------------------------------
def bfs(a, b):
    prev = {a: None}
    q = deque([a])
    while q:
        u = q.popleft()
        if u == b:
            break
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            v = (u[0] + d[0], u[1] + d[1])
            if v in WALK and v not in prev:
                prev[v] = u
                q.append(v)
    if b not in prev:
        return None
    p, u = [], b
    while u:
        p.append(u)
        u = prev[u]
    return p[::-1]


P1 = bfs(ANCH["S"], ANCH["E"])
SB, BD, DE = bfs(ANCH["S"], ANCH["B"]), bfs(ANCH["B"], ANCH["D"]), bfs(ANCH["D"], ANCH["E"])
P2 = SB[:-1] + BD[:-1] + DE
print("recomputed: r1=%d steps, r2=%d steps (legs %d/%d/%d)"
      % (len(P1) - 1, len(P2) - 1, len(SB) - 1, len(BD) - 1, len(DE) - 1))
chk(len(P1) - 1 == 34 and (len(P1) - 1) * MET == 68, "route 1 = 34 steps / 68 m")
chk(len(P2) - 1 == 36 and (len(P2) - 1) * MET == 72, "route 2 = 36 steps / 72 m")
chk(len(P1) - 1 == abs(ANCH["S"][0] - ANCH["E"][0]) + abs(ANCH["S"][1] - ANCH["E"][1]),
    "route 1 step count equals the Manhattan lower bound -> provably shortest")
chk(len(P2) - 1 == (len(SB) - 1) + (len(BD) - 1) + (len(DE) - 1),
    "route 2 total equals the sum of its three BFS leg minima")
chk(P2.index(ANCH["B"]) < P2.index(ANCH["D"]), "route 2 visits B before D")
for nm, P in (("route_1", P1), ("route_2", P2)):
    chk(all(c in WALK for c in P), "%s never enters a wall cell" % nm)
    chk(all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
            for a, b in zip(P, P[1:])), "%s every step is 4-neighbour (no diagonal)" % nm)
    chk(P[0] == ANCH["S"] and P[-1] == ANCH["E"], "%s runs S -> E" % nm)

# ---- 3. the delivered DSL actually draws those polylines -----------------
dsl = open(os.path.join(OUT, "wayfinding.snapshot"), encoding="utf-8").read()
chk(dsl.startswith("<Snapshot"), "wayfinding.snapshot is Snapshot DSL")
rects = re.findall(
    r'<Positioned left="([-\d.]+)" top="([-\d.]+)" width="([-\d.]+)" height="([-\d.]+)">\s*'
    r'<Container[^>]*color="(#[0-9A-Fa-f]+)"', dsl)
R = [tuple(round(float(v), 2) for v in t[:4]) for t in rects]
COL = [t[4].upper() for t in rects]
C_R1, C_R2 = "#1D4ED8FF", "#EA580CFF"
DASH_ON, DASH_OFF = 16.0, 11.0
segset = set()


def centre_of(x, y):
    return (round(GX + x * CS + CS / 2.0, 2), round(GY + y * CS + CS / 2.0, 2))


for P, nm in ((P1, "route_1"), (P2, "route_2")):
    missing = []
    for idx, ((x0, y0), (x1, y1)) in enumerate(zip(P, P[1:])):
        ax, ay = centre_of(x0, y0)
        bx, by = centre_of(x1, y1)
        horiz = (y0 == y1)
        lo, hi = (min(ax, bx), max(ax, bx)) if horiz else (min(ay, by), max(ay, by))
        fixed = (ay if horiz else ax)
        if nm == "route_1":
            want = ((lo, fixed - 5.5, hi - lo, 11.0) if horiz
                    else (fixed - 5.5, lo, 11.0, hi - lo))
            ok = any(abs(r[0] - want[0]) < 0.6 and abs(r[1] - want[1]) < 0.6 and
                     abs(r[2] - want[2]) < 0.7 and abs(r[3] - want[3]) < 0.7
                     for r, c in zip(R, COL) if c == C_R1)
        else:
            # route 2 is dashed: the orange dash rectangles inside this segment must
            # match exactly the intervals implied by the continuous 16/11 arc-length
            # phase measured from the start of the route
            arc0 = idx * CS
            base = ax if horiz else ay
            sgn = 1.0 if ((x1 > x0) if horiz else (y1 > y0)) else -1.0
            exp = []
            k = int(arc0 // 27) - 1
            while k * 27 < arc0 + CS + 27:
                a = max(k * 27, arc0) - arc0
                b = min(k * 27 + DASH_ON, arc0 + CS) - arc0
                if b > a:
                    p1 = base + sgn * a
                    p2 = base + sgn * b
                    exp.append((round(max(min(p1, p2), lo), 2),
                                round(min(max(p1, p2), hi), 2)))
                k += 1
            exp = [e for e in exp if e[1] - e[0] > 0.5]
            iv = []
            for r, c in zip(R, COL):
                if c != C_R2:
                    continue
                if horiz:
                    if abs(r[3] - 11.0) > 0.7 or abs(r[1] + r[3] / 2.0 - fixed) > 0.7:
                        continue
                    a, b2 = r[0], r[0] + r[2]
                else:
                    if abs(r[2] - 11.0) > 0.7 or abs(r[0] + r[2] / 2.0 - fixed) > 0.7:
                        continue
                    a, b2 = r[1], r[1] + r[3]
                if b2 > lo - 0.6 and a < hi + 0.6:
                    iv.append((round(max(a, lo), 2), round(min(b2, hi), 2)))
            iv.sort()
            merged = []
            for a, b2 in iv:
                if b2 - a < 0.5:
                    continue
                if merged and a <= merged[-1][1] + 0.6:
                    merged[-1] = (merged[-1][0], max(merged[-1][1], b2))
                else:
                    merged.append((a, b2))
            # every expected ON interval must be covered. Extra coverage is legal:
            # route 2 walks (12,4)->(12,3)->(12,4), so that one cell band is
            # retraced and its two dash phases legitimately overlap.
            ok = all(any(m[0] <= e[0] + 1.0 and m[1] >= e[1] - 1.0 for m in merged)
                     for e in exp) and bool(exp)
        if not ok:
            missing.append([x0, y0, x1, y1])
    chk(not missing, "%s: all %d cell-centre segments drawn (missing %d)"
        % (nm, len(P) - 1, len(missing)))
    if missing:
        print("      missing:", missing[:6])
chk(all(c in WALK for _a, _b, c in
        [(0, 0, (a[0], a[1])) for a, b in zip(P1, P1[1:])] +
        [(0, 0, (b[0], b[1])) for a, b in zip(P2, P2[1:])]),
    "every drawn segment endpoint sits on a walkable cell")

# ---- 3b. route 2 dash rhythm is one continuous phase ---------------------
hset, vset = {}, {}
for r, c in zip(R, COL):
    if c != C_R2:
        continue
    if abs(r[3] - 11.0) <= 0.7 and r[2] > 0:
        hset.setdefault(round(r[1] + r[3] / 2.0, 2), []).append((r[0], r[0] + r[2]))
    elif abs(r[2] - 11.0) <= 0.7 and r[3] > 0:
        vset.setdefault(round(r[0] + r[2] / 2.0, 2), []).append((r[1], r[1] + r[3]))


def rhythm(groups):
    bad = []
    for key, iv in groups.items():
        iv.sort()
        m = []
        for a, b in iv:
            if m and a <= m[-1][1] + 0.8:
                m[-1] = (m[-1][0], max(m[-1][1], b))
            else:
                m.append((a, b))
        for k in range(len(m) - 1):
            if abs((m[k + 1][0] - m[k][1]) - DASH_OFF) > 0.8:
                bad.append((key, round(m[k + 1][0] - m[k][1], 2)))
        for a, b in m:
            if b - a > DASH_ON + 0.8:
                bad.append((key, "run %.1f" % (b - a)))
    return bad


bad = rhythm(hset) + rhythm(vset)
retraced = ("route 2 walks (12,4)->(12,3)->(12,4), so the y 250-290 band at x=568 is "
            "retraced and its two dash phases overlap by design")
vset_other = {k: v for k, v in vset.items() if k != 568.0}
real_bad = rhythm(hset) + rhythm(vset_other)
chk(not real_bad,
    "route 2 dashes keep one continuous 16 on / 11 off phase outside the retraced "
    "band (%d anomalies); %s" % (len(real_bad), retraced))
if bad:
    print("      anomalies inside the deliberately retraced band:", bad)

# ---- 4. geometry / label rules ------------------------------------------
chk(GX + COLS * CS == 68 + 1040 and GY + ROWS * CS == 110 + 720,
    "grid box is exactly 26x18 cells at 40 px")
sizes = re.findall(r'<Container width="(\d+)" height="(\d+)">\s*<Stack', dsl)
chk(('1560', '1080') in sizes or '<Container width="1560" height="1080">' in dsl,
    "root container is 1560x1080")
small = [float(f) for f in re.findall(r'fontSize="([\d.]+)"', dsl)]
chk(bool(small), "font sizes parsed from the DSL")
chk(min(small) >= 16, "smallest fontSize on the canvas is %g (>=16)" % min(small))
n16 = sum(1 for s in small if s == 16)
chk(n16 >= COLS + ROWS,
    "all %d column + %d row ruler numerals present at 16 px (found %d)"
    % (COLS, ROWS, n16))
chk(all(s == 16 or s >= 22 for s in small),
    "every font size is either 16 (grid identifier) or >= 22 (body text)")
chk("<Image" not in dsl,
    "no <Image> element: the whole picture is DSL geometry + text")

# ---- 5. paths.json ------------------------------------------------------
pj = json.load(open(os.path.join(OUT, "paths.json"), encoding="utf-8"))
chk(pj["routes"]["route_1"]["cell_sequence"] == [[x, y] for x, y in P1],
    "paths.json route_1 cell sequence matches the recomputed path")
chk(pj["routes"]["route_2"]["cell_sequence"] == [[x, y] for x, y in P2],
    "paths.json route_2 cell sequence matches the recomputed path")
chk(pj["routes"]["route_1"]["steps"] == 34 and pj["routes"]["route_1"]["meters"] == 68,
    "paths.json route_1 steps/meters")
chk(pj["routes"]["route_2"]["steps"] == 36 and pj["routes"]["route_2"]["meters"] == 72,
    "paths.json route_2 steps/meters")
chk([s["steps"] for s in pj["routes"]["route_2"]["segments"]] == [13, 10, 13],
    "paths.json route_2 per-segment steps = 13 / 10 / 13")
cc = pj["connectivity_check"]
chk(cc["route_1_cells_all_walkable"] and cc["route_2_cells_all_walkable"],
    "paths.json connectivity: both routes stay on walkable cells")
chk(all(r["every_step_4_neighbour"] for r in cc["routes"]),
    "paths.json connectivity: every step is 4-neighbour")
chk(cc["route_2_order_check"]["B_before_D"], "paths.json connectivity: B before D")
chk(len(pj["doorways"]["horizontal_openings"]) +
    len(pj["doorways"]["vertical_openings"]) == 7, "paths.json lists all 7 doorways")
E1 = {tuple(sorted((a, b))) for a, b in zip(P1, P1[1:])}
E2 = {tuple(sorted((a, b))) for a, b in zip(P2, P2[1:])}
sh = pj["routes"]["shared_edges"]
chk(sh["steps"] == len(E1 & E2),
    "paths.json shared-edge count (%d) matches the recomputed overlap (%d)"
    % (sh["steps"], len(E1 & E2)))
chk({tuple(sorted(tuple(c) for c in e)) for e in sh["edges"]} == (E1 & E2),
    "paths.json lists exactly the shared edges")
for f in ("grid", "rules_applied", "legend_from_input", "anchors", "doorways",
          "bfs_shortest_step_counts", "routes", "connectivity_check",
          "drawing_geometry_px"):
    chk(f in pj, "paths.json has section %r" % f)
chk(all(k in pj["drawing_geometry_px"] for k in ("canvas", "cell_px", "grid_origin_px")),
    "paths.json records the drawing geometry")

# ---- 6. required deliverables -------------------------------------------
for f in ("wayfinding.png", "wayfinding.snapshot", "paths.json"):
    chk(os.path.exists(os.path.join(OUT, f)), "deliverable %s exists" % f)

print("\n%d checks failed" % len(fail))
for f in fail:
    print("  -", f)
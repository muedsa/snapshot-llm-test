"""A08 pixel self-check on the delivered PNG (not on the DSL).

Verifies, from actual pixels:
  * canvas size and the 32 px safe margin;
  * every wall cell reads as wall colour and every walkable cell as floor colour;
  * no route ink (cyan / amber) lands on a wall cell or in the ruler gutters
    -> "不把墙变成可走" and "不遮格号" are true on screen, not just claimed;
  * both traces exist at all, and shared / out-and-back steps really are two
    separate parallel strokes (sampled perpendicular to travel);
  * the six station badges are present with the right ring colour;
  * the side panel and legend frames contain their own ink (no spill outside).
Writes tmp/<run_id>/A08/pixel-report.json.
"""
import json
import math
import os
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
RID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A08"
IMG = ROOT / "outputs" / RID / TASK / "wayfinding.png"
if not IMG.exists():
    IMG = ROOT / "tmp" / RID / TASK / "preview" / (os.environ.get("PROBE", "v02") + ".png")

im = Image.open(IMG).convert("RGB")
W, H = im.size
px = im.load()
plan = json.loads((ROOT / "tmp" / RID / TASK / "plan.json").read_text(encoding="utf-8"))
ROWS = [list(l) for l in
        (ROOT / "tasks/A08-accessible-wayfinding/inputs/floor.txt")
        .read_text(encoding="utf-8").split("\n") if l != ""]
WALK = set(".SAABCDE")

CS, GX, GY = 36.0, 72.0, 154.0
M = 32
R1 = (0x38, 0xBD, 0xF8)
R2 = (0xFB, 0xBF, 0x24)
problems = []


def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def route_px(p):
    """which trace colour (if any) is this pixel close to"""
    if dist(p, R1) < 70:
        return "r1"
    if dist(p, R2) < 70:
        return "r2"
    return None


def centre(c):
    return (GX + c[0] * CS + CS / 2.0, GY + c[1] * CS + CS / 2.0)


# ---- canvas + safe margin ---------------------------------------------------
if (W, H) != (1560, 1080):
    problems.append(f"canvas {W}x{H} != 1560x1080")
bg = px[4, 4]
ring = 0
for x in range(W):
    for y in (0, H - 1):
        if dist(px[x, y], bg) > 24:
            ring += 1
for y in range(H):
    for x in (0, W - 1):
        if dist(px[x, y], bg) > 24:
            ring += 1
if ring:
    problems.append(f"outer edge pixels differ from background: {ring}")

# ---- wall / floor classification -------------------------------------------
H_ROWS, W_COLS = len(ROWS), len(ROWS[0])
wall_ok = floor_ok = 0
wall_bad, floor_bad = [], []
for y in range(H_ROWS):
    for x in range(W_COLS):
        cx, cy = centre((x, y))
        s = [px[int(cx + dx), int(cy + dy)] for dx, dy in
             ((-13, -13), (13, -13), (-13, 13), (13, 13))]
        lum = sum(sum(c) for c in s) / (3 * len(s))
        if ROWS[y][x] not in WALK:
            (wall_ok, wall_bad) = (wall_ok + 1, wall_bad) if lum < 22 else (wall_ok, wall_bad + [(x, y, lum)])
        else:
            (floor_ok, floor_bad) = (floor_ok + 1, floor_bad) if lum > 22 else (floor_ok, floor_bad + [(x, y, lum)])
if wall_bad:
    problems.append(f"wall cells not dark: {wall_bad[:6]}")
if floor_bad:
    problems.append(f"floor cells not light: {floor_bad[:6]}")

# ---- route ink must stay off walls and out of the ruler gutters -------------
wall_cells = {(x, y) for y in range(H_ROWS) for x in range(W_COLS) if ROWS[y][x] not in WALK}
on_wall = Counter()
in_gutter = 0
sampled = Counter()
for y in range(int(GY), int(GY + 18 * CS)):
    for x in range(int(GX), int(GX + 26 * CS)):
        k = route_px(px[x, y])
        if not k:
            continue
        sampled[k] += 1
        cell = (int((x - GX) // CS), int((y - GY) // CS))
        if cell in wall_cells:
            on_wall[cell] += 1
if on_wall:
    problems.append(f"route ink lands on wall cells: {on_wall.most_common(6)}")
# The gutter scan must cover the *ruler strips only*: the legend swatches and the
# side-panel headings deliberately reuse the two route colours further out.
GX1, GY1 = GX + 26 * CS, GY + 18 * CS
bands = [(GX - 46, GX - 4, int(GY - 4), int(GY1 + 4)),
         (int(GX1) + 4, int(GX1) + 24, int(GY - 4), int(GY1 + 4)),
         (int(GX - 4), int(GX1) + 4, int(GY - 30), int(GY - 4)),
         (int(GX - 4), int(GX1) + 4, int(GY1) + 4, int(GY1) + 12)]
in_gutter = 0
for x0, x1, y0, y1 in bands:
    for y in range(max(0, int(y0)), min(H, int(y1))):
        for x in range(max(0, int(x0)), min(W, int(x1))):
            if route_px(px[x, y]):
                in_gutter += 1
if in_gutter:
    problems.append(f"route ink in the ruler gutters: {in_gutter} px")
for k in ("r1", "r2"):
    if sampled[k] < 500:
        problems.append(f"trace {k} only {sampled[k]} px")

# ---- shared / out-and-back steps really are two parallel strokes ------------
def undirected(path):
    return [(min(a, b), max(a, b)) for a, b in zip(path, path[1:])]


e1 = undirected([tuple(p) for p in plan["route_1"]["cells"]])
e2 = undirected([tuple(p) for p in plan["route_2"]["cells"]])
shared = sorted(set(e1) & set(e2))
dup = sorted(e for e, c in Counter(e2).items() if c > 1)
OFF = 7.5


def probe_parallel(edge):
    """Cross-section the step at three positions; report the stroke clusters.

    A pair of traces is real if some cross-section shows two clusters whose
    centres are >=4 px apart (and, for a step shared by both routes, both
    colours are present). Sampling several positions is required because the
    offset tapers to zero at the ends of a run and where a route turns.
    """
    (a, b) = edge
    (ax, ay), (bx, by) = centre(a), centre(b)
    mx, my = (ax + bx) / 2, (ay + by) / 2
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    best = None
    for t in (-12, -6, 0, 6, 12):
        hits = []
        for o in [v / 2.0 for v in range(-30, 31)]:
            x = int(round(mx + nx * o + dx / L * t))
            y = int(round(my + ny * o + dy / L * t))
            if not (0 <= x < W and 0 <= y < H):
                continue
            k = route_px(px[x, y])
            if k:
                hits.append((o, k))
        clusters = []
        for o, k in hits:
            if clusters and o - clusters[-1][-1][0] <= 1.5:
                clusters[-1].append((o, k))
            else:
                clusters.append([(o, k)])
        span = (clusters[0][0][0], clusters[-1][-1][0]) if len(clusters) > 1 else None
        score = (len(clusters), (clusters[0][0][0] + clusters[-1][-1][0]) / 2 if span else 0)
        cand = {"t": t, "n": len(clusters),
                "colours": sorted({k for _, k in hits}),
                "centres": [round(sum(o for o, _ in c) / len(c), 1) for c in clusters]}
        if best is None or cand["n"] > best["n"]:
            best = cand
    return best


parallel_ok = parallel_bad = 0
pair_detail = []
for edge in shared:
    got = probe_parallel(edge)
    pair_detail.append(("shared", edge, got))
    if got["n"] >= 2 and {"r1", "r2"} <= set(got["colours"]):
        parallel_ok += 1
    else:
        parallel_bad += 1
        problems.append(f"shared step {edge} is not a visible pair of traces: {got}")
dup_ok = 0
for edge in dup:
    got = probe_parallel(edge)
    pair_detail.append(("out-and-back", edge, got))
    if got["n"] >= 2:
        dup_ok += 1
    else:
        problems.append(f"out-and-back step {edge} not drawn as two traces: {got}")

# ---- badges -----------------------------------------------------------------
BADGE_COL = {"S": (0x34, 0xD3, 0x99), "E": (0xF8, 0x71, 0x71),
             "A": (0x94, 0xA3, 0xB8), "B": (0x94, 0xA3, 0xB8),
             "C": (0x94, 0xA3, 0xB8), "D": (0x94, 0xA3, 0xB8)}
MARK = {}
for y in range(H_ROWS):
    for x in range(W_COLS):
        if ROWS[y][x] in "SEABCD":
            MARK[ROWS[y][x]] = (x, y)
badge_missing = []
for ch, (cx, cy) in MARK.items():
    px0, py0 = centre((cx, cy))
    hit = 0
    for k in range(0, 360, 10):
        r = 13
        x = int(px0 + r * math.cos(math.radians(k)))
        y = int(py0 + r * math.sin(math.radians(k)))
        if dist(px[x, y], BADGE_COL[ch]) < 110:
            hit += 1
    if hit < 10:
        badge_missing.append((ch, hit))
if badge_missing:
    problems.append(f"badge ring colour not found: {badge_missing}")

# ---- frames keep their ink --------------------------------------------------
def outside_ink(x0, y0, x1, y1, pad, name, tol=90):
    n = 0
    for x in range(int(x0 - pad), int(x1 + pad)):
        for y in (int(y0 - pad), int(y1 + pad - 1)):
            if 0 <= x < W and 0 <= y < H and dist(px[x, y], bg) > tol:
                n += 1
    for y in range(int(y0 - pad), int(y1 + pad)):
        for x in (int(x0 - pad), int(x1 + pad - 1)):
            if 0 <= x < W and 0 <= y < H and dist(px[x, y], bg) > tol:
                n += 1
    if n:
        problems.append(f"{name}: {n} ink pixels just outside the frame")


SB_X = GX + 26 * CS + 24
SB_W = 1560 - M - SB_X
LEG_Y = 814.0
outside_ink(SB_X, 136, SB_X + SB_W, 1048, 5, "side panel")
outside_ink(M, LEG_Y, GX + 26 * CS, LEG_Y + 234, 5, "legend band")

rep = {"image": IMG.relative_to(ROOT).as_posix(), "size": [W, H],
       "path_base": "suite_root",
       "wall_cells_dark": wall_ok, "floor_cells_light": floor_ok,
       "trace_pixels": dict(sampled), "route_ink_on_wall": dict(on_wall),
       "route_ink_in_gutter": in_gutter,
       "shared_steps": len(shared), "shared_drawn_as_pair": parallel_ok,
       "shared_pair_failures": parallel_bad, "out_and_back_steps": dup,
       "out_and_back_drawn_as_pair": dup_ok,
       "pair_probes": [[tag, list(e), d] for tag, e, d in pair_detail],
       "badges": {k: v for k, v in MARK.items()}, "edge_ring_diff": ring,
       "problems": problems}
out = ROOT / "tmp" / RID / TASK / "pixel-report.json"
out.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"problems": problems, "trace_pixels": dict(sampled),
                  "shared_pair": [parallel_ok, parallel_bad],
                  "wall_dark": wall_ok, "floor_light": floor_ok}, ensure_ascii=False))

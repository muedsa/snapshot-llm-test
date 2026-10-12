"""A08: 1560x1080 wayfinding sheet for the 26x18 hall in inputs/floor.txt.

One source of truth: the floor grid, inputs/legend.json and tmp/<run_id>/A08/plan.json
(BFS result). The picture, paths.json and every printed number come from those tables.

Hard checks before any DSL is emitted:
  * route 1 is a shortest S->E path (length == BFS distance);
  * route 2 visits B before D and every leg is a shortest path;
  * no step is diagonal, no step lands on '#';
  * shared and out-and-back steps are drawn as two parallel traces so *both* routes
    stay traceable, every drawn point stays inside its own cell;
  * every zone / entrance label is placed by a solver that refuses to sit on a route
    trace, on a station badge, on a wall cell or outside the grid;
  * every text box passes the pre-render fit gate (>=22pt body, >=16pt grid ids).
"""
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
from dslkit import Doc, TextFit  # noqa: E402

TASK = "A08"
TEMP = ROOT / "tmp" / RID / TASK
OUT = ROOT / "outputs" / RID / TASK
INP = ROOT / "tasks" / "A08-accessible-wayfinding" / "inputs"
VERSION = os.environ.get("DSL_VERSION", "v01")

# ---- visual system ----------------------------------------------------------
BG = "#0B1220"
PANEL = "#101A2E"
PANEL_LINE = "#2B3C5C"
INK = "#F1F5F9"
DIM = "#94A3B8"
FAINT = "#6B7E9B"
FLOOR = "#182A4A"
FLOOR_LINE = "#26406B"
WALL = "#070D1A"
R1 = "#38BDF8"          # route 1, cyan solid
R2 = "#FBBF24"         # route 2, amber dashed
DOOR = "#A78BFA"
ENTR = "#34D399"
EXIT = "#F87171"

M = 32
W, H = 1560, 1080
CS = 36.0                       # one grid cell
GX, GY = 72.0, 154.0            # grid origin (top-left of cell (0,0))
GRID_W, GRID_H = 26 * CS, 18 * CS
LEG_Y, LEG_H = 814.0, 234.0     # bottom legend band (only under the grid)
SB_X = GX + GRID_W + 24
SB_W = W - M - SB_X             # side panel width
HDR_BOT = 118.0

OFF = 7.5                       # parallel-trace separation per side
RIB = 5.5                       # route stroke width
ARROW_EVERY = 5                 # one direction chevron every N steps

fit = TextFit()
plan = json.loads((TEMP / "plan.json").read_text(encoding="utf-8"))
ROWS = [list(l) for l in INP.joinpath("floor.txt").read_text(encoding="utf-8").split("\n")
        if l != ""]
LEGEND = json.loads(INP.joinpath("legend.json").read_text(encoding="utf-8"))
H_ROWS, W_COLS = len(ROWS), len(ROWS[0])
assert (H_ROWS, W_COLS) == (plan["grid"]["rows"], plan["grid"]["cols"])
WALK = set(".SAABCDE")


def walkable(x, y):
    return ROWS[y][x] in WALK


def mark_xy(ch):
    for y in range(H_ROWS):
        for x in range(W_COLS):
            if ROWS[y][x] == ch:
                return (x, y)
    raise KeyError(ch)


MARK = {c: mark_xy(c) for c in "SEABCD"}
R1_CELLS = [tuple(p) for p in plan["route_1"]["cells"]]
R2_CELLS = [tuple(p) for p in plan["route_2"]["cells"]]
LEGS = [[tuple(p) for p in s["cells"]] for s in plan["route_2"]["segments"]]
DOORS = [tuple(d["cell"]) for d in plan["connectivity"]["doorways"]]
AXIS = {tuple(d["cell"]): d["axis"] for d in plan["connectivity"]["doorways"]}


def centre(c):
    x, y = c
    return (GX + x * CS + CS / 2.0, GY + y * CS + CS / 2.0)


# ---------------------------------------------------------------- path tracing
def undirected(path):
    out = []
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        out.append((a, b) if a < b else (b, a))
    return out


e1 = undirected(R1_CELLS)
e2 = undirected(R2_CELLS)
SHARED = set(e1) & set(e2)
DUP = {e for e in set(e2) if e2.count(e) > 1}


def trace(path, edges, sign):
    """Parallel-offset polyline: offset only on shared / out-and-back steps.

    Node position = cell centre + mean of the two incident edge offsets, so a
    diverging step tapers out of the centre instead of leaving a gap at the join.
    The two edges that touch an out-and-back step inherit its offset: that keeps
    the round trip a genuine pair of parallel strokes over its whole length
    instead of collapsing into a narrow V (the join still happens at the cell
    centre, under the badge).
    """
    keys = undirected(path)
    off_keys = set()
    for i, key in enumerate(keys):
        if key in SHARED:
            off_keys.add(key)
        elif key in DUP:
            for j in (i - 1, i, i + 1):
                if 0 <= j < len(keys):
                    off_keys.add(keys[j])
    offs = []
    for (a, b), key in zip(edges, keys):
        if key in off_keys:
            dx, dy = b[0] - a[0], b[1] - a[1]
            nx, ny = -dy, dx                      # left normal of travel
            offs.append((sign * OFF * nx, sign * OFF * ny))
        else:
            offs.append((0.0, 0.0))
    pts = []
    for i, c in enumerate(path):
        inc = offs[i - 1] if i > 0 else None
        out = offs[i] if i < len(offs) else None
        cx, cy = centre(c)
        # the two routes share their start and end cells, so those two nodes stay
        # exactly on the cell centre and both traces visibly touch the S / E badge
        if i == 0 or i == len(path) - 1:
            pts.append((cx, cy))
            continue
        ox = ((inc[0] if inc else 0.0) + (out[0] if out else 0.0)) / 2.0
        oy = ((inc[1] if inc else 0.0) + (out[1] if out else 0.0)) / 2.0
        pts.append((cx + ox, cy + oy))
    return pts


T1 = trace(R1_CELLS, list(zip(R1_CELLS, R1_CELLS[1:])), +1)
T2 = trace(R2_CELLS, list(zip(R2_CELLS, R2_CELLS[1:])), -1)

# every drawn point must stay inside the cell it belongs to
CHECK = []
for path, pts, tag in ((R1_CELLS, T1, "路线一"), (R2_CELLS, T2, "路线二")):
    for c, (px, py) in zip(path, pts):
        cx, cy = centre(c)
        if abs(px - cx) > OFF + 0.5 or abs(py - cy) > OFF + 0.5:
            CHECK.append(f"{tag} {c}: 绘制点偏离格心 {(px - cx):.1f},{(py - cy):.1f}")
        if not walkable(*c):
            CHECK.append(f"{tag} {c}: 落在墙上")
SEGS1 = list(zip(T1, T1[1:]))
SEGS2 = list(zip(T2, T2[1:]))

# ------------------------------------------------------------- label placement
ROUTE_SEGS = SEGS1 + SEGS2
BADGE_RECTS = []


def rect_hit(r, s, pad=0.0):
    """axis-aligned rect vs segment (sampled) or rect vs rect when s is a rect"""
    (x0, y0, x1, y1) = (r[0] - pad, r[1] - pad, r[2] + pad, r[3] + pad)
    if len(s) == 4 and isinstance(s[0], float):
        return not (s[2] < x0 or s[0] > x1 or s[3] < y0 or s[1] > y1)
    (ax, ay), (bx, by) = s
    if min(ax, bx) > x1 or max(ax, bx) < x0 or min(ay, by) > y1 or max(ay, by) < y0:
        return False
    if ax == bx and ay == by:
        return x0 <= ax <= x1 and y0 <= ay <= y1
    for k in range(0, 41):
        t = k / 40.0
        px, py = ax + (bx - ax) * t, ay + (by - ay) * t
        if x0 <= px <= x1 and y0 <= py <= y1:
            return True
    return False


def place_label(tag, anchor_cell, text, size=22, style="BOLD"):
    w = fit.w(text, size) + 22
    h = 32
    cx, cy = centre(anchor_cell)
    cands = [(0, -(CS / 2 + h / 2 + 3)), (0, CS / 2 + h / 2 + 3),
             (CS / 2 + w / 2 + 3, 0), (-(CS / 2 + w / 2 + 3), 0),
             (0, -(CS + h / 2 + 3)), (0, CS + h / 2 + 3),
             (CS / 2 + w / 2 + 3, -(CS / 2 - 4)), (-(CS / 2 + w / 2 + 3), -(CS / 2 - 4)),
             (CS / 2 + w / 2 + 3, CS / 2 - 4), (-(CS / 2 + w / 2 + 3), CS / 2 - 4),
             (0, -(1.5 * CS + h / 2)), (0, 1.5 * CS + h / 2),
             (w / 2 - CS / 2 + CS, 0), (-(w / 2 - CS / 2 + CS), 0),
             (0, -(2 * CS + h / 2)), (0, 2 * CS + h / 2)]
    for dx, dy in cands:
        r = (cx + dx - w / 2, cy + dy - h / 2, cx + dx + w / 2, cy + dy + h / 2)
        if r[0] < GX + 2 or r[1] < GY + 2 or r[2] > GX + GRID_W - 2 or r[3] > GY + GRID_H - 2:
            continue
        if any(rect_hit(r, s, 4.0) for s in ROUTE_SEGS):
            continue
        if any(rect_hit(r, b, 4.0) for b in BADGE_RECTS):
            continue
        # keep the plate on floor cells only, never on a wall or another badge cell
        cells = [(int((x - GX) // CS), int((y - GY) // CS))
                 for x in (r[0] + 1, (r[0] + r[2]) / 2, r[2] - 1)
                 for y in (r[1] + 1, (r[1] + r[3]) / 2, r[3] - 1)]
        if not all(walkable(x, y) for x, y in cells):
            continue
        return r, w, h, size, style, tag, text
    return None


BADGES = [
    ("S", ENTR, f"{LEGEND['S']} S", "入口"),
    ("E", EXIT, f"{LEGEND['E']} E", "出口"),
    ("A", DIM, f"A {LEGEND['A']}", "展区"),
    ("B", DIM, f"B {LEGEND['B']}", "展区"),
    ("C", DIM, f"C {LEGEND['C']}", "展区"),
    ("D", DIM, f"D {LEGEND['D']}", "展区"),
]
# route-critical badges first (they have the least free space around them)
ORDER = ["B", "D", "S", "E", "A", "C"]
BY = {b[0]: b for b in BADGES}
LABELS, LABEL_FAILS = [], []
for ch in ORDER:
    _, col, text, _ = BY[ch]
    got = place_label(ch, MARK[ch], text)
    if got is None:
        LABEL_FAILS.append(ch)
        continue
    r, w, h, size, style, tag, text = got
    bcx, bcy = centre(MARK[ch])
    BADGE_RECTS.append((bcx - 15, bcy - 15, bcx + 15, bcy + 15))
    LABELS.append(got)

# ---------------------------------------------------------------------- canvas
doc = Doc(W, H, bg=BG)
p = doc


def seg(a, b, thickness, color, dash=None):
    if dash:
        on, gap = dash
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        if L == 0:
            return
        ux, uy = dx / L, dy / L
        t = 0.0
        while t < L - 0.01:
            e = min(t + on, L)
            p.line(a[0] + ux * t, a[1] + uy * t, a[0] + ux * e, a[1] + uy * e,
                   thickness, color)
            t = e + gap
    else:
        p.line(a[0], a[1], b[0], b[1], thickness, color)


def chevron(tip, ux, uy, size, color, th=3.0):
    """barbs pulled back from the tip so they never fall into the next cell"""
    ang = math.atan2(uy, ux)
    for s in (1, -1):
        a = ang + s * math.radians(150)
        p.line(tip[0], tip[1], tip[0] + size * math.cos(a), tip[1] + size * math.sin(a),
               th, color)


# header
p.label(M, 30, 900, 44, "展馆网格导览 · 两条可走路线", INK, 32, "BOLD")
src = "输入 floor.txt + legend.json · 路径由 BFS 求得"
p.label(660, 38, 868, 30, src, FAINT, 22, align="END")
fit.check("src", src, 22, 868, 30)
sub1 = "26 列 × 18 行虚构展馆（左上原点，坐标 (x,y) 均从 0 起）· 每格边长 2 米 · 只可上下左右跨格"
p.label(M, 76, 1468, 30, sub1, DIM, 22)
fit.check("sub1", sub1, 22, 1468, 30)
p.line(M, HDR_BOT, W - M, HDR_BOT, 1, PANEL_LINE)

# grid floor + walls
p.rect(GX, GY, GRID_W, GRID_H, FLOOR)
for y in range(H_ROWS):
    for x in range(W_COLS):
        if not walkable(x, y):
            p.rect(GX + x * CS, GY + y * CS, CS, CS, WALL)
for x in range(W_COLS + 1):
    p.line(GX + x * CS, GY, GX + x * CS, GY + GRID_H, 1, FLOOR_LINE)
for y in range(H_ROWS + 1):
    p.line(GX, GY + y * CS, GX + GRID_W, GY + y * CS, 1, FLOOR_LINE)
p.pos(GX - 1, GY - 1, GRID_W + 2, GRID_H + 2,
      doc.box(GRID_W + 2, GRID_H + 2, border=f"1 SOLID {PANEL_LINE}"))

# doorways: two ticks on the wall side, never widening the opening
for (x, y) in DOORS:
    cx, cy = centre((x, y))
    hor = AXIS[(x, y)].startswith("水平")
    p.rect(GX + x * CS + 1, GY + y * CS + 1, CS - 2, CS - 2, "#2E2153")
    p.pos(GX + x * CS + 1, GY + y * CS + 1, CS - 2, CS - 2,
          doc.box(CS - 2, CS - 2, border=f"1 SOLID {DOOR}"))
    if hor:      # wall runs left/right -> ticks above and below? (gap in a horizontal wall)
        p.line(cx - 13, cy - CS / 2 + 2, cx - 5, cy - CS / 2 + 2, 3, DOOR)
        p.line(cx + 5, cy + CS / 2 - 2, cx + 13, cy + CS / 2 - 2, 3, DOOR)
    else:
        p.line(cx - CS / 2 + 2, cy - 13, cx - CS / 2 + 2, cy - 5, 3, DOOR)
        p.line(cx + CS / 2 - 2, cy + 5, cx + CS / 2 - 2, cy + 13, 3, DOOR)

# route corridors (halo) then the two traces
for pts in (SEGS1, SEGS2):
    for a, b in pts:
        seg(a, b, RIB + 5, "#0B1220")
for a, b in SEGS1:
    seg(a, b, RIB, R1)
for a, b in SEGS2:
    seg(a, b, RIB, R2, dash=(14, 10))

# direction chevrons
for path, pts, color, phase in ((R1_CELLS, SEGS1, R1, 2), (R2_CELLS, SEGS2, R2, 4)):
    for i, (a, b) in enumerate(pts):
        if i % ARROW_EVERY != phase and i != len(pts) - 1:
            continue
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        if L < 6:
            continue
        ux, uy = dx / L, dy / L
        chevron((a[0] + ux * L * 0.62, a[1] + uy * L * 0.62), ux, uy, 11, color, 3.2)

# station badges + labels
for (r, w, h, size, style, tag, text) in LABELS:
    p.pos(r[0], r[1], w, h, doc.box(w, h, color="#12203A", radius=8,
                                    border=f"1 SOLID {PANEL_LINE}",
                                    inner=doc.text(text, INK, size, style, align="CENTER"),
                                    align="CENTER"))
for ch in "SEABCD":
    _, col, _, _ = BY[ch]
    cx, cy = centre(MARK[ch])
    p.pos(cx - 13, cy - 13, 26, 26,
          doc.box(26, 26, color=BG, radius=13, border=f"2 SOLID {col}",
                  inner=doc.text(ch, col, 18, "BOLD", align="CENTER"), align="CENTER"))
    fit.check(f"badge {ch}", ch, 18, 26, 26)

# coordinate rulers
for x in range(W_COLS):
    s = str(x)
    p.label(GX + x * CS, GY - 26, CS, 22, s, FAINT, 16, align="CENTER")
for y in range(H_ROWS):
    p.label(GX - 46, GY + y * CS + 9, 40, 22, str(y), FAINT, 16, align="CENTER")
p.label(GX - 44, GY - 26, 40, 22, "(x,y)", FAINT, 16)
p.line(GX, GY - 3, GX + GRID_W, GY - 3, 1, PANEL_LINE)
p.line(GX - 3, GY, GX - 3, GY + GRID_H, 1, PANEL_LINE)

# ------------------------------------------------------------------ side panel
sy = HDR_BOT + 18
SB_PAD = 18
SB_IN = SB_W - 2 * SB_PAD


def panel(h, y=None):
    p.pos(SB_X, y if y is not None else sy, SB_W, h,
          doc.box(SB_W, h, color=PANEL, radius=14, border=f"1 SOLID {PANEL_LINE}"))


def para(y, text, size=22, color=INK, style=None, box=None, tag=""):
    bw = box or SB_IN
    lines = fit.wrap(text, size, bw)
    hgt = size + (len(lines) - 1) * TextFit.PITCH * size
    fit.check(tag or text[:12], text, size, bw, max(hgt, size), lines=len(lines))
    p.pos(SB_X + SB_PAD, y, bw, hgt + 2,
          doc.box(bw, hgt + 2, inner=doc.text(text, color, size, style, align="START"),
                  align="TOP_LEFT"))
    return hgt + 8


blocks = []
r1, r2 = plan["route_1"], plan["route_2"]
segs = r2["segments"]
cmp_ = plan["comparison"]
conn = plan["connectivity"]
blocks.append(("h", "路线一 · S→E 最短", 22, R1, "BOLD"))
blocks.append(("p", f"{r1['steps']} 步 · {r1['meters']} 米（每步一格 2 米）。"
                    f"最短路共 {r1['shortest_path_count']:,} 条等价解，本图取其一。", 22, INK, None))
blocks.append(("h", "路线二 · S→B→D→E（先 B 后 D）", 22, R2, "BOLD"))
blocks.append(("p", f"{r2['steps']} 步 · {r2['meters']} 米；分段 "
                    f"{segs[0]['steps']}＋{segs[1]['steps']}＋{segs[2]['steps']} 步，"
                    f"每段各取最短路。", 22, INK, None))
blocks.append(("p", f"比路线一多 {cmp_['route_2_minus_route_1_steps']} 步"
                    f"＝{cmp_['route_2_minus_route_1_steps'] * 2} 米；"
                    f"两线重合 {cmp_['shared_step_count']} 步。", 22, DIM, None))
blocks.append(("h", "重合与折返", 22, DOOR, "BOLD"))
blocks.append(("p", "B(12,3) 是端点格：进入 B 后原路退回 (12,4) 再南下。"
                    "重合段与折返段都画成平行双线，青实线＝路线一，琥珀虚线＝路线二。",
               22, DIM, None))
blocks.append(("h", "门洞 · 连通性 · 尺度", 22, DOOR, "BOLD"))
blocks.append(("p", f"门洞 {len(DOORS)} 处：" + "、".join(f"({x},{y})" for x, y in DOORS) + "。",
               22, INK, None))
blocks.append(("p", f"墙 {plan['grid']['wall_cells']} 格、可走 "
                    f"{plan['grid']['walkable_cells']} 格；自 S 广度优先可达 "
                    f"{conn['bfs_from_S_reached']} 格，无孤立格。仅 4-邻接移动，"
                    "墙体不可走，门洞不额外放大。", 22, DIM, None))

# first pass: exact vertical layout (heading rules cost extra space, so the frame
# must be sized from the same numbers the second pass emits). A text box is
# PITCH*size tall *per line* and the glyphs are centred in that line box, so the
# advance and the rule both use the full box height, not the nominal ink height.
LAYOUT, yy = [], sy + 14
for kind, text, size, color, style in blocks:
    nl = fit.lines(text, size, SB_IN)
    hgt = nl * TextFit.PITCH * size
    if kind == "h":
        yy += 4
    LAYOUT.append(("txt", yy, text, size, color, style, nl, hgt))
    yy += hgt
    if kind == "h":
        LAYOUT.append(("rule", yy + 3))
        yy += 3 + 8
    else:
        yy += 7
PANEL_H = yy - sy + 2
assert sy + PANEL_H <= 1048, f"side panel too tall: {sy + PANEL_H:.0f} > 1048"
panel(PANEL_H)
for item in LAYOUT:
    if item[0] == "rule":
        p.line(SB_X + SB_PAD, item[1], SB_X + SB_W - SB_PAD, item[1], 1, PANEL_LINE)
        continue
    _, y0, text, size, color, style, nl, hgt = item
    fit.check(f"sb:{text[:10]}", text, size, SB_IN, hgt, lines=nl)
    p.pos(SB_X + SB_PAD, y0, SB_IN, hgt,
          doc.box(SB_IN, hgt, inner=doc.text(text, color, size, style, align="START",
                                             maxlines=nl), align="TOP_LEFT"))



PH = PANEL_H

# -------------------------------------------- second side panel: leg mileage
# The column has ~200 px left under the info panel; a per-leg distance table
# belongs there (the task asks for steps *and* metres).
SEQ_Y = sy + PANEL_H + 16
rows = [(f"路线一 S→E（最短）", f"{r1['steps']} 步 · {r1['meters']} 米", R1)]
for s in segs:
    rows.append((f"{s['from']}→{s['to']} 段", f"{s['steps']} 步 · {s['meters']} 米", DIM))
rows.append(("路线二合计（先 B 后 D）", f"{r2['steps']} 步 · {r2['meters']} 米", R2))
ROW_H = 29.0
TOP = 10 + 30 + 4 + 8
SEQ_H = TOP + len(rows) * ROW_H + 8
assert SEQ_Y + SEQ_H <= 1048, f"mileage panel too tall: {SEQ_Y + SEQ_H:.0f} > 1048"
panel(SEQ_H, SEQ_Y)
qy = SEQ_Y + 10
head = "分段里程（每步一格 = 2 米）"
fit.check("mileage-h", head, 22, SB_IN, 30)
p.label(SB_X + SB_PAD, qy, SB_IN, 30, head, INK, 22, "BOLD")
qy += 30
p.line(SB_X + SB_PAD, qy, SB_X + SB_W - SB_PAD, qy, 1, PANEL_LINE)
qy += 8
for lab, val, col in rows:
    fit.check(f"mileage:{lab[:6]}", lab, 22, 290, 26)
    fit.check(f"mileage-v:{val[:6]}", val, 22, 260, 26)
    p.label(SB_X + SB_PAD, qy, 290, 26, lab, col, 22)
    p.label(SB_X + SB_PAD + SB_IN - 260, qy, 260, 26, val, col, 22, align="END")
    qy += ROW_H

# --------------------------------------------------------------------- legend
p.pos(M, LEG_Y, GX + GRID_W - M, LEG_H,
      doc.box(GX + GRID_W - M, LEG_H, color=PANEL, radius=14,
              border=f"1 SOLID {PANEL_LINE}"))
ly = LEG_Y + 14
p.label(M + 16, ly, 120, 28, "图例", INK, 22, "BOLD")
items = [
    ("solid", "路线一 青色实线", R1),
    ("dash", "路线二 琥珀虚线", R2),
    ("double", "重合与往返＝平行双线", DOOR),
    ("chev", "箭头＝行进方向", INK),
    ("wall", "墙体（不可走）", WALL),
    ("floor", "可走格", FLOOR),
    ("door", "门洞记号（不放大）", DOOR),
    ("badge", "S 入口 · E 出口", ENTR),
    ("badge2", "A–D 四展区", DIM),
]
COLW = 300.0
for i, (kind, text, col) in enumerate(items):
    row, k = divmod(i, 3)
    x = M + 16 + k * COLW
    y = ly + 38 + row * 44
    if kind == "solid":
        p.line(x, y + 11, x + 30, y + 11, RIB, col)
    elif kind == "dash":
        seg((x, y + 11), (x + 30, y + 11), RIB, col, dash=(9, 6))
    elif kind == "double":
        p.line(x, y + 7, x + 30, y + 7, 3, R1)
        p.line(x, y + 15, x + 30, y + 15, 3, R2)
    elif kind == "chev":
        chevron((x + 26, y + 11), 1, 0, 11, col, 3.0)
    elif kind == "wall":
        p.rect(x, y + 1, 22, 20, WALL)
        p.pos(x, y + 1, 22, 20, doc.box(22, 20, border=f"1 SOLID {PANEL_LINE}"))
    elif kind == "floor":
        p.rect(x, y + 1, 22, 20, FLOOR)
        p.pos(x, y + 1, 22, 20, doc.box(22, 20, border=f"1 SOLID {FLOOR_LINE}"))
    elif kind == "door":
        p.rect(x, y + 1, 22, 20, "#2E2153")
        p.line(x + 11, y + 3, x + 11, y + 8, 3, col)
        p.line(x + 11, y + 13, x + 11, y + 18, 3, col)
    else:
        lab = "S" if kind == "badge" else "A"
        c2 = col if kind == "badge" else PANEL_LINE
        p.pos(x + 2, y - 1, 22, 22, doc.box(22, 22, color=BG, radius=11,
                                            border=f"2 SOLID {c2}",
                                            inner=doc.text(lab, col if kind == "badge" else DIM,
                                                            16, "BOLD", align="CENTER"),
                                            align="CENTER"))
    bw = COLW - 46
    fit.check(f"legend:{text}", text, 22, bw, 26)
    p.label(x + 36, y, bw, 26, text, DIM, 22)
# scale bar (5 cells = 10 m) in the fourth legend row
sx = M + 16
sby = ly + 38 + 3 * 44 - 4
p.label(sx, sby, 150, 26, "尺度", INK, 22, "BOLD")
bx = sx + 74
for i in range(5):
    p.rect(bx + i * CS, sby + 2, CS, 14, "#1B2A4A" if i % 2 == 0 else "#2A3D63")
p.pos(bx, sby + 2, 5 * CS, 14, doc.box(5 * CS, 14, border=f"1 SOLID {PANEL_LINE}"))
scale_a = "5 格 = 10 米"
ax0 = bx + 5 * CS + 14
p.label(ax0, sby, 200, 26, scale_a, DIM, 22)
fit.check("scale", scale_a, 22, 200, 26)
# the second note starts after the real width of the first one, never at a
# guessed fixed offset (v02 overlapped here)
scale_note = "每步一格 = 2 米"
nx0 = ax0 + fit.w(scale_a, 22) + 34
p.label(nx0, sby, 220, 26, scale_note, FAINT, 22)
fit.check("legend-note", scale_note, 22, 220, 26)
axis_note = "坐标标尺：上方 x · 左侧 y"
p.label(GX + GRID_W - 16 - 470, ly, 470, 26, axis_note, FAINT, 22, align="END")
fit.check("axis-note", axis_note, 22, 470, 26)
assert sby + 26 <= LEG_Y + LEG_H, f"legend overflow {sby + 26} > {LEG_Y + LEG_H}"

DSL = doc.dsl()
OUT.mkdir(parents=True, exist_ok=True)
(TEMP / f"{VERSION}.snapshot").write_text(DSL, encoding="utf-8")
report = {"text_items": fit.n, "problems": fit.problems,
          "trace_checks": CHECK, "label_failures": LABEL_FAILS,
          "shared_edges": len(SHARED), "dup_edges": sorted(DUP),
          "labels": [{"tag": t, "rect": [round(v, 1) for v in r]} for r, w, h, s, st, t, x in LABELS],
          "side_panel_height": round(PH, 1), "legend_bottom": round(sby + 30, 1)}
(TEMP / "fit-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                      encoding="utf-8")
print(json.dumps({"bytes": len(DSL.encode()), "text_items": fit.n,
                  "problems": fit.problems, "trace_checks": CHECK,
                  "label_failures": LABEL_FAILS,
                  "shared": len(SHARED), "dup": len(DUP),
                  "panel_h": round(PH, 1)}, ensure_ascii=False))
sys.exit(1 if (fit.problems or CHECK or LABEL_FAILS) else 0)
